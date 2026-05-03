// RiskCard.jsx — Displays one disease's prediction result
import React from "react";
// RiskCard.jsx (v2) — Now shows raw vs adjusted probability + abnormal markers
import { useState } from "react";

const ICONS = {
  "Kidney Disease": "🫘",
  "Heart Disease":  "❤️",
  "Liver Disease":  "🫀",
  "Diabetes":       "🩸",
};

const RISK_CONFIG = {
  Low:         { color: "#16a34a", bg: "#f0fdf4", border: "#bbf7d0", bar: "#22c55e", label: "Low Risk",      emoji: "✅" },
  Moderate:    { color: "#d97706", bg: "#fffbeb", border: "#fde68a", bar: "#f59e0b", label: "Moderate Risk", emoji: "⚠️" },
  High:        { color: "#dc2626", bg: "#fef2f2", border: "#fecaca", bar: "#ef4444", label: "High Risk",     emoji: "🔴" },
  Unknown:     { color: "#6b7280", bg: "#f9fafb", border: "#e5e7eb", bar: "#9ca3af", label: "Unknown",       emoji: "❓" },
  Unavailable: { color: "#6b7280", bg: "#f9fafb", border: "#e5e7eb", bar: "#9ca3af", label: "Unavailable",  emoji: "⚙️" },
};

export default function RiskCard({ prediction, animDelay = 0 }) {
  const [showDetails, setShowDetails] = useState(false);
  const cfg = RISK_CONFIG[prediction.risk_level] || RISK_CONFIG.Unknown;
  const pct = prediction.percentage;

  // Was the probability adjusted significantly by clinical check?
  const rawPct = prediction.raw_model_probability != null
    ? Math.round(prediction.raw_model_probability * 100)
    : null;
  const wasAdjusted = rawPct != null && Math.abs(rawPct - pct) >= 3;

  return (
    <div style={{
      background: cfg.bg,
      border: `1.5px solid ${cfg.border}`,
      borderRadius: "16px",
      padding: "1.5rem",
      animation: `slideUp 0.5s ease ${animDelay}s both`,
    }}>

      {/* ── Header row ── */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "1.2rem" }}>
        <span style={{ fontSize: "32px" }}>{ICONS[prediction.disease]}</span>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: "15px", fontWeight: 700, color: "#111827" }}>
            {prediction.disease}
          </div>
          <span style={{
            display: "inline-block", fontSize: "11px", fontWeight: 600,
            color: cfg.color, background: "white",
            border: `1px solid ${cfg.border}`, borderRadius: "20px",
            padding: "2px 10px", marginTop: "3px",
          }}>
            {cfg.emoji} {cfg.label}
          </span>
        </div>

        {/* Circular progress dial */}
        <div style={{
          width: 62, height: 62, borderRadius: "50%", flexShrink: 0,
          background: `conic-gradient(${cfg.bar} ${pct * 3.6}deg, #e5e7eb 0deg)`,
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          <div style={{
            width: 46, height: 46, borderRadius: "50%", background: cfg.bg,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "12px", fontWeight: 700, color: cfg.color,
          }}>
            {pct}%
          </div>
        </div>
      </div>

      {/* ── Probability bar ── */}
      <div style={{ marginBottom: "1rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "#6b7280", marginBottom: "4px" }}>
          <span>Adjusted Risk Score</span>
          <span style={{ fontWeight: 600, color: cfg.color }}>{(prediction.probability * 100).toFixed(1)}%</span>
        </div>
        <div style={{ background: "#e5e7eb", borderRadius: "99px", height: "7px", overflow: "hidden" }}>
          <div style={{ width: `${pct}%`, height: "100%", background: cfg.bar, borderRadius: "99px" }} />
        </div>
        {/* Show raw model probability if it differs */}
        {wasAdjusted && rawPct != null && (
          <div style={{ fontSize: "11px", color: "#6b7280", marginTop: "4px" }}>
            ML model output: {rawPct}%
            {rawPct > pct
              ? <span style={{ color: "#16a34a" }}> ↓ reduced after clinical check</span>
              : <span style={{ color: "#dc2626" }}> ↑ increased after clinical check</span>
            }
          </div>
        )}
      </div>

      {/* ── Recommendation ── */}
      <div style={{
        fontSize: "13px", color: "#374151", lineHeight: 1.6,
        background: "white", borderRadius: "10px",
        padding: "10px 12px", border: `1px solid ${cfg.border}`,
        marginBottom: "10px",
      }}>
        {prediction.recommendation}
      </div>

      {/* ── Confidence note ── */}
      {prediction.confidence_note && (
        <div style={{
          fontSize: "11px", color: "#6b7280", lineHeight: 1.5,
          background: "white", borderRadius: "8px",
          padding: "8px 10px", border: "1px solid #f3f4f6",
          marginBottom: "8px",
        }}>
          🔍 {prediction.confidence_note}
        </div>
      )}

      {/* ── Abnormal markers warning ── */}
      {prediction.abnormal_markers?.length > 0 && (
        <div style={{
          background: "#fffbeb", border: "1px solid #fde68a",
          borderRadius: "8px", padding: "8px 10px", marginBottom: "8px",
        }}>
          <div style={{ fontSize: "11px", fontWeight: 600, color: "#92400e", marginBottom: "4px" }}>
            ⚠️ Markers outside normal range:
          </div>
          {prediction.abnormal_markers.map((m, i) => (
            <div key={i} style={{ fontSize: "11px", color: "#78350f", lineHeight: 1.6 }}>• {m}</div>
          ))}
        </div>
      )}

      {/* ── Details toggle ── */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        style={{
          background: "none", border: "none", fontSize: "11px",
          color: cfg.color, cursor: "pointer", padding: 0, fontWeight: 600,
        }}
      >
        {showDetails ? "▲ Hide" : "▼ Show"} details
      </button>

      {showDetails && (
        <div style={{ marginTop: "8px", display: "flex", flexDirection: "column", gap: "6px" }}>
          {/* Markers checked count */}
          {prediction.markers_checked > 0 && (
            <div style={{ fontSize: "11px", color: "#6b7280" }}>
              📊 {prediction.markers_checked} key marker{prediction.markers_checked !== 1 ? "s" : ""} cross-checked against clinical ranges
            </div>
          )}
          {/* Features used */}
          {prediction.features_used?.length > 0 && (
            <div>
              <div style={{ fontSize: "11px", color: "#6b7280", marginBottom: "4px" }}>
                Fields used ({prediction.features_used.length}):
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                {prediction.features_used.map(f => (
                  <span key={f} style={{
                    fontSize: "10px", background: "white",
                    border: `1px solid ${cfg.border}`, borderRadius: "5px",
                    padding: "2px 6px", color: "#374151",
                  }}>
                    {f.replace(/_/g, " ")}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
