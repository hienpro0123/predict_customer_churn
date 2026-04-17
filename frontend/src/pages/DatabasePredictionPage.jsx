import { useEffect, useState } from "react";

import {
  fetchCustomers,
  fetchCustomer,
  fetchCustomerPredictions,
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
  const [customerOptions, setCustomerOptions] = useState([]);
  const [customerIdInput, setCustomerIdInput] = useState("");
  const [selectedId, setSelectedId] = useState("");
  const [values, setValues] = useState(null);
  const [history, setHistory] = useState([]);
  const [result, setResult] = useState(null);
  const [isResultStale, setIsResultStale] = useState(false);
  const [error, setError] = useState("");
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(true);
  const [isLoadingCustomer, setIsLoadingCustomer] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    fetchCustomers()
      .then((data) => setCustomerOptions(data.map((item) => item.id)))
      .catch(() => setCustomerOptions([]))
      .finally(() => setIsLoadingSuggestions(false));
  }, []);

  async function handleLoadCustomer() {
    const normalizedId = customerIdInput.trim();
    if (!normalizedId) {
      setError("Vui lòng nhập Customer ID.");
      return;
    }

    setIsLoadingCustomer(true);
    setError("");
    try {
      const [customer, predictionHistory] = await Promise.all([
        fetchCustomer(normalizedId),
        fetchCustomerPredictions(normalizedId)
      ]);
      setSelectedId(normalizedId);
      setValues(mapCustomerToInputs(customer));
      setHistory(predictionHistory);
      setResult(null);
      setIsResultStale(false);
    } catch (err) {
      setValues(null);
      setHistory([]);
      setResult(null);
      if (err?.status === 404) {
        setError("Không tìm thấy khách hàng.");
      } else {
        setError(err.message ?? "Không thể tải thông tin khách hàng.");
      }
    } finally {
      setIsLoadingCustomer(false);
    }
  }

  function updateField(key, value) {
    setValues((current) => ({ ...current, [key]: value }));
    if (result) {
      setIsResultStale(true);
    }
  }

  async function handlePredict() {
    if (!selectedId || !values) {
      setError("Vui lòng load khách hàng trước.");
      return;
    }
    setIsRunning(true);
    setError("");
    try {
      const data = await runCustomerPrediction(selectedId, values);
      setResult(data.result);
      setHistory(data.history);
      setIsResultStale(false);
    } catch (err) {
      setError(err.message ?? "Could not run prediction for this customer.");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <div className="page-stack">
      <section>
        <h4>Predict From Database</h4>
        <p className="section-caption">Enter a customer ID (e.g. ST01), load profile, then run prediction.</p>
        <div className="form-card">
          <div className="inline-controls">
            <label className="field compact">
              <span>Customer ID</span>
              <input
                type="text"
                value={customerIdInput}
                onChange={(event) => setCustomerIdInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    handleLoadCustomer();
                  }
                }}
                list="customer-id-options"
                placeholder="Enter customer ID, e.g. ST01"
              />
            </label>
            <datalist id="customer-id-options">
              {customerOptions.map((customerId) => (
                <option key={customerId} value={customerId} />
              ))}
            </datalist>
            <button
              className="secondary-button"
              type="button"
              onClick={handleLoadCustomer}
              disabled={isLoadingCustomer || isLoadingSuggestions}
            >
              {isLoadingCustomer ? "Loading..." : "Load Customer"}
            </button>
          </div>
          {isLoadingSuggestions ? <p className="section-caption">Đang tải danh sách khách hàng...</p> : null}
        </div>
      </section>

      {values ? <FormSection values={values} onChange={updateField} disabled={isRunning || isLoadingCustomer} /> : null}

      <div className="action-row">
        <button className="primary-button full-width" onClick={handlePredict} disabled={!values || isRunning || isLoadingCustomer}>
          {isRunning ? "Running..." : "Run Prediction From Database"}
        </button>
        {error ? <div className="error-banner">{error}</div> : null}
      </div>

      <ResultCard result={result} title="Prediction Result" stale={isResultStale} />
      <PredictionHistory rows={history} />
    </div>
  );
}
