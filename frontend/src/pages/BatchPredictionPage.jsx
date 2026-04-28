import { useMemo, useState } from "react";

import { runBatchPrediction } from "../api/client";

const requiredColumns = [
  "Age",
  "Gender",
  "Tenure",
  "Usage Frequency",
  "Support Calls",
  "Payment Delay",
  "Subscription Type",
  "Contract Length",
  "Total Spend",
  "Last Interaction"
];

export default function BatchPredictionPage() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [errors, setErrors] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const downloadUrl = useMemo(() => {
    if (!result?.csv_content) {
      return "";
    }
    const blob = new Blob([result.csv_content], { type: "text/csv;charset=utf-8;" });
    return URL.createObjectURL(blob);
  }, [result]);

  async function handleRun() {
    if (!file) {
      return;
    }
    setIsLoading(true);
    setError("");
    setErrors([]);
    try {
      const data = await runBatchPrediction(file);
      setResult(data);
    } catch (err) {
      setError(err.message ?? "Batch prediction failed.");
      setErrors(err.errors ?? []);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="page-stack">
      <section>
        <h4>Batch Predict (CSV)</h4>
        <p className="section-caption">Upload CSV with required columns to run prediction for multiple customers at once.</p>
        <div className="form-card">
          <div className="code-block">{requiredColumns.join(", ")}</div>
          <input
            className="file-input"
            type="file"
            accept=".csv"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
        </div>
      </section>

      <div className="action-row">
        <button className="primary-button full-width" onClick={handleRun} disabled={!file || isLoading}>
          {isLoading ? "Processing..." : "Run Batch Prediction"}
        </button>
        {error ? <div className="error-banner">{error}</div> : null}
      </div>

      {errors.length > 0 ? (
        <section className="form-card">
          <h4>Validation Errors</h4>
          <ul className="error-list">
            {errors.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      ) : null}

      {result ? (
        <section>
          <h4>Batch Results</h4>
          <div className="success-banner">Batch prediction completed for {result.count} rows.</div>

          <a className="secondary-button" href={downloadUrl} download="batch_prediction_results.csv">
            Download Batch Result CSV
          </a>

          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Row</th>
                  <th>Prediction</th>
                  <th>Probability</th>
                  <th>Risk</th>
                  <th>Subscription</th>
                  <th>Contract</th>
                </tr>
              </thead>
              <tbody>
                {result.rows.map((row) => (
                  <tr key={row.row}>
                    <td>{row.row}</td>
                    <td>{row.prediction}</td>
                    <td>{row.churn_probability_percent.toFixed(2)}%</td>
                    <td>{row.risk_level}</td>
                    <td>{row.inputs["Subscription Type"]}</td>
                    <td>{row.inputs["Contract Length"]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}
    </div>
  );
}
