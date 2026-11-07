# 🩸 Stewart Acid-Base Analysis

[![Streamlit](https://img.shields.io/badge/Streamlit-Live%20Demo-FF4B4B?logo=streamlit&logoColor=white)](https://n7fyxlln7scrqcnsbssn9w.streamlit.app/)
[![Tests](https://github.com/farukss54-bit/Stewart-Analyser-/actions/workflows/tests.yml/badge.svg)](https://github.com/farukss54-bit/Stewart-Analyser-/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue)]()

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
- 📚 **Sample Cases** — Educational cases

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

## 🖥️ React/Next.js interface (experimental)

A second front end lives next to the Streamlit app. The calculation engine (`core.py`) is shared and untouched: the web interface only displays what the engine returns and never computes clinical values itself.

- `api/` — stateless FastAPI layer (`/api/analyze`, `/api/batch`, `/api/cases`, `/api/references`, …) that calls `core.py`, `validation.py` and `services.py`
- `web/` — Next.js (App Router, TypeScript) interface: quick and advanced mode, ready cases, classic comparison, single and batch CSV, charts, references, light/dark theme, phone/tablet layout

```bash
pip install -r requirements.txt -r api/requirements.txt
cd web && npm install && cd ..

# Windows: starts API (8000) and web (3000) together
.\scripts\dev.ps1

# Any system: two terminals
uvicorn api.main:app --port 8000
cd web && npm run dev          # http://localhost:3000
```

Tests: `pytest` also covers the API; web tests are `cd web && npm test`, plus `npm run lint` and `npm run build`. CI runs both (`.github/workflows/tests.yml`). TypeScript types are generated from the API schema (`python scripts/export_openapi.py`, then `cd web && npm run api:tipleri`); CI fails if they are out of date.

The Streamlit app remains the reference implementation and the online demo. The React interface is not deployed publicly yet.

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
pytest tests/test_api.py tests/test_api_batch.py tests/test_services.py tests/test_app_bd.py -v

# Web interface
cd web && npm test

# Coverage
pytest --cov=. --cov-report=html
```

---

## 📁 File Structure

```
.
├── app.py              # Streamlit UI orchestrator
├── core.py             # Analysis engine
├── constants.py        # Clinical constants, thresholds, sample cases
├── services.py         # Framework-free helpers shared by Streamlit and the API
├── ui_components.py    # UI render functions
├── visualization.py    # Plotly charts
├── validation.py       # 3-tier validation, Na/Cl swap detection
├── logger.py           # Structured logging (no PHI)
├── api/                # FastAPI layer for the React interface
├── web/                # Next.js (React) interface
├── scripts/            # dev.ps1 (start API + web), export_openapi.py
├── tests/
│   ├── test_api.py, test_api_batch.py  # HTTP API tests (golden tests against core)
│   ├── test_app_bd.py            # Streamlit BD-box behaviour (AppTest)
│   ├── test_cds_differential.py  # CDS differential module tests
│   ├── test_core.py              # Unit tests
│   ├── test_regression.py        # Regression tests
│   ├── test_services.py          # Shared service functions
│   ├── test_ui_imports.py        # UI import smoke tests
│   └── test_validation.py        # Edge case tests
├── requirements.txt    # Dependencies (Streamlit app)
├── Dockerfile          # Production container (Streamlit)
├── docs/
│   ├── AGENTS.md       # Agent guide (for AI developers)
│   └── BE_FORMUL_RAPORU.txt  # BE formula verification report
├── README.md           # This file
└── README_TR.md        # Turkish version
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

- **Stewart PA.** Modern quantitative acid-base chemistry. *Can J Physiol Pharmacol.* 1983;61(12):1444-61. PMID 6423247
- **Figge J, Mydosh T, Fencl V.** Serum proteins and acid-base equilibria: a follow-up. *J Lab Clin Med.* 1992;120(5):713-9. PMID 1431499
- **Fencl V, Jabor A, Kazda A, Figge J.** Diagnosis of metabolic acid-base disturbances in critically ill patients. *Am J Respir Crit Care Med.* 2000;162(6):2246-51. PMID 11112147
- **Morgan TJ.** The Stewart approach: one clinician's perspective. *Clin Biochem Rev.* 2009;30(2):41-54. PMID 19565024
- **Kellum JA.** Disorders of acid-base balance. *Crit Care Med.* 2007;35(11):2630-6. PMID 17893626
- **Berend K, de Vries APJ, Gans ROB.** Physiological approach to assessment of acid-base disturbances. *N Engl J Med.* 2014;371(15):1434-45. PMID 25295502
- **Story DA.** Stewart acid-base: a simplified bedside approach. *Anesth Analg.* 2016;123(2):511-5. PMID 27140683

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Run tests: `pytest -v` (all tests must pass)
4. Submit a pull request

Read the AGENTS.md file to learn about project rules, architecture, and common pitfalls.

---

## ⚕️ Legal Disclaimer

This application is **for educational purposes only** and describes physiological mechanisms. It does not diagnose or recommend treatment. All clinical decisions require expert physician evaluation.

---

## 📜 License

MIT License

---

*🇹🇷 [Türkçe versiyon → README_TR.md](README_TR.md)*
