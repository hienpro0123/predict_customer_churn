function formatPercent(value) {
  return `${(value * 100).toFixed(2)}%`;
}

export default function ResultCard({ result, title }) {
  if (!result) {
    return null;
  }

  return (
    <section>
      <h4>Model Decision</h4>
      <h3>{title}</h3>

      <div className="result-shell">
        <div className="result-card gauge-card">
          <div className="gauge-title">Churn Risk (%)</div>
          <div className="risk-meter__value">{formatPercent(result.probability)}</div>
          <div className={`risk-pill risk-pill--${result.risk_level.toLowerCase()}`}>{result.risk_level} RISK</div>
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
            <small className="insight-source">
              Source: {result.insight.insight_source}
              {result.insight.insight_error ? ` (${result.insight.insight_error})` : ""}
            </small>
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
