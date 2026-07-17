# 🩸 Stewart Acid-Base Analysis

[![Streamlit](https://img.shields.io/badge/Streamlit-Live%20Demo-FF4B4B?logo=streamlit&logoColor=white)](https://n7fyxlln7scrqcnsbssn9w.streamlit.app/)
[![Tests](https://img.shields.io/badge/tests-156%20passed-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()

An **education-focused web application** for blood gas evaluation using the **Stewart-Fencl physicochemical approach**.

> ⚕️ **This tool describes physiological mechanisms; it is not a diagnostic or therapeutic recommendation.** It is intended for educational purposes. All clinical decisions require expert physician evaluation.

---

## 🎯 What is this project?

Beyond classical acid-base analysis (Henderson-Hasselbalch, anion gap), this tool provides a **physicochemical approach** based on **Strong Ion Difference (SID)** and **weak acids (Atot)** concepts.

### Who is it for?
- 🏥 **Emergency / ICU physicians** — rapid analysis of complex acid-base disorders
- 📚 **Medical students and residents** — learning through ready-made cases with literature references
- 🔬 **Researchers** — batch CSV analysis and literature-based threshold values

### Why Stewart?
- Reveals **masked acidoses** that classical approaches miss (e.g., hypoalbuminemia + acidosis)
- Distinguishes **mixed disorders**
- Quantifies each component's contribution in **mEq/L**
- Calculates the **Strong Ion Gap (SIG)** effect

---

## 🚀 Features

### Analysis Modes
| Mode | Description |
|------|-------------|
| **Quick** | Minimum parameters (pH, pCO₂, Na, Cl). BE-based component breakdown. |
| **Advanced** | Full Stewart analysis: SIDa, SIDe, SIG, Atot. Complete mechanism analysis. |

### Input Methods
- ✏️ **Manual entry** — Quick or advanced form
- 📂 **Batch CSV** — Bulk analysis with row-by-row validation
- 📚 **Sample Cases** — Educational cases (including Akoğlu cases)

### Outputs
- 📋 **Headline** — One-sentence clinical summary
- 📊 **Basic Values** — pH, pCO₂, HCO₃, BE (emoji + arrow + color coding)
- 📈 **SID Table** — 3-tier SID (simple / basic / full)
- 🧮 **Contribution Breakdown** — Each mechanism's mEq/L and % contribution to BE
- 📉 **Visualizations** — Gamblegram, contribution bar chart, SID waterfall, pH gauge
- 💡 **CDS Notes** — Categorized (A/B/C) clinical decision support tips
- ⚖️ **Classic Comparison** — Differences between Stewart and classical approaches

---

## 🛠️ Installation

### Local Development
```bash
# Clone the repo
git clone https://github.com/farukss54-bit/Stewart-Analyser-.git
cd Stewart-Analyser-

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```
The app opens at `http://localhost:8501` by default.

### Docker
```bash
docker build -t stewart-analyzer .
docker run -p 8501:8501 stewart-analyzer
```

### VS Code / GitHub Codespaces
`.devcontainer/devcontainer.json` is included. Dependencies auto-install on open.

---

## 🧪 Testing

```bash
# All tests
pytest -v

# Specific test files
pytest tests/test_core.py -v
pytest tests/test_validation.py -v
pytest tests/test_regression.py -v
pytest tests/test_cds_differential.py -v
pytest tests/test_ui_imports.py -v

# Coverage
pytest --cov=. --cov-report=html
```

---

## 📁 File Structure

```
.
├── app.py              # Streamlit UI orchestrator
├── core.py             # Analysis engine (~1,700 lines)
├── constants.py        # Clinical constants, thresholds, sample cases (~1,100 lines)
├── ui_components.py    # UI render functions
├── visualization.py    # Plotly charts
├── validation.py       # 3-tier validation, Na/Cl swap detection
├── logger.py           # Structured logging (no PHI)
├── tests/
│   ├── test_cds_differential.py  # CDS differential module tests
│   ├── test_core.py              # Unit tests
│   ├── test_regression.py        # Regression tests
│   ├── test_sample_cases.py      # Sample case integrity tests
│   ├── test_ui_imports.py        # UI import smoke tests
│   └── test_validation.py        # Edge case tests
├── requirements.txt    # Dependencies
├── Dockerfile          # Production container
├── docs/
│   ├── AGENTS.md       # Agent guide (for AI developers)
│   └── BE_FORMUL_RAPORU.txt  # BE formula verification report
└── README_EN.md        # This file
```

---

## 📖 Usage

### Quick Mode
1. Select "Quick (Clinical)" from sidebar
2. Enter pH, pCO₂, Na, Cl
3. Optional: K, lactate, albumin
4. Click "Analyze"

### Advanced Mode
1. Select "Advanced" from sidebar
2. Enter all parameters (including Ca, Mg, phosphate)
3. View SIG calculation and full mechanism analysis

### Sample Cases
1. Select a case from "📚 Sample Cases" in sidebar
2. Click "🔄 Load Values" button
3. Review educational notes and classic comparison

### Batch Analysis
1. Upload a CSV file (one row per patient)
2. Automatic validation and analysis
3. Download results

---

## 🔬 Literature References

This project is based on the following literature:

- **Stewart PA.** Modern quantitative acid-base chemistry. *Can J Physiol Pharmacol.* 1983
- **Figge J, Mydosh T, Fencl V.** Serum proteins and acid-base equilibria. *J Lab Clin Med.* 1991
- **Fencl V, Jabor A, Kazda A, Figge J.** Diagnosis of metabolic acid-base disturbances. *Am J Respir Crit Care.* 2000
- **Morgan TJ.** The Stewart approach. *Crit Care Clin.* 2009
- **Kellum JA.** Disorders of acid-base balance. *Crit Care Med.* 2009
- **Berend K, et al.** Physiological approach to assessment of acid-base disturbances. *NEJM.* 2014
- **Story DA.** Stewart acid-base: A simplified bedside approach. *Anesth Analg.* 2016

**Clinical case contributions:** Assoc. Prof. Haldun Akoğlu — Marmara University Emergency Medicine Dept.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Run tests: `pytest -v` (all 156 tests must pass)
4. Submit a pull request

Read the AGENTS.md file to learn about project rules, architecture, and common pitfalls.

---

## ⚕️ Legal Disclaimer

This application is **for educational purposes only** and describes physiological mechanisms. It does not diagnose or recommend treatment. All clinical decisions require expert physician evaluation.

---

## 📜 License

MIT License

---

*🇹🇷 [Türkçe versiyon → README.md](README.md)*
