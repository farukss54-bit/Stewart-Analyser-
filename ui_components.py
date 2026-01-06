# ui_components.py
# Stewart Asit-Baz Analizi - UI Components v3.2
# Extracted from app.py for cleaner architecture

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from constants import (
    SID_NORMAL_SIMPLE, SID_NORMAL_BASIC, SID_NORMAL_FULL,
    PARAM_DEFINITIONS, UI_TEXTS, SAMPLE_CASES
)


# =============================================================================
# COLOR CODING & INDICATORS
# =============================================================================

def get_emoji(level: str) -> str:
    """Generic status emoji"""
    return {"normal": "🟢", "info": "🔵", "warning": "🟡", "critical": "🔴"}.get(level, "⚪")


def get_acidbase_indicator(direction: str) -> str:
    """
    Acid-base status visual indicator
    direction: "acidosis", "alkalosis", "normal", "resp_acidosis", "resp_alkalosis"
    """
    indicators = {
        "acidosis": "🔴↓",      # Red down - acidosis
        "alkalosis": "🔵↑",     # Blue up - alkalosis
        "resp_acidosis": "🔴↑", # Red up - high pCO2
        "resp_alkalosis": "🔵↓", # Blue down - low pCO2
        "normal": "🟢",
    }
    return indicators.get(direction, "⚪")


# =============================================================================
# VALUE FORMATTERS WITH COLOR CODING
# =============================================================================

def format_ph_display(ph: float) -> Tuple[str, str, str]:
    """pH display with color coding"""
    if ph < 7.35:
        severity = "şiddetli " if ph < 7.20 else ""
        return get_acidbase_indicator("acidosis"), f"{severity}Asidemi", "acidosis"
    elif ph > 7.45:
        severity = "şiddetli " if ph > 7.55 else ""
        return get_acidbase_indicator("alkalosis"), f"{severity}Alkalemi", "alkalosis"
    return get_acidbase_indicator("normal"), "Normal", "normal"


def format_pco2_display(pco2: float) -> Tuple[str, str, str]:
    """pCO2 display with color coding"""
    if pco2 > 45:
        return get_acidbase_indicator("resp_acidosis"), "Respiratuvar asidoz", "acidosis"
    elif pco2 < 35:
        return get_acidbase_indicator("resp_alkalosis"), "Respiratuvar alkaloz", "alkalosis"
    return get_acidbase_indicator("normal"), "Normal", "normal"


def format_be_display(be: float) -> Tuple[str, str, str]:
    """BE display with color coding"""
    if be < -2:
        severity = "şiddetli " if be < -10 else ""
        return get_acidbase_indicator("acidosis"), f"{severity}Metabolik asidoz", "acidosis"
    elif be > 2:
        severity = "şiddetli " if be > 10 else ""
        return get_acidbase_indicator("alkalosis"), f"{severity}Metabolik alkaloz", "alkalosis"
    return get_acidbase_indicator("normal"), "Normal", "normal"


def format_hco3_display(hco3: float) -> Tuple[str, str, str]:
    """HCO3 display with color coding"""
    if hco3 < 22:
        return get_acidbase_indicator("acidosis"), "Düşük", "acidosis"
    elif hco3 > 26:
        return get_acidbase_indicator("alkalosis"), "Yüksek", "alkalosis"
    return get_acidbase_indicator("normal"), "Normal", "normal"


# =============================================================================
# SECTION RENDERERS
# =============================================================================

def render_headline(headline, mechanism_analysis=None):
    """Render summary result - mechanism-based, non-diagnostic"""
    st.markdown("### 🎯 Özet Sonuç")
    
    # Dominant mechanism color
    dominant_lower = headline.dominant_mechanism.lower() if headline.dominant_mechanism else ""
    if "asidoz" in dominant_lower:
        dominant_icon = "🔴"
    elif "alkaloz" in dominant_lower:
        dominant_icon = "🔵"
    elif "normal" in dominant_lower or "yok" in dominant_lower:
        dominant_icon = "🟢"
    else:
        dominant_icon = "⚪"
    
    # Dominant mechanism
    st.markdown(f"**Dominant metabolik mekanizma:** {dominant_icon} {headline.dominant_mechanism}")
    
    # Significant mechanisms
    if headline.significant_mechanisms:
        st.markdown("**Anlamlı katkıda bulunan mekanizmalar:**")
        for sm in headline.significant_mechanisms:
            sm_icon = "🔴" if "asidoz" in sm.lower() else "🔵" if "alkaloz" in sm.lower() else "⚪"
            st.markdown(f"  • {sm_icon} {sm}")
    
    # Contributing mechanisms (collapsible)
    if headline.contributing_mechanisms:
        with st.expander("Katkıda bulunan diğer mekanizmalar"):
            for cm in headline.contributing_mechanisms:
                st.markdown(f"  • {cm}")
    
    # Respiratory status
    if headline.respiratory_status:
        resp_lower = headline.respiratory_status.lower()
        if "asidoz" in resp_lower:
            resp_icon = "🔴"
        elif "alkaloz" in resp_lower:
            resp_icon = "🔵"
        elif "uygun" in resp_lower or "normal" in resp_lower:
            resp_icon = "🟢"
        else:
            resp_icon = "⚪"
        st.markdown(f"**Solunumsal durum:** {resp_icon} {headline.respiratory_status}")
    
    # Pattern note (non-diagnostic)
    if headline.pattern_note:
        st.info(f"📋 {headline.pattern_note}")


def render_basic_values(ph: float, pco2: float, hco3_used: float, be_used: float,
                        hco3_source: str, be_source: str):
    """Render basic blood gas values with color coding"""
    st.subheader("📊 Temel Değerler")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        ph_icon, ph_text, _ = format_ph_display(ph)
        st.metric("pH", f"{ph:.2f}", f"{ph_icon} {ph_text}")
    with c2:
        pco2_icon, pco2_text, _ = format_pco2_display(pco2)
        st.metric("pCO₂", f"{pco2:.1f} mmHg", f"{pco2_icon} {pco2_text}")
    with c3:
        hco3_icon, hco3_text, _ = format_hco3_display(hco3_used)
        src = " (hes.)" if hco3_source == "calculated" else ""
        st.metric("HCO₃⁻", f"{hco3_used:.1f}", f"{hco3_icon}{src}")
    with c4:
        be_icon, be_text, _ = format_be_display(be_used)
        src = " (hes.)" if be_source == "calculated" else ""
        st.metric("BE", f"{be_used:+.1f}", f"{be_icon} {be_text}{src}")
    
    # Definition expander
    render_basic_values_definitions()


def render_basic_values_definitions():
    """Render basic values definition expander"""
    with st.expander("ℹ️ Temel kan gazı değerleri ne demek?"):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown(PARAM_DEFINITIONS["ph"]["long"])
            st.markdown("---")
            st.markdown(PARAM_DEFINITIONS["pco2"]["long"])
        with col_t2:
            st.markdown(PARAM_DEFINITIONS["hco3"]["long"])
            st.markdown("---")
            st.markdown(PARAM_DEFINITIONS["be"]["long"])


def render_contribution_breakdown(contribution, mechanism_analysis=None):
    """Render metabolic mechanism analysis - mechanism-focused, non-diagnostic"""
    st.markdown("### ⚖️ Metabolik Mekanizma Analizi")
    
    # Mechanism contribution percentages
    if mechanism_analysis and mechanism_analysis.all_mechanisms:
        st.markdown("**Mekanizma Katkı Oranları (BE'ye göre):**")
        for mc in mechanism_analysis.all_mechanisms:
            if mc.contribution_percent >= 5:
                bar_color = "🔴" if mc.direction == "acidosis" else "🔵"
                direction_text = "asidoz yönünde" if mc.direction == "acidosis" else "alkaloz yönünde"
                
                level_badge = ""
                if mc.level == "dominant":
                    level_badge = "**[DOMINANT]**"
                elif mc.level == "significant":
                    level_badge = "*[Anlamlı]*"
                
                st.markdown(f"  {bar_color} **{mc.name}:** {mc.effect_meq:+.1f} mEq/L ({mc.contribution_percent:.0f}% katkı) - {direction_text} {level_badge}")
        
        st.markdown("---")
    
    col_acid, col_alk = st.columns(2)
    
    with col_acid:
        st.markdown("**🔴 Asidoz Yönündeki Etkiler**")
        if contribution.acidosis_contributors:
            for name, val, desc in contribution.acidosis_contributors:
                st.markdown(f"• **{name}:** 🔴↓ {val:+.1f} mEq/L\n  <small>{desc}</small>", unsafe_allow_html=True)
        else:
            st.markdown("*Belirgin etki yok*")
    
    with col_alk:
        st.markdown("**🔵 Alkaloz Yönündeki Etkiler**")
        if contribution.alkalosis_contributors:
            for name, val, desc in contribution.alkalosis_contributors:
                st.markdown(f"• **{name}:** 🔵↑ {val:+.1f} mEq/L\n  <small>{desc}</small>", unsafe_allow_html=True)
        else:
            st.markdown("*Belirgin etki yok*")
    
    # Respiratory
    resp_dir, resp_val, resp_desc = contribution.respiratory_effect
    if "Asidoz" in resp_dir:
        resp_icon = "🔴↑"
    elif "Alkaloz" in resp_dir:
        resp_icon = "🔵↓"
    else:
        resp_icon = "🟢"
    st.markdown(f"**🌬️ Respiratuvar etki:** {resp_icon} {resp_dir} ({resp_desc})")
    
    # Net effect
    if contribution.net_metabolic < -2:
        net_icon = "🔴↓"
        net_text = "Net metabolik asidoz yönünde etki"
    elif contribution.net_metabolic > 2:
        net_icon = "🔵↑"
        net_text = "Net metabolik alkaloz yönünde etki"
    else:
        net_icon = "🟢"
        net_text = "Net metabolik etki dengede"
    
    st.info(f"**Net metabolik etki:** {net_icon} **{contribution.net_metabolic:+.1f} mEq/L** — {net_text}\n\n{contribution.summary}")
    
    # Definition expander
    with st.expander("ℹ️ Bileşen etkileri ne demek?"):
        st.markdown(PARAM_DEFINITIONS["sid_effect"]["long"])
        st.markdown("---")
        st.markdown(PARAM_DEFINITIONS["albumin_effect"]["long"])
        st.markdown("---")
        st.markdown(PARAM_DEFINITIONS["lactate_effect"]["long"])
        st.markdown("---")
        st.markdown(PARAM_DEFINITIONS["residual_effect"]["long"])


def render_sid_table(out, interpret_sid_direction_func):
    """Render 3-layer SID table with Interpretation column"""
    sid = out.sid_values
    
    # SID interpretations
    sid_simple_interp = interpret_sid_direction_func(sid.sid_simple, "simple")
    sid_basic_interp = interpret_sid_direction_func(sid.sid_basic, "basic") if sid.sid_basic else "—"
    sid_full_interp = interpret_sid_direction_func(sid.sid_full, "full") if sid.sid_full else "—"
    
    data = [
        {"Katman": "SID_simple", "Formül": "Na - Cl", "Değer": f"{sid.sid_simple:.1f}", 
         "Normal": f"~{SID_NORMAL_SIMPLE}", "Yorum": sid_simple_interp, "Durum": "✓"},
        {"Katman": "SID_basic", "Formül": "Na - Cl - Lac", 
         "Değer": f"{sid.sid_basic:.1f}" if sid.sid_basic else "—",
         "Normal": f"~{SID_NORMAL_BASIC}", 
         "Yorum": sid_basic_interp,
         "Durum": "✓" if sid.sid_basic else f"❌ {sid.sid_basic_status}"},
        {"Katman": "SID_full (SIDa)", "Formül": "(Na+K+Ca+Mg) - (Cl+Lac)",
         "Değer": f"{sid.sid_full:.1f}" if sid.sid_full else "—",
         "Normal": f"~{SID_NORMAL_FULL}",
         "Yorum": sid_full_interp,
         "Durum": sid.sid_full_status + (f" (eksik: {', '.join(sid.sid_full_missing)})" if sid.sid_full_missing else "")}
    ]
    st.table(pd.DataFrame(data))
    
    # Definition expander
    with st.expander("ℹ️ SID parametreleri ne demek?"):
        st.markdown(PARAM_DEFINITIONS["sid_simple"]["long"])
        st.markdown("---")
        st.markdown(PARAM_DEFINITIONS["sid_basic"]["long"])
        st.markdown("---")
        st.markdown(PARAM_DEFINITIONS["sid_full"]["long"])


def render_stewart_params(out, interpret_sig_func):
    """Render Stewart parameters section"""
    st.subheader("🧪 Stewart Parametreleri")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if out.sid_values.sid_full:
            st.metric("SIDapparent", f"{out.sid_values.sid_full:.1f}")
        if out.sid_effective:
            st.metric("SIDeffective", f"{out.sid_effective:.1f}")
    
    with c2:
        if out.atot:
            st.metric("Atot", f"{out.atot:.1f}")
        
        # Cl/Na ratio with color coding
        if out.cl_na_ratio > 0.75:
            clna_icon = "🔴↑"
            clna_text = "Yüksek (asidoz eğilimi)"
        else:
            clna_icon = "🟢"
            clna_text = "Normal"
        st.metric("Cl/Na Oranı", f"{out.cl_na_ratio:.3f}", f"{clna_icon} {clna_text}")
    
    with c3:
        if out.sig is not None:
            # SIG color coding
            if out.sig > 2:
                sig_icon = "🔴↑"
            elif out.sig < -2:
                sig_icon = "🔵↓"
            else:
                sig_icon = "🟢"
            st.metric("SIG", f"{out.sig:.1f}", f"{sig_icon} {out.sig_interpretation}")
            if out.sig_reliability != "reliable":
                st.caption(f"⚠️ Güvenilirlik: {out.sig_reliability}")
    
    # Definition expander
    with st.expander("ℹ️ Stewart parametreleri ne demek?"):
        col_def1, col_def2 = st.columns(2)
        with col_def1:
            st.markdown(PARAM_DEFINITIONS["sid_effective"]["long"])
            st.markdown("---")
            st.markdown(PARAM_DEFINITIONS["atot"]["long"])
        with col_def2:
            st.markdown(PARAM_DEFINITIONS["sig"]["long"])
            st.markdown("---")
            st.markdown(PARAM_DEFINITIONS["cl_na_ratio"]["long"])


def render_anion_gap(out):
    """Render Anion Gap section"""
    st.subheader("📏 Anyon Gap")
    c1, c2 = st.columns(2)
    
    with c1:
        # AG color coding
        if out.anion_gap > 12:
            ag_icon = "🔴↑"
            ag_text = "Yüksek (HAGMA?)"
        else:
            ag_icon = "🟢"
            ag_text = "Normal"
        st.metric("AG", f"{out.anion_gap:.1f}", f"{ag_icon} {ag_text}")
    
    with c2:
        if out.anion_gap_corrected:
            # Corrected AG color coding
            if out.anion_gap_corrected > 16:
                agc_icon = "🔴↑"
                agc_text = "Yüksek"
            else:
                agc_icon = "🟢"
                agc_text = "Normal"
            st.metric("AG (düzeltilmiş)", f"{out.anion_gap_corrected:.1f}", f"{agc_icon} {agc_text}")
    
    # Definition expander
    with st.expander("ℹ️ Anyon Gap ne demek?"):
        col_ag1, col_ag2 = st.columns(2)
        with col_ag1:
            st.markdown(PARAM_DEFINITIONS["anion_gap"]["long"])
        with col_ag2:
            st.markdown(PARAM_DEFINITIONS["anion_gap_corrected"]["long"])


def render_compensation(out):
    """Render compensation section"""
    st.subheader("🫁 Kompanzasyon")
    if out.compensation_details:
        st.markdown(f"**{out.compensation_details}**")
    if "Uygun" in out.compensation_status:
        st.success(f"✅ {out.compensation_status}")
    elif out.compensation_status:
        st.warning(f"⚠️ {out.compensation_status}")


def render_classic_comparison(classic_comparison):
    """Render classic approach comparison"""
    if classic_comparison and classic_comparison.differences:
        with st.expander("🔍 Klasik Yaklaşıma Göre Fark", expanded=False):
            for diff in classic_comparison.differences:
                st.markdown(f"• {diff}")
            st.markdown("---")
            st.markdown(f"**{classic_comparison.stewart_advantage}**")
            if classic_comparison.missed_by_classic:
                st.warning("Klasik analizde gözden kaçabilecek durumlar: " + ", ".join(classic_comparison.missed_by_classic))


def render_cds_notes(cds_notes):
    """Render Clinical Decision Support notes"""
    if cds_notes:
        with st.expander("🧠 Klinik Karar Destek Notları", expanded=False):
            cat_a = [n for n in cds_notes if n.category == "A"]
            cat_b = [n for n in cds_notes if n.category == "B"]
            cat_c = [n for n in cds_notes if n.category == "C"]
            
            if cat_a:
                st.markdown("**A. Fizikokimyasal Zorunluluklar:**")
                for note in cat_a:
                    st.markdown(f"• {note.note}")
            
            if cat_b:
                st.markdown("**B. Maskelenme ve Karşıt Etkiler:**")
                for note in cat_b:
                    st.markdown(f"• {note.note}")
            
            if cat_c:
                st.markdown("**C. Olası Mekanizmalar:**")
                for note in cat_c:
                    st.markdown(f"• *{note.condition}* → {note.note}")
                    if note.mechanisms:
                        st.markdown("  Bu patern aşağıdaki mekanizmalarla uyumlu olabilir:")
                        for m in note.mechanisms:
                            st.markdown(f"    - {m}")
                        st.caption("  *Klinik korelasyon ve ek test gerektirir.*")


def render_soft_warnings(soft_warnings):
    """Render soft warnings (non-judgmental language)"""
    if soft_warnings:
        with st.expander("ℹ️ Eksik Parametre Notları", expanded=False):
            for w in soft_warnings:
                st.markdown(f"• {w}")


def render_warnings(warnings):
    """Render critical warnings"""
    for w in warnings:
        if "mismatch" in w.lower():
            st.error(f"❌ {w}")
        else:
            st.warning(f"⚠️ {w}")


# =============================================================================
# SIDEBAR COMPONENTS
# =============================================================================

def render_case_selector() -> Optional[str]:
    """Render sample case selector in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📚 Hazır Vakalar")
    
    case_names = {k: v["name"] for k, v in SAMPLE_CASES.items()}
    selected = st.sidebar.selectbox(
        "Vaka seç:",
        options=[""] + list(case_names.keys()),
        format_func=lambda x: case_names.get(x, "-- Seçiniz --")
    )
    
    if selected:
        case = SAMPLE_CASES[selected]
        st.sidebar.info(case["description"])
        st.sidebar.caption(f"💡 {case['teaching_point']}")
        
        if st.sidebar.button("📥 Değerleri Yükle", use_container_width=True):
            return selected
    
    return None


def load_case_values(case_key: str):
    """Load case values into session state"""
    if case_key and case_key in SAMPLE_CASES:
        case = SAMPLE_CASES[case_key]
        for k, v in case["values"].items():
            st.session_state[f"case_{k}"] = v
        return True
    return False


def get_case_value(key: str, default):
    """Get case value from session state, ensure float type"""
    val = st.session_state.get(f"case_{key}", default)
    if val is not None and isinstance(val, (int, float)):
        return float(val)
    return val


# =============================================================================
# LANDING & FOOTER
# =============================================================================

def render_landing():
    """Render landing description"""
    with st.expander("ℹ️ Bu uygulama hakkında", expanded=False):
        st.markdown(UI_TEXTS["landing"])


def render_footer(references: Dict[str, str]):
    """Render footer with references and disclaimer"""
    st.divider()
    with st.expander("📚 Referanslar"):
        for key, ref in references.items():
            st.caption(f"• {ref}")
    
    st.caption("📖 *Bu parametreler fizyolojik mekanizmaları tanımlar; tanı veya tedavi önerisi değildir.*")
    st.caption(f"🔬 **v3.2** | Contribution-Based Analysis, Modular Architecture")
    st.caption(UI_TEXTS["disclaimer"])
