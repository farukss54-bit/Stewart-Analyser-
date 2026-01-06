# app.py
# Stewart Asit-Baz Analizi - Streamlit UI Orchestrator
# v3.2 - Modular Architecture
# UI components are imported from ui_components.py

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# === CORE IMPORTS ===
from core import (
    StewartInput, analyze_stewart, output_to_dict, dict_to_input,
    calculate_hco3, interpret_sid_direction
)

# === CONSTANTS ===
from constants import (
    PH_MIN, PH_MAX, PCO2_MIN, PCO2_MAX,
    NA_MIN, NA_MAX, CL_MIN, CL_MAX, K_MIN, K_MAX,
    CA_MIN, CA_MAX, CA_NORMAL, MG_MIN, MG_MAX, MG_NORMAL,
    LACTATE_MIN, LACTATE_MAX,
    ALBUMIN_MIN_GL, ALBUMIN_MAX_GL, ALBUMIN_NORMAL_GL,
    ALBUMIN_MIN_GDL, ALBUMIN_MAX_GDL, ALBUMIN_NORMAL_GDL,
    PO4_MIN, PO4_MAX, PO4_NORMAL,
    BE_MIN, BE_MAX,
    UI_TEXTS, SAMPLE_CASES, REFERENCES
)

# === UI COMPONENTS ===
from ui_components import (
    render_headline,
    render_basic_values,
    render_contribution_breakdown,
    render_sid_table,
    render_stewart_params,
    render_anion_gap,
    render_compensation,
    render_classic_comparison,
    render_cds_notes,
    render_soft_warnings,
    render_warnings,
    get_case_value,
    render_footer
)

# === VISUALIZATION ===
from visualization import render_visualization_section

# === LOGGING ===
from logger import log_user_action, log_analysis_error


# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(page_title="Stewart Asit-Baz Analizi", page_icon="🩸", layout="wide")

# === HEADER ===
st.title(UI_TEXTS["app_title"])
st.markdown(f"*{UI_TEXTS['app_subtitle']}*")

# Landing description
with st.expander("ℹ️ Bu araç hakkında", expanded=False):
    st.markdown(UI_TEXTS["landing_description"])

# Disclaimer
st.caption(f"⚕️ {UI_TEXTS['disclaimer_short']}")


# =============================================================================
# SIDEBAR
# =============================================================================

st.sidebar.header("⚙️ Ayarlar")
mod = st.sidebar.radio(
    "Hesaplama Modu", 
    ["Hızlı (Klinik)", "Gelişmiş"],
    help="Hızlı: Fencl-derived residual\nGelişmiş: SIG = SIDa - SIDe"
)

st.sidebar.divider()

# === SAMPLE CASES ===
st.sidebar.header("📚 Hazır Vakalar")
selected_case = st.sidebar.selectbox(
    "Örnek vaka seç",
    ["-- Seçiniz --"] + list(SAMPLE_CASES.keys()),
    format_func=lambda x: SAMPLE_CASES[x]["name"] if x in SAMPLE_CASES else x
)

if selected_case != "-- Seçiniz --":
    case = SAMPLE_CASES[selected_case]
    st.sidebar.info(f"**{case['name']}**\n\n{case['description']}")
    st.sidebar.caption(f"💡 {case['teaching_point']}")
    if st.sidebar.button("🔄 Değerleri Yükle", use_container_width=True):
        for key, val in case["values"].items():
            st.session_state[f"case_{key}"] = val
        log_user_action("load_sample_case", {"case": selected_case})
        st.rerun()

st.sidebar.divider()
batch_mode = st.sidebar.checkbox("📊 Batch Modu (CSV)")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_download_csv(inp, out):
    """Create downloadable CSV from single analysis"""
    data = output_to_dict(inp, out)
    df = pd.DataFrame([data])
    return df.to_csv(index=False).encode("utf-8")


def process_batch(df, mode):
    """Process batch CSV data"""
    results = []
    errors = []
    
    for idx, row in df.iterrows():
        try:
            inp = dict_to_input(row.to_dict())
            out, val = analyze_stewart(inp, mode)
            
            if val.is_valid:
                result = output_to_dict(inp, out)
                result["row"] = idx + 1
                result["status"] = "OK"
                results.append(result)
            else:
                errors.append({"row": idx + 1, "errors": "; ".join(val.errors)})
        except Exception as e:
            errors.append({"row": idx + 1, "errors": str(e)})
            log_analysis_error("batch_row_failed", {"row": idx, "error": str(e)})
    
    return results, errors


# =============================================================================
# BATCH MODE
# =============================================================================

if batch_mode:
    st.header("📊 Batch Analiz")
    
    # Sample CSV download
    sample_csv = """ph,pco2,na,cl,k,lactate,albumin_gl,be
7.40,40,140,102,4.0,1.0,40,0
7.30,30,138,108,4.5,3.0,35,-6
7.25,25,136,100,5.0,8.0,28,-12"""
    
    st.download_button(
        "📥 Örnek CSV İndir",
        sample_csv,
        "sample_stewart.csv",
        "text/csv",
        help="Bu formatı kullanarak kendi verilerinizi hazırlayın"
    )
    
    uploaded = st.file_uploader("CSV dosyası yükle", type=["csv"])
    
    if uploaded:
        try:
            df = pd.read_csv(uploaded)
            st.success(f"✅ {len(df)} satır yüklendi")
            st.dataframe(df.head())
            
            if st.button("🔬 Toplu Analiz Yap", type="primary"):
                log_user_action("batch_start", {"rows": len(df)})
                
                mode_key = "quick" if mod == "Hızlı (Klinik)" else "advanced"
                
                with st.spinner("Analiz ediliyor..."):
                    results, errors = process_batch(df, mode_key)
                
                if results:
                    st.success(f"✅ {len(results)} başarılı analiz")
                    result_df = pd.DataFrame(results)
                    st.dataframe(result_df)
                    
                    csv = result_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📥 Sonuçları İndir",
                        csv,
                        f"stewart_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        "text/csv"
                    )
                
                if errors:
                    st.error(f"❌ {len(errors)} hatalı satır")
                    for e in errors:
                        st.caption(f"Satır {e['row']}: {e['errors']}")
                
                log_user_action("batch_complete", {"success": len(results), "errors": len(errors)})
                
        except Exception as e:
            st.error(f"CSV okuma hatası: {e}")
            log_analysis_error("csv_parse_error", {"error": str(e)})


# =============================================================================
# QUICK MODE
# =============================================================================

elif mod == "Hızlı (Klinik)":
    st.header("🩸 Hızlı Analiz")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Kan Gazı")
        ph = st.number_input("pH", PH_MIN, PH_MAX, get_case_value("ph", 7.40), 0.01, key="quick_ph")
        pco2 = st.number_input("pCO₂ (mmHg)", PCO2_MIN, PCO2_MAX, get_case_value("pco2", 40.0), 0.1, key="quick_pco2")
        
        st.markdown("---")
        be_col1, be_col2 = st.columns([3, 1])
        with be_col1:
            be_input = st.number_input("BE / BD", BE_MIN, BE_MAX, get_case_value("be", 0.0), 0.1, key="quick_be")
        with be_col2:
            is_bd = st.checkbox("BD", help="Base Deficit olarak girdiyseniz işaretleyin")
    
    with col2:
        st.subheader("Elektrolitler")
        na = st.number_input("Na⁺ (mmol/L)", NA_MIN, NA_MAX, get_case_value("na", 140.0), 0.1, key="quick_na")
        cl = st.number_input("Cl⁻ (mmol/L)", CL_MIN, CL_MAX, get_case_value("cl", 100.0), 0.1, key="quick_cl")
        
        lac_var = st.checkbox("Laktat var", get_case_value("lactate", None) is not None)
        lactate = st.number_input("Laktat (mmol/L)", LACTATE_MIN, LACTATE_MAX, 
                                 get_case_value("lactate", 1.0), 0.1, key="quick_lac") if lac_var else None
        
        alb_var = st.checkbox("Albümin var", get_case_value("albumin_gl", None) is not None)
        if alb_var:
            alb_unit = st.selectbox("Birim", ["g/L", "g/dL"], key="quick_alb_unit")
            if alb_unit == "g/L":
                alb = st.number_input("Albümin (g/L)", ALBUMIN_MIN_GL, ALBUMIN_MAX_GL, 
                                     get_case_value("albumin_gl", ALBUMIN_NORMAL_GL), 0.1, key="quick_alb")
                albumin_gl = alb
            else:
                alb = st.number_input("Albümin (g/dL)", ALBUMIN_MIN_GDL, ALBUMIN_MAX_GDL, 
                                     ALBUMIN_NORMAL_GDL, 0.1, key="quick_alb_gdl")
                albumin_gl = alb * 10
        else:
            albumin_gl = None
        
        st.markdown("---")
        hco3_man = st.checkbox("HCO₃⁻ manuel gir")
        hco3 = st.number_input("HCO₃⁻", 5.0, 50.0, 24.0, 0.1, key="quick_hco3") if hco3_man else None
        if not hco3_man:
            st.caption(f"HCO₃⁻ hesaplanacak: ~{calculate_hco3(ph, pco2):.1f}")
    
    # === ANALYZE BUTTON ===
    if st.button("🔬 Analiz Et", type="primary", use_container_width=True):
        inp = StewartInput(
            ph=ph, pco2=pco2, na=na, cl=cl, hco3=hco3, be=be_input,
            is_be_base_deficit=is_bd, lactate=lactate, albumin_gl=albumin_gl
        )
        out, val = analyze_stewart(inp, "quick")
        
        if not val.is_valid:
            for e in val.errors:
                st.error(f"❌ {e}")
            st.stop()
        
        log_user_action("quick_analysis", {"ph": ph, "pco2": pco2})
        
        st.divider()
        
        # === RESULTS ===
        
        # Headline
        if out.headline:
            render_headline(out.headline, out.mechanism_analysis)
        
        st.divider()
        
        # Warnings
        render_warnings(out.warnings)
        
        # Basic values
        render_basic_values(ph, pco2, out.hco3_used, out.be_used, out.hco3_source, out.be_source)
        
        st.divider()
        
        # Contribution breakdown
        if out.contribution:
            render_contribution_breakdown(out.contribution, out.mechanism_analysis)
        
        st.divider()
        
        # SID table
        st.subheader("📐 SID Değerleri")
        render_sid_table(out, interpret_sid_direction)
        
        # Compensation
        render_compensation(out)
        
        # Classic comparison
        if out.classic_comparison:
            render_classic_comparison(out.classic_comparison)
        
        # CDS notes
        if out.cds_notes:
            render_cds_notes(out.cds_notes)
        
        # Soft warnings
        render_soft_warnings(out.soft_warnings)
        
        # Download
        st.divider()
        csv_data = create_download_csv(inp, out)
        st.download_button("📥 Sonucu İndir (CSV)", csv_data, "stewart_result.csv", "text/csv")


# =============================================================================
# ADVANCED MODE
# =============================================================================

else:  # Gelişmiş mod
    st.header("🔬 Gelişmiş Analiz")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Kan Gazı")
        ph = st.number_input("pH", PH_MIN, PH_MAX, get_case_value("ph", 7.40), 0.01, key="adv_ph")
        pco2 = st.number_input("pCO₂", PCO2_MIN, PCO2_MAX, get_case_value("pco2", 40.0), 0.1, key="adv_pco2")
        
        st.markdown("---")
        be_col1, be_col2 = st.columns([3, 1])
        with be_col1:
            be_input = st.number_input("BE / BD", BE_MIN, BE_MAX, get_case_value("be", 0.0), 0.1, key="adv_be")
        with be_col2:
            is_bd = st.checkbox("BD", key="adv_bd", help="Base Deficit")
        
        hco3_man = st.checkbox("HCO₃⁻ manuel", key="adv_hco3_check")
        hco3 = st.number_input("HCO₃⁻", 5.0, 50.0, 24.0, 0.1, key="adv_hco3") if hco3_man else None
    
    with col2:
        st.subheader("Elektrolitler")
        na = st.number_input("Na⁺", NA_MIN, NA_MAX, get_case_value("na", 140.0), 0.1, key="adv_na")
        cl = st.number_input("Cl⁻", CL_MIN, CL_MAX, get_case_value("cl", 100.0), 0.1, key="adv_cl")
        k = st.number_input("K⁺", K_MIN, K_MAX, get_case_value("k", 4.0), 0.1, key="adv_k")
        lactate = st.number_input("Laktat", LACTATE_MIN, LACTATE_MAX, 
                                  get_case_value("lactate", 1.0), 0.1, key="adv_lac")
    
    with col3:
        st.subheader("İleri Parametreler")
        ca = st.number_input("Ca²⁺ (iyonize)", CA_MIN, CA_MAX, CA_NORMAL, 0.01, key="adv_ca",
                            help="İyonize kalsiyum (mmol/L)")
        mg = st.number_input("Mg²⁺", MG_MIN, MG_MAX, MG_NORMAL, 0.01, key="adv_mg")
        
        alb_unit = st.selectbox("Albümin birimi", ["g/L", "g/dL"], key="adv_alb_unit")
        if alb_unit == "g/L":
            albumin_gl = st.number_input("Albümin", ALBUMIN_MIN_GL, ALBUMIN_MAX_GL,
                                        get_case_value("albumin_gl", ALBUMIN_NORMAL_GL), 0.1, key="adv_alb")
        else:
            alb_gdl = st.number_input("Albümin", ALBUMIN_MIN_GDL, ALBUMIN_MAX_GDL,
                                     ALBUMIN_NORMAL_GDL, 0.1, key="adv_alb_gdl")
            albumin_gl = alb_gdl * 10
        
        po4 = st.number_input("Fosfat", PO4_MIN, PO4_MAX, PO4_NORMAL, 0.1, key="adv_po4",
                             help="mmol/L")
    
    # === ANALYZE BUTTON ===
    if st.button("🔬 Gelişmiş Analiz", type="primary", use_container_width=True):
        inp = StewartInput(
            ph=ph, pco2=pco2, na=na, cl=cl, k=k,
            ca=ca, mg=mg, lactate=lactate,
            albumin_gl=albumin_gl, po4=po4,
            hco3=hco3, be=be_input, is_be_base_deficit=is_bd
        )
        out, val = analyze_stewart(inp, "advanced")
        
        if not val.is_valid:
            for e in val.errors:
                st.error(f"❌ {e}")
            st.stop()
        
        log_user_action("advanced_analysis", {"ph": ph, "pco2": pco2})
        
        st.divider()
        
        # === RESULTS ===
        
        # Headline
        if out.headline:
            render_headline(out.headline, out.mechanism_analysis)
        
        st.divider()
        
        # Warnings
        render_warnings(out.warnings)
        
        # Basic values
        render_basic_values(ph, pco2, out.hco3_used, out.be_used, out.hco3_source, out.be_source)
        
        st.divider()
        
        # Contribution breakdown
        if out.contribution:
            render_contribution_breakdown(out.contribution, out.mechanism_analysis)
        
        st.divider()
        
        # SID table
        st.subheader("📐 SID Değerleri")
        render_sid_table(out, interpret_sid_direction)
        
        # Stewart parameters (advanced only)
        render_stewart_params(out, None)
        
        # Anion gap (advanced only)
        render_anion_gap(out)
        
        # Compensation
        render_compensation(out)
        
        # Visualization (advanced only)
        with st.expander("📈 Görselleştirme", expanded=False):
            render_visualization_section(inp, out)
        
        # Classic comparison
        if out.classic_comparison:
            render_classic_comparison(out.classic_comparison)
        
        # CDS notes
        if out.cds_notes:
            render_cds_notes(out.cds_notes)
        
        # Soft warnings
        render_soft_warnings(out.soft_warnings)
        
        # Download
        st.divider()
        csv_data = create_download_csv(inp, out)
        st.download_button("📥 Sonucu İndir (CSV)", csv_data, "stewart_result.csv", "text/csv")


# =============================================================================
# FOOTER
# =============================================================================

render_footer(REFERENCES)
