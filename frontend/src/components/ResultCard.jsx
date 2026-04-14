import { useEffect, useId } from "react";

function formatPercent(value) {
  return `${(value * 100).toFixed(2)}%`;
}

function GaugeChart({ probability }) {
  const safeProbability = Number.isFinite(probability) ? Math.max(0, Math.min(1, probability)) : 0;
  const gaugeId = useId().replace(/:/g, "_");

  useEffect(() => {
    const plotly = window.Plotly;
    const gaugeNode = document.getElementById(gaugeId);
    if (!plotly || !gaugeNode) {
      return;
    }

    const safePct = Math.max(0, Math.min(100, safeProbability * 100));

    plotly.newPlot(
      gaugeNode,
      [
        {
          type: "indicator",
          mode: "gauge+number",
          value: safePct,
          title: {
            text: "Churn Risk (%)",
            font: { size: 22, color: "#eef4ff", family: "Inter, Segoe UI, sans-serif" }
          },
          number: {
            font: { size: 70, color: "#38bdf8", family: "Inter, Segoe UI, sans-serif" },
            valueformat: ".0f"
          },
          gauge: {
            shape: "angular",
            axis: {
              range: [0, 100],
              tickmode: "array",
              tickvals: [20, 40, 60, 80],
              ticktext: ["20", "40", "60", "80"],
              tickcolor: "#cbd5e1",
              tickwidth: 2,
              ticklen: 12,
              tickfont: { color: "#eef4ff", size: 16, family: "Inter, Segoe UI, sans-serif" }
            },
            bar: {
              color: "#1ea7ff",
              thickness: 0.22
            },
            bgcolor: "#1b2e4f",
            borderwidth: 0,
            steps: [
              { range: [0, 30], color: "#22c55e" },
              { range: [30, 70], color: "#facc15" },
              { range: [70, 100], color: "#ef4444" }
            ]
          }
        }
      ],
      {
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        margin: { t: 55, r: 20, b: 10, l: 20 },
        height: 330,
        font: { color: "#eef4ff", family: "Inter, Segoe UI, sans-serif" }
      },
      {
        displayModeBar: false,
        responsive: true,
        staticPlot: true
      }
    );
  }, [gaugeId, safeProbability]);

  return (
    <div className="risk-gauge">
      <div id={gaugeId} className="plotly-gauge" aria-label="Churn risk gauge" />
    </div>
  );
}

export default function ResultCard({ result, title, stale = false }) {
  if (!result) {
    return null;
  }

  return (
    <section>
      <h4>Model Decision</h4>
      <h3>{title}</h3>
      {stale ? <div className="stale-hint">Inputs changed. Previous result is outdated. Run prediction again.</div> : null}

      <div className={`result-shell${stale ? " result-shell--stale" : ""}`}>
        <div className="result-card gauge-card">
          <GaugeChart probability={result.probability} />
        </div>

        <div className="result-card summary-card result-copy">
          <div className="score-text">{formatPercent(result.probability)}</div>
          <div className={`badge badge--${result.risk_level.toLowerCase()}`}>{result.risk_level} RISK</div>

          <div className={`status-banner ${result.prediction === 1 ? "danger" : "safe"}`}>
            {result.prediction === 1 ? "Customer is likely to churn." : "Customer is likely to stay."}
          </div>

          <div className="insight-box">
            <h3>Recommended Action</h3>
            <p>{result.insight.recommended_action}</p>
          </div>

          <div className="insight-box driver-box">
            <h3>Top Risk Drivers</h3>
            <p>Strongest factors currently pushing churn risk up:</p>
            <ul className="driver-list">
              {result.top_risk_drivers.map((driver) => (
                <li key={driver.label}>
                  <span className="driver-name">{driver.label}</span>
                  <span className="driver-score">{Math.round(driver.score * 100)}%</span>
                  <div className="driver-reason">{driver.reason}</div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
