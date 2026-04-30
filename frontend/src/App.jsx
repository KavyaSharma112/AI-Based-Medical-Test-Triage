// App.jsx — Main application. Manages mode switching, form state, and results display.
import { useState } from "react";
import LabForm from "./components/LabForm";
import PDFUpload from "./components/PDFUpload";
import RiskCard from "./components/RiskCard";
import { predictAll } from "./services/api";
import React from "react";

// Animation keyframes injected once
const GLOBAL_STYLES = `
  @keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #f1f5f9; font-family: 'Segoe UI', system-ui, sans-serif; }
  input::-webkit-outer-spin-button,
  input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
`;

export default function App() {
  const [mode, setMode] = useState("form");          // "form" | "pdf"
  const [formValues, setFormValues] = useState({});  // All input field values
  const [results, setResults] = useState(null);      // API response
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Handle any form field change
  function handleFieldChange(e) {
    const { name, value } = e.target;
    setFormValues(prev => ({ ...prev, [name]: value }));
  }

  // When PDF extraction completes, pre-fill form with extracted values
  function handlePDFExtracted(extractedValues) {
    setFormValues(prev => ({ ...prev, ...extractedValues }));
    // Switch to form mode so user can review before predicting
    setMode("form");
  }

  // Submit form → call /predict-all
  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const data = await predictAll(formValues);
      setResults(data);
      // Scroll to results
      setTimeout(() => {
        document.getElementById("results")?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setFormValues({});
    setResults(null);
    setError(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  const filledCount = Object.values(formValues).filter(v => v !== "" && v != null).length;

  return (
    <>
      <style>{GLOBAL_STYLES}</style>

      {/* ── Header ── */}
      <header style={{
        background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
        color: "white",
        padding: "2rem 1rem",
        textAlign: "center",
      }}>
        <div style={{ fontSize: "36px", marginBottom: "8px" }}>🏥</div>
        <h1 style={{ fontSize: "24px", fontWeight: 800, letterSpacing: "-0.5px", marginBottom: "6px" }}>
          AI Medical Test Triage System
        </h1>
        <p style={{ fontSize: "13px", color: "#94a3b8", maxWidth: "500px", margin: "0 auto" }}>
          Enter your lab values or upload a PDF report to assess risk across
          Kidney, Heart, Liver &amp; Diabetes conditions.
        </p>
        <div style={{
          display: "inline-block", marginTop: "12px",
          background: "#dc2626", borderRadius: "20px",
          padding: "4px 14px", fontSize: "11px", fontWeight: 600, color: "white",
        }}>
          ⚠️ NOT a medical diagnosis — for informational purposes only
        </div>
      </header>

      {/* ── Main Content ── */}
      <main style={{ maxWidth: "860px", margin: "0 auto", padding: "1.5rem 1rem 3rem" }}>

        {/* Mode toggle */}
        <div style={{
          display: "flex", gap: "8px", marginBottom: "1.5rem",
          background: "white", borderRadius: "12px", padding: "6px",
          border: "1px solid #e5e7eb",
        }}>
          {[
            { id: "form", label: "✏️  Enter Lab Values Manually" },
            { id: "pdf",  label: "📄  Upload PDF Report" },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setMode(tab.id)}
              style={{
                flex: 1, padding: "10px", fontSize: "13px", fontWeight: 600,
                border: "none", borderRadius: "8px", cursor: "pointer",
                background: mode === tab.id ? "linear-gradient(135deg, #6366f1, #8b5cf6)" : "transparent",
                color: mode === tab.id ? "white" : "#6b7280",
                transition: "all 0.2s",
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* PDF Upload mode */}
        {mode === "pdf" && (
          <div style={{
            background: "white", borderRadius: "14px",
            padding: "1.5rem", border: "1px solid #e5e7eb",
            marginBottom: "1.5rem",
            animation: "fadeIn 0.3s ease",
          }}>
            <PDFUpload onExtracted={handlePDFExtracted} />
          </div>
        )}

        {/* Field counter badge */}
        {filledCount > 0 && (
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between",
            background: "#eef2ff", border: "1px solid #c7d2fe",
            borderRadius: "10px", padding: "10px 16px", marginBottom: "1rem",
            fontSize: "13px",
          }}>
            <span style={{ color: "#4338ca", fontWeight: 600 }}>
              📋 {filledCount} field{filledCount !== 1 ? "s" : ""} filled
            </span>
            <button
              onClick={handleReset}
              style={{
                background: "none", border: "1px solid #c7d2fe",
                borderRadius: "6px", padding: "3px 10px",
                fontSize: "11px", color: "#6366f1", cursor: "pointer",
              }}
            >
              Clear all
            </button>
          </div>
        )}

        {/* Lab form (always visible so PDF results can be reviewed) */}
        <LabForm
          values={formValues}
          onChange={handleFieldChange}
          onSubmit={handleSubmit}
          loading={loading}
        />

        {/* Error */}
        {error && (
          <div style={{
            marginTop: "1rem",
            background: "#fef2f2", border: "1px solid #fecaca",
            borderRadius: "12px", padding: "1rem 1.25rem",
            fontSize: "13px", color: "#dc2626",
          }}>
            ❌ {error}
            <div style={{ fontSize: "12px", color: "#ef4444", marginTop: "4px" }}>
              Make sure your backend is running at http://localhost:8000
            </div>
          </div>
        )}

        {/* ── Results ── */}
        {results && (
          <div id="results" style={{ marginTop: "2rem", animation: "fadeIn 0.4s ease" }}>

            {/* Results header */}
            <div style={{
              display: "flex", alignItems: "center", justifyContent: "space-between",
              marginBottom: "1rem",
            }}>
              <h2 style={{ fontSize: "18px", fontWeight: 800, color: "#111827" }}>
                🔬 Prediction Results
              </h2>
              <span style={{ fontSize: "12px", color: "#6b7280" }}>
                Based on {results.input_summary.fields_provided} lab values
              </span>
            </div>

            {/* 4 Risk cards in 2-column grid */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
              gap: "1rem",
              marginBottom: "1.25rem",
            }}>
              {results.predictions.map((pred, i) => (
                <RiskCard key={pred.disease} prediction={pred} animDelay={i * 0.1} />
              ))}
            </div>

            {/* Disclaimer */}
            <div style={{
              background: "#fffbeb", border: "1px solid #fde68a",
              borderRadius: "12px", padding: "1rem 1.25rem",
              fontSize: "12px", color: "#92400e", lineHeight: 1.6,
            }}>
              {results.disclaimer}
            </div>

            {/* New analysis button */}
            <button
              onClick={handleReset}
              style={{
                marginTop: "1rem", width: "100%",
                background: "white", border: "1.5px solid #e5e7eb",
                borderRadius: "12px", padding: "12px",
                fontSize: "14px", fontWeight: 600, color: "#374151",
                cursor: "pointer",
              }}
            >
              ↩ Start New Analysis
            </button>
          </div>
        )}
      </main>
    </>
  );
}
