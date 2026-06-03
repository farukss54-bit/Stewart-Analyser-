# app.py
# Stewart Asit-Baz Analizi - Streamlit UI Orchestrator
# v3.4 - Derived Value Management & Sign Error Detection
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
    calculate_hco3, calculate_be, interpret_sid_direction,
    normalize_input, stewart_input_from_normalized
)
from validation import validate_csv_row

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
    PH_NORMAL_LOW, PH_NORMAL_HIGH,
    UI_TEXTS, SAMPLE_CASES, REFERENCES, ACKNOWLEDGMENTS
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
from logger import log_user_action, log_analysis_error, log_batch_progress


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

# =============================================================================
# SESSION STATE DEFAULTS
# =============================================================================
for prefix in ["quick", "adv"]:
    st.session_state.setdefault(f"{prefix}_ph", 7.40)
    st.session_state.setdefault(f"{prefix}_pco2", 40.0)
    st.session_state.setdefault(f"{prefix}_na", 140.0)
    st.session_state.setdefault(f"{prefix}_cl", 100.0)
    st.session_state.setdefault(f"{prefix}_k", 4.0)
    st.session_state.setdefault(f"{prefix}_lac", 1.0)
    st.session_state.setdefault(f"{prefix}_ca", CA_NORMAL)
    st.session_state.setdefault(f"{prefix}_mg", MG_NORMAL)
    st.session_state.setdefault(f"{prefix}_alb", ALBUMIN_NORMAL_GL)
    st.session_state.setdefault(f"{prefix}_alb_gdl", ALBUMIN_NORMAL_GDL)
    st.session_state.setdefault(f"{prefix}_po4", PO4_NORMAL)
    st.session_state.setdefault(f"{prefix}_alb_unit", "g/L")

st.session_state.setdefault("quick_lac_var", False)
st.session_state.setdefault("quick_alb_var", False)

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
        values = case["values"]
        # Temel parametreler (hem quick hem advanced)
        for key in ["ph", "pco2", "na", "cl"]:
            if key in values:
                val = float(values[key])
                st.session_state[f"quick_{key}"] = val
                st.session_state[f"adv_{key}"] = val
        if "k" in values:
            val = float(values["k"])
            st.session_state["quick_k"] = val
            st.session_state["adv_k"] = val
        if "lactate" in values:
            val = float(values["lactate"])
            st.session_state["quick_lac"] = val
            st.session_state["adv_lac"] = val
            st.session_state["quick_lac_var"] = True
        else:
            st.session_state["quick_lac_var"] = False
        if "albumin_gl" in values:
            alb = float(values["albumin_gl"])
            st.session_state["quick_alb"] = alb
            st.session_state["adv_alb"] = alb
            st.session_state["quick_alb_var"] = True
            if alb > 10:
                st.session_state["quick_alb_unit"] = "g/L"
                st.session_state["adv_alb_unit"] = "g/L"
            else:
                st.session_state["quick_alb_unit"] = "g/dL"
                st.session_state["adv_alb_unit"] = "g/dL"
        else:
            st.session_state["quick_alb_var"] = False
        if "be" in values:
            st.session_state["quick_be_manual"] = float(values["be"])
            st.session_state["adv_be_manual"] = float(values["be"])
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
    total = max(len(df), 1)

    for idx, row in df.iterrows():
        _progress = min((idx + 1) / total, 1.0)
        log_batch_progress(idx + 1, total, "processing")

        row_dict = row.to_dict()
        validation = validate_csv_row(row_dict, idx)

        if not validation.is_valid:
            error_msg = "; ".join(validation.errors)
            results.append({"row": idx + 1, "status": "ERROR", "errors": error_msg})
            errors.append({"row": idx + 1, "errors": error_msg})
            continue

        try:
            inp = stewart_input_from_normalized(validation.normalized_values)
            out, val = analyze_stewart(inp, mode)

            if val.is_valid:
                result = output_to_dict(inp, out)
                result.update({
                    "row": idx + 1,
                    "status": "OK",
                    "warnings": "|".join(val.warnings),
                })
                results.append(result)
            else:
                error_text = "; ".join(val.errors)
                results.append({"row": idx + 1, "status": "ERROR", "errors": error_text})
                errors.append({"row": idx + 1, "errors": error_text})
        except Exception as e:
            err = str(e)
            results.append({"row": idx + 1, "status": "ERROR", "errors": err})
            errors.append({"row": idx + 1, "errors": err})
            log_analysis_error("batch_row_failed", {"row": idx, "error": err})

    log_batch_progress(total, total, "complete")
    return results, errors


def check_be_sign_error(ph: float, be: float) -> dict:
    """
    BE işaret hatası kontrolü.
    
    Returns:
        dict with keys:
        - has_error: bool
        - message: str
        - suggested_be: float (işaret düzeltilmiş)
    """
    # pH asidemi gösteriyor ama BE pozitif (alkaloz)
    if ph < PH_NORMAL_LOW and be > 2:
        return {
            "has_error": True,
            "message": f"⚠️ pH ({ph:.2f}) asidemi gösteriyor ama BE ({be:+.1f}) pozitif. İşaret hatası olabilir!",
            "suggested_be": -be
        }
    
    # pH alkalemi gösteriyor ama BE negatif (asidoz)
    if ph > PH_NORMAL_HIGH and be < -2:
        return {
            "has_error": True,
            "message": f"⚠️ pH ({ph:.2f}) alkalemi gösteriyor ama BE ({be:+.1f}) negatif. İşaret hatası olabilir!",
            "suggested_be": -be
        }
    
    return {"has_error": False, "message": "", "suggested_be": be}


def render_derived_values_section(ph: float, pco2: float, mode_prefix: str):
    """
    Türetilmiş değerler (HCO₃ ve BE) için ortak UI bileşeni.
    Her iki modda da aynı mantığı kullanır.
    
    Returns:
        tuple: (hco3_to_use, be_to_use, is_be_base_deficit, should_stop)
    """
    # Hesaplanan değerler
    hco3_calc = calculate_hco3(ph, pco2)
    be_calc = calculate_be(ph, hco3_calc)
    
    st.markdown("---")
    st.markdown("##### 📊 Türetilmiş Değerler")
    
    # Hesaplanan değerleri göster
    calc_col1, calc_col2 = st.columns(2)
    with calc_col1:
        st.metric("HCO₃⁻ (hesaplanan)", f"{hco3_calc:.1f} mEq/L")
    with calc_col2:
        st.metric("BE (hesaplanan)", f"{be_calc:+.1f} mEq/L")
    
    # Doğrulama modu checkbox
    verify_mode = st.checkbox(
        "🔍 Cihaz değerlerini doğrula",
        help="Kan gazı cihazınızın gösterdiği HCO₃ veya BE değerini girerek tutarlılığı kontrol edebilirsiniz.",
        key=f"{mode_prefix}_verify_mode"
    )
    
    # Varsayılan değerler
    hco3_to_use = None  # None = hesaplansın
    be_to_use = None    # None = hesaplansın
    is_bd = False
    should_stop = False
    
    if verify_mode:
        st.info("💡 Cihaz değerini girmek tutarlılık kontrolü sağlar. Fark >2 mEq/L ise uyarı alırsınız.")
        
        verify_col1, verify_col2 = st.columns(2)
        
        with verify_col1:
            hco3_verify = st.checkbox("HCO₃⁻ doğrula", key=f"{mode_prefix}_hco3_verify")
            if hco3_verify:
                hco3_manual = st.number_input(
                    "Cihaz HCO₃⁻ (mEq/L)", 
                    5.0, 50.0, hco3_calc, 0.1,
                    key=f"{mode_prefix}_hco3_manual"
                )
                hco3_diff = abs(hco3_manual - hco3_calc)
                
                if hco3_diff > 2:
                    st.error(f"🚨 HCO₃ farkı: {hco3_diff:.1f} mEq/L (hesaplanan: {hco3_calc:.1f})")
                    st.warning("Bu fark önemli. Örnek kalitesi, cihaz kalibrasyonu veya giriş hatası olabilir.")
                else:
                    st.success(f"✅ HCO₃ tutarlı (fark: {hco3_diff:.1f} mEq/L)")
                
                hco3_to_use = hco3_manual
        
        with verify_col2:
            be_verify = st.checkbox("BE doğrula", key=f"{mode_prefix}_be_verify")
            if be_verify:
                be_col1, be_col2 = st.columns([3, 1])
                with be_col1:
                    be_manual = st.number_input(
                        "Cihaz BE (mEq/L)", 
                        BE_MIN, BE_MAX, be_calc, 0.1,
                        key=f"{mode_prefix}_be_manual"
                    )
                with be_col2:
                    is_bd = st.checkbox("BD", key=f"{mode_prefix}_is_bd", help="Base Deficit olarak girdiyseniz işaretleyin")
                
                # BD ise işareti çevir
                be_effective = -be_manual if is_bd else be_manual
                be_diff = abs(be_effective - be_calc)
                
                # İşaret hatası kontrolü
                sign_check = check_be_sign_error(ph, be_effective)
                
                if sign_check["has_error"]:
                    st.error(sign_check["message"])
                    
                    # Net yönlendirme
                    if be_manual > 0:
                        st.info(f"💡 **Düzeltmek için:** Değeri **{-be_manual:.1f}** olarak değiştirin veya **BD** kutusunu işaretleyin.")
                    else:
                        st.info(f"💡 **Düzeltmek için:** Değeri **{-be_manual:.1f}** olarak değiştirin.")
                    
                    should_stop = True
                
                elif be_diff > 2:
                    st.error(f"🚨 BE farkı: {be_diff:.1f} mEq/L (hesaplanan: {be_calc:+.1f})")
                    st.warning("Bu fark önemli. Örnek kalitesi, cihaz kalibrasyonu veya giriş hatası olabilir.")
                else:
                    st.success(f"✅ BE tutarlı (fark: {be_diff:.1f} mEq/L)")
                
                be_to_use = be_effective
    
    return hco3_to_use, be_to_use, is_bd, should_stop


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
        st.subheader("Kan Gazı (Ölçülen)")
        ph = st.number_input("pH", PH_MIN, PH_MAX, step=0.01, key="quick_ph")
        pco2 = st.number_input("pCO₂ (mmHg)", PCO2_MIN, PCO2_MAX, step=0.1, key="quick_pco2")
        
        # Türetilmiş değerler bölümü
        hco3, be_input, is_bd, should_stop = render_derived_values_section(ph, pco2, "quick")
    
    with col2:
        st.subheader("Elektrolitler")
        na = st.number_input("Na⁺ (mmol/L)", NA_MIN, NA_MAX, step=0.1, key="quick_na")
        cl = st.number_input("Cl⁻ (mmol/L)", CL_MIN, CL_MAX, step=0.1, key="quick_cl")
        
        lac_var = st.checkbox("Laktat var", key="quick_lac_var")
        lactate = st.number_input("Laktat (mmol/L)", LACTATE_MIN, LACTATE_MAX, step=0.1, key="quick_lac") if lac_var else None
        
        alb_var = st.checkbox("Albümin var", key="quick_alb_var")
        if alb_var:
            alb_unit = st.selectbox("Birim", ["g/L", "g/dL"], key="quick_alb_unit")
            if alb_unit == "g/L":
                alb = st.number_input("Albümin (g/L)", ALBUMIN_MIN_GL, ALBUMIN_MAX_GL, step=0.1, key="quick_alb")
                albumin_gl = alb
            else:
                alb = st.number_input("Albümin (g/dL)", ALBUMIN_MIN_GDL, ALBUMIN_MAX_GDL, step=0.1, key="quick_alb_gdl")
                albumin_gl = alb * 10
        else:
            albumin_gl = None
    
    # === ANALYZE BUTTON ===
    analyze_disabled = should_stop
    
    if should_stop:
        st.error("🚫 İşaret hatası düzeltilmeden analiz yapılamaz. Lütfen yukarıdaki uyarıyı kontrol edin.")
    
    if st.button("🔬 Analiz Et", type="primary", use_container_width=True, disabled=analyze_disabled):
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
        st.subheader("🔍 SID Değerleri")
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
        st.subheader("Kan Gazı (Ölçülen)")
        ph = st.number_input("pH", PH_MIN, PH_MAX, step=0.01, key="adv_ph")
        pco2 = st.number_input("pCO₂", PCO2_MIN, PCO2_MAX, step=0.1, key="adv_pco2")
        
        # Türetilmiş değerler bölümü
        hco3, be_input, is_bd, should_stop = render_derived_values_section(ph, pco2, "adv")
    
    with col2:
        st.subheader("Elektrolitler")
        na = st.number_input("Na⁺", NA_MIN, NA_MAX, step=0.1, key="adv_na")
        cl = st.number_input("Cl⁻", CL_MIN, CL_MAX, step=0.1, key="adv_cl")
        k = st.number_input("K⁺", K_MIN, K_MAX, step=0.1, key="adv_k")
        lactate = st.number_input("Laktat", LACTATE_MIN, LACTATE_MAX, step=0.1, key="adv_lac")
    
    with col3:
        st.subheader("İleri Parametreler")
        ca = st.number_input("Ca²⁺ (iyonize)", CA_MIN, CA_MAX, step=0.01, key="adv_ca",
                            help="İyonize kalsiyum (mmol/L)")
        mg = st.number_input("Mg²⁺", MG_MIN, MG_MAX, step=0.01, key="adv_mg")
        
        alb_unit = st.selectbox("Albümin birimi", ["g/L", "g/dL"], key="adv_alb_unit")
        if alb_unit == "g/L":
            albumin_gl = st.number_input("Albümin", ALBUMIN_MIN_GL, ALBUMIN_MAX_GL, step=0.1, key="adv_alb")
        else:
            alb_gdl = st.number_input("Albümin", ALBUMIN_MIN_GDL, ALBUMIN_MAX_GDL, step=0.1, key="adv_alb_gdl")
            albumin_gl = alb_gdl * 10
        
        po4 = st.number_input("Fosfat", PO4_MIN, PO4_MAX, step=0.1, key="adv_po4",
                             help="mmol/L")
    
    # === ANALYZE BUTTON ===
    analyze_disabled = should_stop
    
    if should_stop:
        st.error("🚫 İşaret hatası düzeltilmeden analiz yapılamaz. Lütfen yukarıdaki uyarıyı kontrol edin.")
    
    if st.button("🔬 Gelişmiş Analiz", type="primary", use_container_width=True, disabled=analyze_disabled):
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
        st.subheader("🔍 SID Değerleri")
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

render_footer(REFERENCES, ACKNOWLEDGMENTS)
