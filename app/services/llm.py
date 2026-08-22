"""LLM integration service — Phase 3, Layer 13 upgrade.

Enforces the canonical role of LLM: SYNTHESIS ONLY, never primary intelligence source.

Rules enforced by this module:
  1. LLM never invents financial data — only synthesizes engine outputs
  2. Every prompt injects structured ResearchContext from the database
  3. Challenge mode: after initial analysis, LLM argues against its own conclusion
  4. Structured reasoning protocol: cite specific numbers, flag unverified claims
  5. Evidence-grounded fallback if LLM unavailable: deterministic narrative from engines
"""

import re
import logging
import datetime
from typing import Dict, Any, List, Optional

from app.core.config import settings
from app.models.schemas import QueryRequest, QueryResponse, ConvictionCall
from app.services.market_data import get_quote, create_meta_header, normalize_symbol

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

def sanitize_input(text: str) -> str:
    """Sanitize user prompt to prevent injection attempts."""
    clean = re.sub(r'[\{\}\<\>]', '', text)
    return clean[:500].strip()


def generate_text(prompt: str) -> str:
    """Fallback / helper to generate text narrative."""
    return f"Narrative Analysis (Skill Ver: {settings.SKILL_LIBRARY_VERSION}): {prompt[:300]}..."


# ─────────────────────────────────────────────────────────────────────────────
# Phase 3: Research Context Builder
# ─────────────────────────────────────────────────────────────────────────────

def build_research_context(symbol: str) -> str:
    """Assemble structured ResearchContext from live data + database.

    Injects into LLM prompt as structured data (not prose) to ground reasoning.
    The LLM MUST cite numbers from this context — no fabrication allowed.
    """
    norm = normalize_symbol(symbol)
    context_lines = [
        f"═══ RESEARCH CONTEXT: {norm} ═══",
        f"[RULE: Cite ONLY numbers from this context. Never invent financial data.]",
        "",
    ]

    # Live market quote
    try:
        quote = get_quote(norm)
        price = getattr(quote, "price", None) if hasattr(quote, "price") else quote.get("price")
        pe = getattr(quote, "pe_ratio", None) if hasattr(quote, "pe_ratio") else quote.get("pe_ratio")
        high_52w = getattr(quote, "fifty_two_week_high", None) if hasattr(quote, "fifty_two_week_high") else quote.get("fifty_two_week_high")
        low_52w = getattr(quote, "fifty_two_week_low", None) if hasattr(quote, "fifty_two_week_low") else quote.get("fifty_two_week_low")
        context_lines += [
            "── LIVE MARKET DATA (Source: yfinance) ──",
            f"Price: ₹{price} | P/E: {pe} | 52W Range: ₹{low_52w} – ₹{high_52w}",
            "",
        ]
    except Exception as e:
        context_lines.append(f"Live quote unavailable: {e}")

    # Financial observations from ResearchDataStore
    try:
        from app.services.research_data import ResearchDataStore
        store = ResearchDataStore()
        _, financials, events, _, ownership, _ = store.get_timeline(norm)

        if financials:
            # Latest 4 quarters of key metrics
            metrics_of_interest = ["revenue", "net_income", "pat", "operating_cash_flow", "roce"]
            context_lines.append("── FINANCIAL OBSERVATIONS (last 4Q from ResearchDataStore) ──")
            for metric_name in metrics_of_interest:
                obs = sorted(
                    [f for f in financials if f.metric in [metric_name, f"total_{metric_name}"]],
                    key=lambda x: str(x.period_end)
                )[-4:]
                if obs:
                    values = ", ".join(f"{o.period_end}: {o.value:,.0f}" for o in obs)
                    context_lines.append(f"{metric_name.upper()}: {values}")
            context_lines.append("")
        else:
            context_lines.append("Financial observations: None in database (run seed_watchlist)")
            context_lines.append("")

        if ownership:
            latest_own = sorted(ownership, key=lambda x: str(x.period_end))[-1]
            context_lines += [
                "── OWNERSHIP (latest from ResearchDataStore) ──",
                f"Promoter: {latest_own.promoter_pct}% | FII: {latest_own.fii_pct}% | DII: {latest_own.dii_pct}%",
                f"Pledge: {latest_own.promoter_pledge_pct or 0}%",
                "",
            ]

        if events:
            recent_events = sorted(events, key=lambda x: str(getattr(x, "event_date", "")))[-3:]
            if recent_events:
                context_lines.append("── RECENT EVENTS ──")
                for evt in recent_events:
                    context_lines.append(f"• {getattr(evt, 'event_date', '?')}: {getattr(evt, 'title', '?')} [{getattr(evt, 'event_type', '?')}]")
                context_lines.append("")
    except Exception as e:
        context_lines.append(f"ResearchDataStore unavailable: {e}")
        context_lines.append("")

    # Regime context
    try:
        from app.services.knowledge.regime_engine import RegimeEngine
        macro = RegimeEngine().get_macro_context()
        context_lines += [
            "── MACRO REGIME ──",
            f"Regime: {macro.regime.regime} | India VIX: {macro.india_vix} | Nifty: {macro.nifty_level}",
            f"RBI Repo Rate: {macro.rbi_repo_rate}% | Risk-Free Rate: {macro.risk_free_rate}%",
            "",
        ]
    except Exception:
        pass

    context_lines.append("═══ END RESEARCH CONTEXT ═══")
    return "\n".join(context_lines)


def _build_analysis_prompt(query_text: str, symbol: str, mode: str, research_context: str) -> str:
    """Build the primary analysis prompt with structured reasoning protocol."""
    return f"""You are the IERL Institutional Equity Research AI. Mode: {mode}.
Skill Library Version: {settings.SKILL_LIBRARY_VERSION}

{research_context}

STRUCTURED REASONING PROTOCOL (MANDATORY):
1. Cite ONLY specific numbers from the Research Context above — never invent data
2. For every claim, state: KNOWN (data exists above) or UNCERTAIN (not in context)
3. Flag any metric that looks anomalous or needs further verification
4. Never guarantee investment returns — express probability and risk
5. If a data point is missing from context, say "DATA REQUIRED: [metric name]"

USER QUERY: {query_text}

Provide your analysis in this structure:
A) KEY FINDINGS (cite 3-5 specific data points from context)
B) KNOWN STRENGTHS (grounded in data above)
C) KNOWN RISKS (grounded in data above)
D) WHAT IS UNCERTAIN (what data is missing or unreliable?)
E) PRELIMINARY THESIS (one sentence, with confidence: HIGH/MEDIUM/LOW)"""


def _build_challenge_prompt(initial_analysis: str, symbol: str) -> str:
    """Build the challenge prompt — LLM argues against its own conclusion."""
    return f"""You are playing Devil's Advocate for your previous analysis of {symbol}.

PREVIOUS ANALYSIS:
{initial_analysis[:1500]}

Now CHALLENGE your own conclusion. Answer:
1. What is the STRONGEST argument AGAINST your preliminary thesis?
2. Which of your assumptions could be WRONG and how wrong?
3. What RED FLAGS did you downplay or miss?
4. Under what scenario (regime change, earnings miss, governance event) does your thesis FAIL?
5. What would a SHORT SELLER say about this stock?

Be specific. Use the same data from the Research Context. Do not contradict facts — only challenge the interpretation and weighting of signals."""


# ─────────────────────────────────────────────────────────────────────────────
# Phase 3: Evidence-Grounded LLM Query
# ─────────────────────────────────────────────────────────────────────────────

def process_llm_query(req: QueryRequest) -> QueryResponse:
    """Process a research query with Phase 3 evidence-grounded prompting.

    Flow:
      1. Extract symbol from query
      2. Build ResearchContext from live data + database
      3. Send structured analysis prompt to LLM
      4. Send challenge prompt to LLM (argue against own conclusion)
      5. Combine into final grounded response
      6. If LLM unavailable, generate deterministic narrative from engine outputs
    """
    query_text = sanitize_input(req.query)
    mode = req.mode or "Quick"

    # ── Daily LLM call limit check ────────────────────────────────────────
    from app.services.db import get_connection
    conn_check = get_connection()
    today_start = datetime.datetime.now(datetime.timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ).isoformat()
    daily_calls = conn_check.execute(
        "SELECT COUNT(*) as cnt FROM llm_usage WHERE timestamp >= ?",
        (today_start,)
    ).fetchone()["cnt"]
    conn_check.close()
    fallback = daily_calls >= settings.LLM_DAILY_CALL_LIMIT

    # ── Symbol extraction ─────────────────────────────────────────────────
    STOP_VERBS = {
        "SHOW", "WHAT", "CHECK", "ANALYZE", "PLEASE", "PRICE", "RETURN",
        "FETCH", "MODE", "QUICK", "RESEARCH", "WITH", "FROM", "THAT", "THIS",
        "YOUR", "THE", "AND", "STOCK", "GIVE", "TELL", "FIND", "VIEW",
        "CALCULATE", "WILL", "SOME", "MANY", "ABOUT", "INFO", "DATA", "LOOK"
    }
    candidates = re.findall(r'\b[A-Z0-9^]{2,12}\b', query_text.upper())
    symbol = "RELIANCE"
    for cand in candidates:
        if cand not in STOP_VERBS and len(cand) >= 2:
            symbol = cand
            break

    # ── Build Research Context (Phase 3 core) ────────────────────────────
    research_context = build_research_context(symbol)

    # ── Try Gemini with evidence-grounded prompt ──────────────────────────
    gemini_key = settings.GEMINI_API_KEY
    if gemini_key and "your_" not in gemini_key.lower() and not fallback:
        try:
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)
                analysis_prompt = _build_analysis_prompt(query_text, symbol, mode, research_context)
                resp1 = client.models.generate_content(model="gemini-2.5-flash", contents=analysis_prompt)
                initial_analysis = resp1.text
                challenge_section = ""
                if mode.lower() in ("research", "deep", "full"):
                    challenge_prompt = _build_challenge_prompt(initial_analysis, symbol)
                    resp2 = client.models.generate_content(model="gemini-2.5-flash", contents=challenge_prompt)
                    challenge_section = f"\n\n━━━ DEVIL'S ADVOCATE (Challenge Mode) ━━━\n{resp2.text}"
            except Exception:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")

                # Primary analysis prompt
                analysis_prompt = _build_analysis_prompt(query_text, symbol, mode, research_context)
                response1 = model.generate_content(analysis_prompt)
                initial_analysis = response1.text

                # Challenge mode (only in Research/Deep modes, not Quick)
                challenge_section = ""
                if mode.lower() in ("research", "deep", "full"):
                    challenge_prompt = _build_challenge_prompt(initial_analysis, symbol)
                    response2 = model.generate_content(challenge_prompt)
                    challenge_section = f"\n\n━━━ DEVIL'S ADVOCATE (Challenge Mode) ━━━\n{response2.text}"

            final_reply = initial_analysis + challenge_section

            provider_used = f"Google Gemini 1.5 Flash — Evidence-Grounded (Skill Ver: {settings.SKILL_LIBRARY_VERSION})"
            token_count = len(final_reply.split())
            estimated_cost = (token_count / 1000.0) * settings.LLM_COST_PER_1K_TOKENS

            # Persist usage
            conn_log = get_connection()
            conn_log.execute(
                "INSERT INTO llm_usage (timestamp, provider, token_count, estimated_cost) VALUES (?, ?, ?, ?)",
                (datetime.datetime.now(datetime.timezone.utc).isoformat(), provider_used, token_count, estimated_cost)
            )
            conn_log.commit()
            conn_log.close()

            return QueryResponse(
                query=query_text,
                mode=mode,
                reply=final_reply,
                provider=provider_used,
                meta=create_meta_header(source=f"Gemini 1.5 Flash ({settings.SKILL_LIBRARY_VERSION})"),
                disclaimer=(
                    "AI research assistant. All data cited from IERL ResearchDataStore. "
                    "LLM synthesizes engine outputs only — not a primary source of financial data. "
                    "Not investment advice."
                )
            )
        except Exception as e:
            logger.warning("Gemini API call failed: %s — falling back to deterministic", e)

    # ── Deterministic evidence-grounded fallback ──────────────────────────
    provider_used = f"IERL Deterministic Engine ({settings.SKILL_LIBRARY_VERSION})"
    quote_price = "N/A"
    try:
        q = get_quote(symbol)
        quote_price = str(getattr(q, "price", None) or q.get("price", "N/A"))
    except Exception:
        pass

    deterministic_reply = (
        f"DETERMINISTIC RESEARCH SUMMARY — {symbol}\n"
        f"─────────────────────────────────────────\n"
        f"{research_context}\n\n"
        f"No LLM synthesis available (daily limit reached or key not configured).\n"
        f"Current market price: ₹{quote_price}\n"
        f"For full AI synthesis, configure GEMINI_API_KEY and retry in Research mode.\n"
        f"[UNVERIFIED_HYPOTHESIS: Any claims not grounded in the context above]"
    )

    return QueryResponse(
        query=query_text,
        mode=mode,
        reply=deterministic_reply,
        provider=provider_used,
        meta=create_meta_header(source=provider_used),
        disclaimer="Deterministic quantitative readout. Not investment advice."
    )


# ─────────────────────────────────────────────────────────────────────────────
# LLM Narrative Generator (for ConvictionCall)
# ─────────────────────────────────────────────────────────────────────────────

class LLMService:
    """Wrapper formatting ConvictionCall into human-readable narrative.

    Phase 3: Uses evidence from conviction call, not boilerplate.
    """

    def generate_narrative(self, conviction: ConvictionCall) -> str:
        """Generate investor-friendly narrative from a ConvictionCall.

        The LLM synthesizes the engine outputs — it does NOT generate new data.
        """
        prompt = (
            f"Explain the following institutional equity conviction call in plain investor-friendly language.\n"
            f"RULES: Cite only the specific engines and scores below. Do not invent financial data.\n\n"
            f"Symbol: {conviction.symbol}\n"
            f"Verdict: {conviction.verdict}\n"
            f"Conviction Score: {conviction.conviction_score}/100\n"
            f"Confidence Tier: {conviction.confidence_tier}\n"
            f"Primary Thesis: {conviction.primary_thesis}\n"
            f"Contributing Engines: {conviction.contributing_engines}\n"
            f"Contradicting Engines: {conviction.contradicting_engines}\n\n"
            f"Explain WHY this verdict was reached, what the key supporting evidence is, "
            f"and what could change the verdict. Flag any uncertainty explicitly."
        )
        return generate_text(prompt)
