const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

function toErrorList(detail) {
  if (Array.isArray(detail)) {
    return detail.map((item) => {
      if (typeof item === "string") {
        return item;
      }
      const path = Array.isArray(item?.loc) ? item.loc.join(".") : "";
      const text = item?.msg ?? "Invalid input.";
      return path ? `${path}: ${text}` : text;
    });
  }
  if (typeof detail === "string") {
    return [detail];
  }
  return [];
}

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") ?? "";
  const data = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    const detail = typeof data === "object" ? data?.detail : undefined;
    const errors =
      typeof data === "object" ? toErrorList(data?.detail?.errors ?? detail) : [];
    const message =
      typeof data === "string"
        ? data
        : data?.detail?.message ??
          (typeof detail === "string" ? detail : "") ??
          data?.message ??
          "Request failed.";

    const error = new Error(message || errors[0] || "Request failed.");
    error.errors = errors;
    error.status = response.status;
    throw error;
  }

  return data;
}

export async function fetchCustomers() {
  const response = await fetch(`${API_BASE_URL}/customers`);
  return parseResponse(response);
}

export async function fetchCustomer(customerId) {
  const response = await fetch(`${API_BASE_URL}/customers/${customerId}`);
  return parseResponse(response);
}

export async function fetchCustomerPredictions(customerId) {
  const response = await fetch(`${API_BASE_URL}/customers/${customerId}/predictions`);
  return parseResponse(response);
}

export async function runSinglePrediction(inputs) {
  const response = await fetch(`${API_BASE_URL}/predictions/single`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ inputs })
  });
  return parseResponse(response);
}

export async function runCustomerPrediction(customerId, inputs) {
  const response = await fetch(`${API_BASE_URL}/customers/${customerId}/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ inputs })
  });
  return parseResponse(response);
}

export async function runBatchPrediction(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/predictions/batch`, {
    method: "POST",
    body: formData
  });
  return parseResponse(response);
}
