import { useState } from "react";

import { runSinglePrediction } from "../api/client";
import FormSection from "../components/FormSection";
import ResultCard from "../components/ResultCard";

const defaultValues = {
  Age: 30,
  Gender: "Male",
  Tenure: 12,
  "Usage Frequency": 10,
  "Support Calls": 1,
  "Payment Delay": 0,
  "Subscription Type": "Basic",
  "Contract Length": "1 month",
  "Total Spend": 500,
  "Last Interaction": 5
};

export default function SinglePredictionPage() {
  const [values, setValues] = useState(defaultValues);
  const [result, setResult] = useState(null);
  const [isResultStale, setIsResultStale] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit() {
    setIsLoading(true);
    setError("");
    try {
      const data = await runSinglePrediction(values);
      setResult(data);
      setIsResultStale(false);
    } catch (err) {
      setError(err.message ?? "Prediction failed.");
    } finally {
      setIsLoading(false);
    }
  }

  function updateField(key, value) {
    setValues((current) => ({ ...current, [key]: value }));
    if (result) {
      setIsResultStale(true);
    }
  }

  return (
    <div className="page-stack">
      <FormSection values={values} onChange={updateField} disabled={isLoading} />
      <div className="action-row">
        <button className="primary-button" onClick={handleSubmit} disabled={isLoading}>
          {isLoading ? "Running..." : "Run Prediction"}
        </button>
        {error ? <div className="error-banner">{error}</div> : null}
      </div>
      <ResultCard result={result} title="Single Prediction Result" stale={isResultStale} />
    </div>
  );
}
