import { useEffect, useId } from "react";

function GaugeChart({ probability }) {
  const safeProbability = Number.isFinite(probability) ? Math.max(0, Math.min(1, probability)) : 0;
  const safePct = Math.max(0, Math.min(100, safeProbability * 100));
  const gaugeId = useId().replace(/:/g, "_");

  useEffect(() => {
    const plotly = window.Plotly;
    const gaugeNode = document.getElementById(gaugeId);
    if (!plotly || !gaugeNode) {
      return;
    }

    plotly.newPlot(
      gaugeNode,
      [
        {
          type: "indicator",
          mode: "gauge",
          value: safePct,
          domain: { x: [0.09, 0.91], y: [0.08, 0.98] },
          gauge: {
            shape: "angular",
            axis: {
              range: [0, 100],
              tickmode: "array",
              tickvals: [0, 20, 40, 60, 80, 100],
              ticktext: ["0", "20", "40", "60", "80", "100"],
              tickcolor: "#dbeafe",
              tickwidth: 2,
              ticklen: 15,
              tickfont: { color: "#eef4ff", size: 24, family: "Inter, Segoe UI, sans-serif" }
            },
            bar: {
              color: "#38bdf8",
              thickness: 0.2
            },
            bgcolor: "#14243d",
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
        margin: { t: 18, r: 54, b: 0, l: 54 },
        height: 360,
        font: { color: "#eef4ff", family: "Inter, Segoe UI, sans-serif" }
      },
      {
        displayModeBar: false,
        responsive: true,
        staticPlot: true
      }
    );
  }, [gaugeId, safePct]);

  return (
    <div className="risk-gauge">
      <div className="risk-gauge__meta">
        <span>Churn Risk Gauge</span>
      </div>
      <div id={gaugeId} className="plotly-gauge plotly-gauge--wide" aria-label="Churn risk gauge" />
      <div className="risk-gauge__value">{safePct.toFixed(2)}%</div>
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
          <div className="result-card summary-card result-copy">
            <div className={`badge badge--${result.risk_level.toLowerCase()}`}>{result.risk_level} RISK</div>

            <div className={`status-banner ${result.prediction === 1 ? "danger" : "safe"}`}>
              {result.prediction === 1 ? "Customer is likely to churn." : "Customer is likely to stay."}
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
      </div>
    </section>
  );
}
