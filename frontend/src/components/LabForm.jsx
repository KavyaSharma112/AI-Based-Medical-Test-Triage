// LabForm.jsx — Input form grouped by disease / body system
// All fields are optional. User fills in only what they have.

// Field definitions grouped into sections
const SECTIONS = [
  {
    title: "👤 Basic Info",
    color: "#6366f1",
    fields: [
      { name: "age",    label: "Age (years)",        placeholder: "e.g. 45" },
      { name: "gender", label: "Gender (0=F, 1=M)",  placeholder: "0 or 1" },
      { name: "bmi",    label: "BMI",                placeholder: "e.g. 25.0" },
    ],
  },
  {
    title: "🫘 Kidney Panel",
    color: "#0ea5e9",
    fields: [
      { name: "blood_pressure",       label: "Blood Pressure (mm/Hg)",     placeholder: "e.g. 80" },
      { name: "specific_gravity",     label: "Specific Gravity",           placeholder: "e.g. 1.020" },
      { name: "albumin",              label: "Albumin in Urine (0–5)",     placeholder: "0–5" },
      { name: "sugar",                label: "Sugar in Urine (0–5)",       placeholder: "0–5" },
      { name: "blood_glucose_random", label: "Blood Glucose Random (mg/dL)", placeholder: "e.g. 121" },
      { name: "blood_urea",           label: "Blood Urea (mg/dL)",         placeholder: "e.g. 36" },
      { name: "serum_creatinine",     label: "Serum Creatinine (mg/dL)",   placeholder: "e.g. 1.2" },
      { name: "sodium",               label: "Sodium (mEq/L)",             placeholder: "e.g. 137" },
      { name: "potassium",            label: "Potassium (mEq/L)",          placeholder: "e.g. 4.2" },
      { name: "haemoglobin",          label: "Haemoglobin (g/dL)",         placeholder: "e.g. 15.4" },
      { name: "packed_cell_volume",   label: "Packed Cell Volume",         placeholder: "e.g. 44" },
      { name: "white_blood_cell_count", label: "WBC Count (cells/cumm)",   placeholder: "e.g. 7800" },
      { name: "red_blood_cell_count", label: "RBC Count (millions/cmm)",   placeholder: "e.g. 5.2" },
      { name: "hypertension",         label: "Hypertension (0=No, 1=Yes)", placeholder: "0 or 1" },
      { name: "diabetes_mellitus",    label: "Diabetes Mellitus (0=No, 1=Yes)", placeholder: "0 or 1" },
      { name: "appetite",             label: "Appetite (0=Poor, 1=Good)",  placeholder: "0 or 1" },
      { name: "peda_edema",           label: "Pedal Edema (0=No, 1=Yes)", placeholder: "0 or 1" },
      { name: "aanemia",              label: "Anemia (0=No, 1=Yes)",       placeholder: "0 or 1" },
    ],
  },
  {
    title: "❤️ Heart Panel",
    color: "#ef4444",
    fields: [
      { name: "cholesterol",          label: "Cholesterol (mg/dL)",        placeholder: "e.g. 200" },
      { name: "resting_blood_pressure", label: "Resting BP (mm/Hg)",       placeholder: "e.g. 120" },
      { name: "fasting_blood_sugar",  label: "Fasting Blood Sugar >120? (0/1)", placeholder: "0 or 1" },
      { name: "resting_ecg",          label: "Resting ECG (0/1/2)",        placeholder: "0, 1, or 2" },
      { name: "max_heart_rate",       label: "Max Heart Rate",             placeholder: "e.g. 150" },
      { name: "chest_pain_type",      label: "Chest Pain Type (0–3)",      placeholder: "0, 1, 2, or 3" },
      { name: "exercise_angina",      label: "Exercise Angina (0=No, 1=Yes)", placeholder: "0 or 1" },
      { name: "st_depression",        label: "ST Depression",              placeholder: "e.g. 0.0" },
      { name: "st_slope",             label: "ST Slope (0/1/2)",           placeholder: "0, 1, or 2" },
      { name: "num_vessels",          label: "Num Major Vessels (0–3)",    placeholder: "0–3" },
      { name: "thalassemia",          label: "Thalassemia (0/1/2)",        placeholder: "0, 1, or 2" },
    ],
  },
  {
    title: "🫀 Liver Panel",
    color: "#f59e0b",
    fields: [
      { name: "total_bilirubin",           label: "Total Bilirubin (mg/dL)",    placeholder: "e.g. 0.7" },
      { name: "direct_bilirubin",          label: "Direct Bilirubin (mg/dL)",   placeholder: "e.g. 0.1" },
      { name: "alkaline_phosphotase",      label: "Alkaline Phosphatase (IU/L)", placeholder: "e.g. 187" },
      { name: "alamine_aminotransferase",  label: "ALT / SGPT (IU/L)",          placeholder: "e.g. 16" },
      { name: "aspartate_aminotransferase", label: "AST / SGOT (IU/L)",         placeholder: "e.g. 18" },
      { name: "total_proteins",            label: "Total Proteins (g/dL)",      placeholder: "e.g. 6.8" },
      { name: "albumin_globulin_ratio",    label: "Albumin/Globulin Ratio",     placeholder: "e.g. 0.9" },
    ],
  },
  {
    title: "🩸 Diabetes Panel",
    color: "#8b5cf6",
    fields: [
      { name: "glucose",                   label: "Glucose (mg/dL)",            placeholder: "e.g. 120" },
      { name: "insulin",                   label: "Insulin (mu U/ml)",          placeholder: "e.g. 79" },
      { name: "skin_thickness",            label: "Skin Thickness (mm)",        placeholder: "e.g. 20" },
      { name: "pregnancies",               label: "Number of Pregnancies",      placeholder: "e.g. 0" },
      { name: "diabetes_pedigree_function", label: "Diabetes Pedigree Function", placeholder: "e.g. 0.5" },
    ],
  },
];

export default function LabForm({ values, onChange, onSubmit, loading }) {
  return (
    <form onSubmit={onSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {SECTIONS.map(section => (
        <div key={section.title} style={{
          background: "white",
          border: "1px solid #e5e7eb",
          borderRadius: "14px",
          overflow: "hidden",
        }}>
          {/* Section header */}
          <div style={{
            background: section.color + "12",
            borderBottom: `2px solid ${section.color}30`,
            padding: "0.75rem 1.25rem",
            fontSize: "14px",
            fontWeight: 700,
            color: section.color,
          }}>
            {section.title}
          </div>

          {/* Fields grid */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
            gap: "1rem",
            padding: "1.25rem",
          }}>
            {section.fields.map(field => (
              <div key={field.name}>
                <label style={{
                  display: "block", fontSize: "11px", fontWeight: 600,
                  color: "#374151", marginBottom: "4px", textTransform: "uppercase",
                  letterSpacing: "0.03em",
                }}>
                  {field.label}
                </label>
                <input
                  type="number"
                  step="any"
                  name={field.name}
                  value={values[field.name] ?? ""}
                  onChange={onChange}
                  placeholder={field.placeholder}
                  style={{
                    width: "100%",
                    padding: "8px 10px",
                    fontSize: "13px",
                    border: "1.5px solid #e5e7eb",
                    borderRadius: "8px",
                    outline: "none",
                    boxSizing: "border-box",
                    background: "#fafafa",
                    color: "#111827",
                    transition: "border-color 0.2s",
                  }}
                  onFocus={e => e.target.style.borderColor = section.color}
                  onBlur={e => e.target.style.borderColor = "#e5e7eb"}
                />
              </div>
            ))}
          </div>
        </div>
      ))}

      <button
        type="submit"
        disabled={loading}
        style={{
          background: loading ? "#9ca3af" : "linear-gradient(135deg, #6366f1, #8b5cf6)",
          color: "white",
          border: "none",
          borderRadius: "12px",
          padding: "14px",
          fontSize: "15px",
          fontWeight: 700,
          cursor: loading ? "not-allowed" : "pointer",
          letterSpacing: "0.02em",
        }}
      >
        {loading ? "⏳ Analyzing..." : "🔬 Run All Predictions"}
      </button>
    </form>
  );
}
