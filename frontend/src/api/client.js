const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") ?? "";
  const data = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    const message =
      typeof data === "string"
        ? data
        : data?.detail?.message ?? data?.detail ?? data?.message ?? "Request failed.";
    const errors = typeof data === "object" && data?.detail?.errors ? data.detail.errors : [];
    throw { message, errors };
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
