/**
 * Institutional Technical Intelligence Dashboard Panel.
 * Visualizes Technical State Score (TSS 0-100), Market Regime, Setup Taxonomy,
 * Calibrated Probability Ladders, Surveillance Gates, and In-Position Trade Management.
 */

window.TechnicalPanel = {
    render: function(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="technical-dashboard-container" style="padding: 20px; background: #0f172a; color: #f8fafc; font-family: Inter, sans-serif;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 12px; margin-bottom: 20px;">
                    <div>
                        <h2 style="margin: 0; color: #fbbf24; font-size: 1.5rem; display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 1.8rem;">📈</span> Technical Probability & Market-Structure Engine
                        </h2>
                        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.9rem;">
                            26-Layer Multi-Timeframe Intelligence & Setup Probability Calibration (§1-122)
                        </p>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <button id="tech-refresh-btn" style="background: #1e293b; color: #fbbf24; border: 1px solid #fbbf24; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600;">
                            ⚡ Run Tier 0-2 Scan
                        </button>
                    </div>
                </div>

                <!-- Screener & Selection Controls -->
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div style="background: #1e293b; border-radius: 8px; padding: 16px; border: 1px solid #334155;">
                        <h3 style="margin-top: 0; color: #38bdf8; font-size: 1.1rem; display: flex; justify-content: space-between;">
                            <span>🎯 Tier 2 High-Conviction Technical Candidates</span>
                            <span id="regime-badge" style="font-size: 0.8rem; background: #0284c7; color: white; padding: 2px 8px; border-radius: 12px;">R1 Bull Trend</span>
                        </h3>
                        <div id="tech-screener-table-container" style="max-height: 260px; overflow-y: auto;">
                            <p style="color: #94a3b8; font-style: italic;">Loading candidate scan...</p>
                        </div>
                    </div>

                    <!-- Single Stock Deep Technical State -->
                    <div style="background: #1e293b; border-radius: 8px; padding: 16px; border: 1px solid #334155;">
                        <h3 style="margin-top: 0; color: #38bdf8; font-size: 1.1rem;">🔍 Active Stock Scanner</h3>
                        <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                            <input type="text" id="tech-symbol-input" value="POLYCAB" style="background: #0f172a; border: 1px solid #475569; color: white; padding: 8px; border-radius: 4px; width: 100%; text-transform: uppercase;">
                            <button id="tech-analyze-btn" style="background: #0284c7; color: white; border: none; padding: 8px 14px; border-radius: 4px; cursor: pointer; font-weight: 600;">Inspect</button>
                        </div>
                        <div id="tech-stock-summary">
                            <div style="text-align: center; padding: 20px; color: #94a3b8;">
                                Enter ticker to load 26-layer technical vector & probability ladder.
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Deep Analytics Output Section -->
                <div id="tech-deep-report-container" style="display: none;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                        <!-- Technical State Vector Card -->
                        <div style="background: #1e293b; border-radius: 8px; padding: 16px; border: 1px solid #334155;">
                            <h4 style="margin-top: 0; color: #fbbf24; border-bottom: 1px solid #334155; padding-bottom: 8px;">📊 Technical State Vector</h4>
                            <div id="tech-vector-body" style="font-size: 0.9rem; display: flex; flex-direction: column; gap: 8px;"></div>
                        </div>

                        <!-- Calibrated Probability Ladder Card -->
                        <div style="background: #1e293b; border-radius: 8px; padding: 16px; border: 1px solid #334155;">
                            <h4 style="margin-top: 0; color: #4ade80; border-bottom: 1px solid #334155; padding-bottom: 8px;">🎲 Calibrated Probability Ladder</h4>
                            <div id="tech-prob-body" style="font-size: 0.9rem; display: flex; flex-direction: column; gap: 8px;"></div>
                        </div>

                        <!-- Surveillance & Trade Manager Card -->
                        <div style="background: #1e293b; border-radius: 8px; padding: 16px; border: 1px solid #334155;">
                            <h4 style="margin-top: 0; color: #f43f5e; border-bottom: 1px solid #334155; padding-bottom: 8px;">🛡️ Surveillance & Trade Manager</h4>
                            <div id="tech-surv-body" style="font-size: 0.9rem; display: flex; flex-direction: column; gap: 8px;"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.bindEvents();
        this.loadScreenerData();
    },

    bindEvents: function() {
        const refreshBtn = document.getElementById("tech-refresh-btn");
        if (refreshBtn) {
            refreshBtn.addEventListener("click", () => this.loadScreenerData());
        }

        const analyzeBtn = document.getElementById("tech-analyze-btn");
        if (analyzeBtn) {
            analyzeBtn.addEventListener("click", () => {
                const sym = document.getElementById("tech-symbol-input").value;
                if (sym) this.loadStockReport(sym);
            });
        }
    },

    loadScreenerData: async function() {
        const tableContainer = document.getElementById("tech-screener-table-container");
        if (!tableContainer) return;

        tableContainer.innerHTML = `<p style="color: #94a3b8; font-style: italic;">Running Tier 0-2 Funnel Scan...</p>`;

        try {
            const resp = await fetch("/api/v1/technical/screener");
            const data = await resp.json();

            if (data.market_regime) {
                const badge = document.getElementById("regime-badge");
                if (badge) badge.innerText = `${data.market_regime.regime_code} — ${data.market_regime.market_stress_level} Vol`;
            }

            if (!data.candidates || data.candidates.length === 0) {
                tableContainer.innerHTML = `<p style="color: #f87171;">No candidates passed Tier 2 threshold.</p>`;
                return;
            }

            let html = `
                <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.85rem;">
                    <thead>
                        <tr style="border-bottom: 1px solid #475569; color: #94a3b8;">
                            <th style="padding: 6px;">Symbol</th>
                            <th style="padding: 6px;">TSS Score</th>
                            <th style="padding: 6px;">Setup</th>
                            <th style="padding: 6px;">P(+10%|20d)</th>
                            <th style="padding: 6px;">EV (%)</th>
                            <th style="padding: 6px;">Action</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            data.candidates.forEach(c => {
                html += `
                    <tr style="border-bottom: 1px solid #334155;">
                        <td style="padding: 6px; font-weight: bold; color: #fbbf24;">${c.symbol} ${c.pre_breakout_rs ? '🔥' : ''}</td>
                        <td style="padding: 6px; color: #38bdf8; font-weight: bold;">${c.tss_score}</td>
                        <td style="padding: 6px;"><span style="background: #334155; padding: 2px 6px; border-radius: 4px;">${c.setup_class}</span></td>
                        <td style="padding: 6px; color: #4ade80;">${(c.prob_t2_20d * 100).toFixed(0)}%</td>
                        <td style="padding: 6px; color: #a7f3d0;">+${c.expected_value_pct}%</td>
                        <td style="padding: 6px;">
                            <button onclick="TechnicalPanel.loadStockReport('${c.symbol}')" style="background: #0284c7; color: white; border: none; padding: 2px 8px; border-radius: 4px; cursor: pointer; font-size: 0.75rem;">Inspect</button>
                        </td>
                    </tr>
                `;
            });

            html += `</tbody></table>`;
            tableContainer.innerHTML = html;

            if (data.candidates.length > 0) {
                this.loadStockReport(data.candidates[0].symbol);
            }
        } catch (e) {
            tableContainer.innerHTML = `<p style="color: #f87171;">Failed to load screener: ${e.message}</p>`;
        }
    },

    loadStockReport: async function(symbol) {
        const deepContainer = document.getElementById("tech-deep-report-container");
        const vectorBody = document.getElementById("tech-vector-body");
        const probBody = document.getElementById("tech-prob-body");
        const survBody = document.getElementById("tech-surv-body");

        try {
            const resp = await fetch(`/api/v1/technical/report/${symbol}`);
            const data = await resp.json();

            if (deepContainer) deepContainer.style.display = "block";

            // Render Vector Body
            const v = data.state_vector || {};
            vectorBody.innerHTML = `
                <div><strong>Technical State Score:</strong> <span style="color: #fbbf24; font-size: 1.2rem;">${data.technical_state_score} / 100</span></div>
                <div><strong>Setup Class:</strong> ${v.setup_class}</div>
                <div><strong>RS Rating:</strong> ${v.rs_rating_0_99} / 99</div>
                <div><strong>Trend Efficiency Ratio (ER):</strong> ${v.trend_efficiency_ratio}</div>
                <div><strong>Extension Z-Score:</strong> ${v.extension_z_score} ATRs</div>
                <div><strong>RVOL:</strong> ${v.rvol}x | <strong>UDVR:</strong> ${v.udvr}</div>
                <div><strong>Pre-Breakout RS:</strong> ${v.pre_breakout_rs_leadership ? '✅ YES' : 'NO'}</div>
            `;

            // Render Probability Ladder Body
            const p = data.probability_ladder || {};
            probBody.innerHTML = `
                <div><strong>P(+5% in 10d):</strong> ${(p.event_t1_prob_5pct_10d * 100).toFixed(0)}%</div>
                <div><strong>P(+10% in 20d):</strong> ${(p.event_t2_prob_10pct_20d * 100).toFixed(0)}%</div>
                <div><strong>P(+20% in 60d):</strong> ${(p.event_t3_prob_20pct_60d * 100).toFixed(0)}%</div>
                <div><strong>Expected Value (EV):</strong> <span style="color: #4ade80; font-weight: bold;">+${p.expected_value_pct}%</span></div>
                <div><strong>Risk-Adjusted EV (RAEV):</strong> ${p.risk_adjusted_ev}</div>
                <div><strong>Path MAE / MFE:</strong> ${p.expected_mae_pct}% / +${p.expected_mfe_pct}%</div>
            `;

            // Render Surveillance & Trade Manager Body
            const s = data.surveillance_gate || {};
            const tm = data.trade_management || {};
            survBody.innerHTML = `
                <div><strong>ASM / GSM Status:</strong> ${s.asm_stage} / ${s.gsm_stage}</div>
                <div><strong>Circuit Band:</strong> ${s.circuit_band_pct}% (Risk: ${s.circuit_lock_risk})</div>
                <div><strong>Total Roundtrip Cost:</strong> ${s.total_roundtrip_cost_pct}%</div>
                <div><strong>Breakeven Trigger:</strong> ₹${tm.breakeven_trigger_price} (${tm.breakeven_status})</div>
                <div><strong>Partial Exit (+1.5R):</strong> ₹${tm.partial_target_price}</div>
                <div><strong>Chandelier ATR Stop:</strong> <span style="color: #f43f5e; font-weight: bold;">₹${tm.chandelier_atr_stop_price}</span></div>
                <div><strong>Position Verdict:</strong> <span style="background: #0284c7; padding: 2px 6px; border-radius: 4px; font-weight: bold;">${tm.managed_exit_verdict}</span></div>
            `;
        } catch (e) {
            console.error("Error loading technical report:", e);
        }
    }
};
