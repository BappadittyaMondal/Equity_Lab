// Adds concise, idempotent retrieval labels to every canonical source document.
import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "Not_Required_Upload", "Canonical_Source_84");
const marker = "<!-- IERL-CANONICAL-METADATA v1.2 -->";

async function files(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  return (await Promise.all(entries.map((entry) => entry.isDirectory() ? files(path.join(dir, entry.name)) : [path.join(dir, entry.name)]))).flat();
}
function title(file) {
  return path.basename(file, ".md").replace(/_v_0_0/g, "").replace(/^Domain_\d+_/i, "").replaceAll("_", " ");
}
function metadata(file) {
  const relative = path.relative(root, file).replaceAll("\\", "/");
  const skills = relative.startsWith("AI_SKILL_IRA_col_final/");
  const knowledge = relative.startsWith("Knowledge_IRA_COL_FINAL/");
  const index = path.basename(file) === "00_Index.md";
  const role = skills ? "Executable workflow skill" : index ? "Knowledge-library routing index" : knowledge ? "Static knowledge domain" : "Operating-system governance or contract";
  const use = skills ? "Use when the request matches this skill's method, then execute its stated gates and output format." : index ? "Use first to identify the narrowest relevant knowledge domain and cross-check requirements." : knowledge ? "Use for conceptual, sector, or analytical context; validate time-sensitive claims with current evidence." : "Use to govern task routing, contracts, evidence handling, confidence, or output quality.";
  const handoff = skills ? "Handoff: Project Instructions → Confidence Standard → Quality Audit → relevant knowledge domains." : knowledge ? "Handoff: Project Instructions → applicable workflow skill → current primary evidence → risk/forensic review." : "Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.";
  const skillOutput = skills ? "\n> **Minimum skill output:** objective/horizon and as-of date · inputs and gaps · completed gates · conclusion and counter-case · material risks/invalidation · confidence and next verification step.  \n" : "";
  const sectorOverlay = /Domain_3[1-9]_.*DeepDive|Sector_Quick_Reference/.test(path.basename(file)) ? "\n> **Sector risk overlay:** use sector-specific metrics plus cycle, regulatory/policy, balance-sheet, and governance/forensic checks; do not generalise from a single sector datapoint.  \n" : "";
  const cognition = skills ? "Gate-based diagnostic execution: test the thesis, its counter-case, and its invalidation before a conclusion." : knowledge ? "Contextual synthesis: use the framework to form questions, then test it against current evidence and a credible alternative explanation." : "Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.";
  return `${marker}\n> **Canonical retrieval label:** ${title(file)}  \n> **Role:** ${role}  \n> **Use when:** ${use}  \n> **Cognitive mode:** ${cognition}  \n> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  \n> **${handoff}**${skillOutput}${sectorOverlay}\n\n`;
}

const addenda = {
  "AI_Reasoning_Skills_v_0_0.md": `\n\n<!-- IERL-HIGH-RELIABILITY v1.0 -->\n## High-Reliability Reasoning Addendum\n\nFor every material conclusion, create a compact **hypothesis ledger** before deciding: (1) decision and horizon, (2) base case, (3) strongest alternative/counter-case, (4) evidence for and against each, (5) key assumption, (6) falsifier, and (7) confidence impact. Do not let the amount of supporting prose substitute for comparison with the strongest credible alternative.\n\nUse this sequence: frame → identify base rates and causal drivers → collect dated evidence → test alternative explanations → separate correlation from causal claim → identify disconfirming evidence → apply risk gates → state a conditional conclusion. When evidence is mixed, report what would resolve the disagreement instead of forcing a winner.\n`,
  "AI_Research_Engine_v_0_0.md": `\n\n<!-- IERL-HIGH-RELIABILITY v1.0 -->\n## High-Reliability Research Addendum\n\nMaintain an **evidence ledger** for material research: claim, source, source tier, as-of date, period covered, direct support/contradiction, and known limitation. Re-check live-sensitive evidence before use; stale data must be labelled rather than silently blended with current evidence.\n\nA conclusion with a material contradiction is incomplete until the contradiction is explained, bounded, or escalated. Prefer a smaller set of traceable primary facts to a larger set of unverified summaries. Search effort should target the uncertainty most likely to change the decision, not merely add confirming detail.\n`,
  "AI_Quality_Audit_v_0_0.md": `\n\n<!-- IERL-HIGH-RELIABILITY v1.0 -->\n## High-Reliability Decision Gate Addendum\n\nBefore approving a material output, test five failure modes: unsupported material claim; stale or mismatched period; missing counter-case; unresolved hard risk/red flag; and confidence higher than evidence quality. Any failed critical test requires revision, disclosure, or a no-decision result.\n\nAudit the decision path, not only the prose: another analyst should be able to identify the inputs, reproduce the calculation, see the rejected alternative, and know what future fact would invalidate the conclusion.\n`,
  "AI_Task_Orchestrator_v_0_0.md": `\n\n<!-- IERL-HIGH-RELIABILITY v1.0 -->\n## High-Reliability Task Framing Addendum\n\nAt task start, explicitly classify: decision type, horizon, entity/universe, required freshness, user constraints, and consequence of being wrong. Route to the narrowest sufficient workflow; do not invoke every available source by default.\n\nIf a missing input can materially reverse the result, ask for it or continue only with a labelled assumption and reduced confidence. Split compound requests into evidence collection, analysis, risk review, and output stages so an early narrative cannot anchor later reasoning.\n`,
  "AI_Output_System_v_0_0.md": `\n\n<!-- IERL-HIGH-RELIABILITY v1.0 -->\n## High-Reliability Decision Card Addendum\n\nUse this compact decision card for substantive research: **Question & horizon; As-of date; Bottom line; Supporting evidence; Counter-case; Risks/red flags; Assumptions/data gaps; Invalidation or next check; Confidence.** This structure is mandatory when an output contains a recommendation, ranking, forecast, valuation, or trading setup.\n\nDo not hide uncertainty in a disclaimer. Put the uncertainty next to the conclusion and state whether it changes the action, sizing, timing, or decision status.\n`,
};

let changed = 0;
for (const file of (await files(root)).filter((file) => file.endsWith(".md"))) {
  const content = await readFile(file, "utf8");
  const withoutOldMetadata = content.replace(/^(?:<!-- IERL-CANONICAL-METADATA v[\d.]+ -->\r?\n(?:>.*\r?\n)*(?:\r?\n)*)+/, "");
  const addendum = addenda[path.basename(file)] ?? "";
  const withoutOldAddendum = withoutOldMetadata.replace(/(?:\r?\n)*<!-- IERL-HIGH-RELIABILITY v1\.0 -->[\s\S]*$/, "");
  const upgraded = metadata(file) + withoutOldAddendum + addendum;
  if (upgraded !== content) {
    await writeFile(file, upgraded, "utf8");
    changed++;
  }
}
console.log(`Canonical retrieval labels added: ${changed}`);
