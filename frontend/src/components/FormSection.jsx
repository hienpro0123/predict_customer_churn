const contractOptions = [
  { label: "Monthly", value: "1 month" },
  { label: "Quarterly", value: "3 months" },
  { label: "Annual", value: "12 months" }
];

const subscriptionOptions = ["Basic", "Standard", "Premium"];
const genderOptions = ["Male", "Female"];

const customerFields = [
  { key: "Age", label: "Age", type: "number", min: 18, max: 80 },
  { key: "Tenure", label: "Tenure (months)", type: "number", min: 1, max: 60 },
  { key: "Usage Frequency", label: "Usage Frequency", type: "number", min: 1, max: 30 },
  { key: "Support Calls", label: "Support Calls", type: "number", min: 0, max: 20 }
];

const subscriptionFields = [
  { key: "Payment Delay", label: "Payment Delay", type: "number", min: 0, max: 30 },
  { key: "Total Spend", label: "Total Spend", type: "number", min: 0, max: 10000, step: 0.01 },
  { key: "Last Interaction", label: "Last Interaction", type: "number", min: 0, max: 30 }
];

function NumberField({ field, values, onChange, disabled }) {
  const value = values[field.key];

  return (
    <label className="field">
      <span>{field.label}</span>
      <input
        disabled={disabled}
        type={field.type}
        value={value ?? ""}
        min={field.min}
        max={field.max}
        step={field.step ?? 1}
        onChange={(event) => {
          const rawValue = event.target.value;
          if (rawValue === "") {
            onChange(field.key, "");
            return;
          }
          const numericValue = Number(rawValue);
          if (Number.isNaN(numericValue)) {
            return;
          }
          onChange(field.key, numericValue);
        }}
      />
    </label>
  );
}

export default function FormSection({ values, onChange, disabled = false }) {
  return (
    <section>
      <h4>Customer Profile Inputs</h4>
      <div className="split-grid">
        <div className="form-card">
          <h3>Customer Information</h3>
          <div className="form-grid">
            {customerFields.map((field) => (
              <NumberField
                key={field.key}
                field={field}
                values={values}
                onChange={onChange}
                disabled={disabled}
              />
            ))}
            <label className="field">
              <span>Gender</span>
              <select
                disabled={disabled}
                value={values["Gender"]}
                onChange={(event) => onChange("Gender", event.target.value)}
              >
                {genderOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>

        <div className="form-card">
          <h3>Subscription Details</h3>
          <div className="form-grid">
            {subscriptionFields.map((field) => (
              <NumberField
                key={field.key}
                field={field}
                values={values}
                onChange={onChange}
                disabled={disabled}
              />
            ))}
            <label className="field">
              <span>Subscription Type</span>
              <select
                disabled={disabled}
                value={values["Subscription Type"]}
                onChange={(event) => onChange("Subscription Type", event.target.value)}
              >
                {subscriptionOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Contract Length</span>
              <select
                disabled={disabled}
                value={values["Contract Length"]}
                onChange={(event) => onChange("Contract Length", event.target.value)}
              >
                {contractOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>
      </div>
    </section>
  );
}
