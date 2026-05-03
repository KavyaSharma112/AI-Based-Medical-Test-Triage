// PDFUpload.jsx — Drag-and-drop PDF upload component
import React from "react";
import { useState, useRef } from "react";
import { uploadPDF } from "../services/api";

export default function PDFUpload({ onExtracted }) {
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef();

  async function handleFile(file) {
    if (!file || !file.name.endsWith(".pdf")) {
      setError("Please upload a PDF file.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await uploadPDF(file);
      setResult(data);
      // Pass extracted values up to parent so form gets pre-filled
      if (data.extracted_values) {
        onExtracted(data.extracted_values);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      {/* Drop zone */}
      <div
        onClick={() => inputRef.current.click()}
        onDragOver={e => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${dragging ? "#6366f1" : "#d1d5db"}`,
          borderRadius: "14px",
          padding: "2.5rem 1.5rem",
          textAlign: "center",
          cursor: "pointer",
          background: dragging ? "#eef2ff" : "#fafafa",
          transition: "all 0.2s",
        }}
      >
        <div style={{ fontSize: "40px", marginBottom: "8px" }}>📄</div>
        <div style={{ fontSize: "15px", fontWeight: 600, color: "#374151", marginBottom: "4px" }}>
          {loading ? "Extracting values..." : "Drop your lab report PDF here"}
        </div>
        <div style={{ fontSize: "12px", color: "#9ca3af" }}>
          or click to browse · Max 10MB · Digital PDFs work best
        </div>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          style={{ display: "none" }}
          onChange={e => handleFile(e.target.files[0])}
        />
      </div>

      {/* Loading spinner */}
      {loading && (
        <div style={{ textAlign: "center", color: "#6366f1", fontSize: "14px", fontWeight: 500 }}>
          ⏳ Reading PDF and extracting lab values...
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{
          background: "#fef2f2", border: "1px solid #fecaca",
          borderRadius: "10px", padding: "12px 16px",
          fontSize: "13px", color: "#dc2626",
        }}>
          ❌ {error}
        </div>
      )}

      {/* Success */}
      {result && (
        <div style={{
          background: "#f0fdf4", border: "1px solid #bbf7d0",
          borderRadius: "10px", padding: "12px 16px",
        }}>
          <div style={{ fontSize: "13px", fontWeight: 600, color: "#16a34a", marginBottom: "8px" }}>
            ✅ {result.fields_extracted} values extracted from "{result.filename}"
          </div>
          <div style={{ fontSize: "12px", color: "#15803d", marginBottom: "8px" }}>
            {result.message}
          </div>
          {/* Show extracted fields */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: "5px" }}>
            {Object.entries(result.extracted_values || {}).map(([k, v]) => (
              <span key={k} style={{
                fontSize: "11px", background: "white",
                border: "1px solid #bbf7d0", borderRadius: "6px",
                padding: "2px 8px", color: "#374151",
              }}>
                {k.replace(/_/g, " ")}: <strong>{v}</strong>
              </span>
            ))}
          </div>
          <div style={{ fontSize: "11px", color: "#6b7280", marginTop: "8px" }}>
            ↓ The form below has been pre-filled. Review values before running predictions.
          </div>
        </div>
      )}
    </div>
  );
}
