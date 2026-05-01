// api.js — All backend calls go through here
const BASE_URL = "http://localhost:8000/api";

export async function predictAll(formData) {
  // Remove empty fields before sending
  const cleaned = {};
  for (const [key, val] of Object.entries(formData)) {
    if (val !== "" && val !== null && val !== undefined) {
      cleaned[key] = parseFloat(val);
    }
  }
  const response = await fetch(`${BASE_URL}/predict-all`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cleaned),
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || "Prediction failed");
  }
  return response.json();
}

export async function uploadPDF(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${BASE_URL}/upload-pdf`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || "PDF upload failed");
  }
  return response.json();
}
