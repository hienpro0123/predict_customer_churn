function formatCreatedAt(value) {
  if (!value) {
    return "-";
  }
  const raw = String(value);
  const normalized = /z$/i.test(raw) || /[+-]\d{2}:\d{2}$/.test(raw) ? raw : `${raw}Z`;
  const date = new Date(normalized);
  if (Number.isNaN(date.getTime())) {
    return raw;
  }

  return new Intl.DateTimeFormat("vi-VN", {
    timeZone: "Asia/Ho_Chi_Minh",
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    day: "2-digit",
    month: "2-digit",
    year: "numeric"
  }).format(date);
}

export default function PredictionHistory({ rows }) {
  return (
    <section>
      <h4>Prediction History</h4>

      {rows.length === 0 ? (
        <div className="empty-state">No prediction history is available for this customer yet.</div>
      ) : (
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Label</th>
                <th>Probability</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.prediction_id}>
                  <td>{row.prediction_id}</td>
                  <td>{row.predicted_label}</td>
                  <td>{(row.churn_probability * 100).toFixed(2)}%</td>
                  <td>{formatCreatedAt(row.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
