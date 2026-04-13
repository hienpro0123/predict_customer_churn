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
                <th>Recommended Action</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.prediction_id}>
                  <td>{row.prediction_id}</td>
                  <td>{row.predicted_label}</td>
                  <td>{(row.churn_probability * 100).toFixed(2)}%</td>
                  <td>{row.recommended_action || "-"}</td>
                  <td>{new Date(row.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
