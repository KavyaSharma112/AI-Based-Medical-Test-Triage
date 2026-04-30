// RiskCard.jsx — Displays one disease's prediction result
import React from "react";
import { useState } from "react";

const ICONS = {
  "Kidney Disease": "🫘",
  "Heart Disease": "❤️",
  "Liver Disease": "🫀",
  "Diabetes": "🩸",
};

const RISK_CONFIG = {
  Low:         { color: "#16a34a", bg: "#f0fdf4", border: "#bbf7d0", bar: "#22c55e", label: "Low Risk",      emoji: "✅" },
  Moderate:    { color: "#d97706", bg: "#fffbeb", border: "#fde68a", bar: "#f59e0b", label: "Moderate Risk", emoji: "⚠️" },
  High:        { color: "#dc2626", bg: "#fef2f2", border: "#fecaca", bar: "#ef4444", label: "High Risk",     emoji: "🔴" },
  Unknown:     { color: "#6b7280", bg: "#f9fafb", border: "#e5e7eb", bar: "#9ca3af", label: "Unknown",       emoji: "❓" },
  Unavailable: { color: "#6b7280", bg: "#f9fafb", border: "#e5e7eb", bar: "#9ca3af", label: "Unavailable",  emoji: "⚙️" },
};

export default function RiskCard({ prediction, animDelay = 0 }) {
  const [expanded, setExpanded] = useState(false);
  const cfg = RISK_CONFIG[prediction.risk_level] || RISK_CONFIG.Unknown;
  const pct = prediction.percentage;

  return (
    <div style={{
      background: cfg.bg,
      border: `1.5px solid ${cfg.border}`,
      borderRadius: "16px",
      padding: "1.5rem",
      animation: `slideUp 0.5s ease ${animDelay}s both`,
    }}>
      {/* Header row */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "1.2rem" }}>
        <span style={{ fontSize: "32px" }}>{ICONS[prediction.disease]}</span>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: "15px", fontWeight: 700, color: "#111827" }}>{prediction.disease}</div>
          <span style={{
            display: "inline-block", fontSize: "11px", fontWeight: 600,
            color: cfg.color, background: "white",
            border: `1px solid ${cfg.border}`, borderRadius: "20px",
            padding: "2px 10px", marginTop: "3px",
          }}>
            {cfg.emoji} {cfg.label}
          </span>
        </div>
        {/* Circular progress */}
        <div style={{
          width: 58, height: 58, borderRadius: "50%", flexShrink: 0,
          background: `conic-gradient(${cfg.bar} ${pct * 3.6}deg, #e5e7eb 0deg)`,
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          <div style={{
            width: 44, height: 44, borderRadius: "50%", background: cfg.bg,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "12px", fontWeight: 700, color: cfg.color,
          }}>{pct}%</div>
        </div>
      </div>

      {/* Progress bar */}
      <div style={{ marginBottom: "1rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "#6b7280", marginBottom: "4px" }}>
          <span>Risk Probability</span>
          <span style={{ fontWeight: 600, color: cfg.color }}>{(prediction.probability * 100).toFixed(1)}%</span>
        </div>
        <div style={{ background: "#e5e7eb", borderRadius: "99px", height: "7px", overflow: "hidden" }}>
          <div style={{ width: `${pct}%`, height: "100%", background: cfg.bar, borderRadius: "99px" }} />
        </div>
      </div>

      {/* Recommendation */}
      <div style={{
        fontSize: "13px", color: "#374151", lineHeight: 1.6,
        background: "white", borderRadius: "10px",
        padding: "10px 12px", border: `1px solid ${cfg.border}`,
      }}>
        {prediction.recommendation}
      </div>

      {/* Features toggle */}
      {prediction.features_used?.length > 0 && (
        <div style={{ marginTop: "10px" }}>
          <button onClick={() => setExpanded(!expanded)} style={{
            background: "none", border: "none", fontSize: "11px",
            color: cfg.color, cursor: "pointer", padding: 0, fontWeight: 600,
          }}>
            {expanded ? "▲ Hide" : "▼ Show"} features used ({prediction.features_used.length})
          </button>
          {expanded && (
            <div style={{ display: "flex", flexWrap: "wrap", gap: "5px", marginTop: "8px" }}>
              {prediction.features_used.map(f => (
                <span key={f} style={{
                  fontSize: "11px", background: "white",
                  border: `1px solid ${cfg.border}`, borderRadius: "6px",
                  padding: "2px 7px", color: "#374151",
                }}>{f.replace(/_/g, " ")}</span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
