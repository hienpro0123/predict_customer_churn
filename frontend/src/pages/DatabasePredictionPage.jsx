import { useEffect, useState } from "react";

import {
  fetchCustomer,
  fetchCustomerPredictions,
  fetchCustomers,
  runCustomerPrediction
} from "../api/client";
import FormSection from "../components/FormSection";
import PredictionHistory from "../components/PredictionHistory";
import ResultCard from "../components/ResultCard";

function mapCustomerToInputs(customer) {
  return {
    Age: customer.age,
    Gender: customer.gender,
    Tenure: customer.tenure,
    "Usage Frequency": customer.usage_frequency,
    "Support Calls": customer.support_calls,
    "Payment Delay": customer.payment_delay,
    "Subscription Type": customer.subscription_type,
    "Contract Length": customer.contract_length,
    "Total Spend": customer.total_spend,
    "Last Interaction": customer.last_interaction
  };
}

export default function DatabasePredictionPage() {
  const [customers, setCustomers] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [values, setValues] = useState(null);
  const [history, setHistory] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isLoadingCustomers, setIsLoadingCustomers] = useState(true);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    fetchCustomers()
      .then((data) => {
        setCustomers(data);
        if (data.length > 0) {
          setSelectedId(data[0].id);
        }
      })
      .catch((err) => setError(err.message ?? "Could not load customers."))
      .finally(() => setIsLoadingCustomers(false));
  }, []);

  useEffect(() => {
    if (!selectedId) {
      return;
    }

    Promise.all([fetchCustomer(selectedId), fetchCustomerPredictions(selectedId)])
      .then(([customer, predictionHistory]) => {
        setValues(mapCustomerToInputs(customer));
        setHistory(predictionHistory);
        setResult(null);
      })
      .catch((err) => setError(err.message ?? "Could not load customer detail."));
  }, [selectedId]);

  function updateField(key, value) {
    setValues((current) => ({ ...current, [key]: value }));
  }

  async function handlePredict() {
    setIsRunning(true);
    setError("");
    try {
      const data = await runCustomerPrediction(selectedId, values);
      setResult(data.result);
      setHistory(data.history);
    } catch (err) {
      setError(err.message ?? "Could not run prediction for this customer.");
    } finally {
      setIsRunning(false);
    }
  }

  if (isLoadingCustomers) {
    return <div className="empty-state">Loading customers...</div>;
  }

  return (
    <div className="page-stack">
      <section>
        <h4>Predict From Database</h4>
        <p className="section-caption">Select a stored customer, review the profile, and save a new prediction.</p>
        <div className="form-card">
          <label className="field">
            <span>Customer ID</span>
            <select value={selectedId} onChange={(event) => setSelectedId(event.target.value)}>
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.id}
                </option>
              ))}
            </select>
          </label>
        </div>
      </section>

      {values ? <FormSection values={values} onChange={updateField} disabled={isRunning} /> : null}

      <div className="action-row">
        <button className="primary-button full-width" onClick={handlePredict} disabled={!values || isRunning}>
          {isRunning ? "Scoring..." : "Run Prediction From Database"}
        </button>
        {error ? <div className="error-banner">{error}</div> : null}
      </div>

      <ResultCard result={result} title="Prediction Result" />
      <PredictionHistory rows={history} />
    </div>
  );
}
