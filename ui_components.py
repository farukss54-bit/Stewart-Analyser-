# ui_components.py
# Stewart Asit-Baz Analizi - UI Components v3.3
# FIXED: Double arrow bug, green color issue
# Single arrow + severity-based color coding

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from constants import (
    SID_NORMAL_SIMPLE, SID_NORMAL_BASIC, SID_NORMAL_FULL,
    PARAM_DEFINITIONS, UI_TEXTS, SAMPLE_CASES
)


# =============================================================================
# COLOR CODING & INDICATORS - REDESIGNED v3.3
# =============================================================================

def get_emoji(level: str) -> str:
    """Generic status emoji"""
    return {"normal": "🟢", "info": "🔵", "warning": "🟡", "critical": "🔴"}.get(level, "⚪")


def get_value_indicator(value: float, param: str) -> dict:
    """
    Return a SINGLE indicator dict with: emoji, arrow, text, severity, color
    
    IMPORTANT: Only ONE arrow per value - no double arrows!
    
    Returns dict with keys:
        - emoji: Status emoji
        - arrow: Direction arrow (single!)
        - text: Description text
        - severity: Level name
        - color: CSS color code
    """
    result = {
        "emoji": "🟢",
        "arrow": "",
        "text": "Normal",
        "severity": "normal",
        "color": "#00CC00"
    }
    
    if param == "ph":
        if value < 6.80:
            result = {"emoji": "🚨", "arrow": "⬇", "text": "KRİTİK ASİDEMİ", "severity": "kritik", "color": "#FF0000"}
        elif value < 7.00:
            result = {"emoji": "🔴", "arrow": "⬇", "text": "Şiddetli Asidemi", "severity": "siddetli", "color": "#FF4444"}
        elif value < 7.20:
            result = {"emoji": "🟠", "arrow": "⬇", "text": "Orta Asidemi", "severity": "orta", "color": "#FF8800"}
        elif value < 7.35:
            result = {"emoji": "🟡", "arrow": "⬇", "text": "Hafif Asidemi", "severity": "hafif", "color": "#FFCC00"}
        elif value > 7.80:
            result = {"emoji": "🚨", "arrow": "⬆", "text": "KRİTİK ALKALEMİ", "severity": "kritik", "color": "#FF0000"}
        elif value > 7.65:
            result = {"emoji": "🔴", "arrow": "⬆", "text": "Şiddetli Alkalemi", "severity": "siddetli", "color": "#FF4444"}
        elif value > 7.55:
            result = {"emoji": "🟠", "arrow": "⬆", "text": "Orta Alkalemi", "severity": "orta", "color": "#FF8800"}
        elif value > 7.45:
            result = {"emoji": "🟡", "arrow": "⬆", "text": "Hafif Alkalemi", "severity": "hafif", "color": "#FFCC00"}
    
    elif param == "pco2":
        if value > 120:
            result = {"emoji": "🚨", "arrow": "⬆", "text": "KRİTİK HİPERKAPNİ", "severity": "kritik", "color": "#FF0000"}
        elif value > 80:
            result = {"emoji": "🔴", "arrow": "⬆", "text": "Şiddetli Resp. Asidoz", "severity": "siddetli", "color": "#FF4444"}
        elif value > 60:
            result = {"emoji": "🟠", "arrow": "⬆", "text": "Orta Resp. Asidoz", "severity": "orta", "color": "#FF8800"}
        elif value > 45:
            result = {"emoji": "🟡", "arrow": "⬆", "text": "Hafif Resp. Asidoz", "severity": "hafif", "color": "#FFCC00"}
        elif value < 15:
            result = {"emoji": "🚨", "arrow": "⬇", "text": "KRİTİK HİPOKAPNİ", "severity": "kritik", "color": "#FF0000"}
        elif value < 20:
            result = {"emoji": "🔴", "arrow": "⬇", "text": "Şiddetli Resp. Alkaloz", "severity": "siddetli", "color": "#FF4444"}
        elif value < 25:
            result = {"emoji": "🟠", "arrow": "⬇", "text": "Orta Resp. Alkaloz", "severity": "orta", "color": "#FF8800"}
        elif value < 35:
            result = {"emoji": "🟡", "arrow": "⬇", "text": "Hafif Resp. Alkaloz", "severity": "hafif", "color": "#FFCC00"}
    
    elif param == "hco3":
        if value < 10:
            result = {"emoji": "🚨", "arrow": "⬇", "text": "KRİTİK DÜŞÜK", "severity": "kritik", "color": "#FF0000"}
        elif value < 15:
            result = {"emoji": "🔴", "arrow": "⬇", "text": "Çok Düşük", "severity": "siddetli", "color": "#FF4444"}
        elif value < 18:
            result = {"emoji": "🟠", "arrow": "⬇", "text": "Düşük", "severity": "orta", "color": "#FF8800"}
        elif value < 22:
            result = {"emoji": "🟡", "arrow": "⬇", "text": "Hafif Düşük", "severity": "hafif", "color": "#FFCC00"}
        elif value > 40:
            result = {"emoji": "🚨", "arrow": "⬆", "text": "KRİTİK YÜKSEK", "severity": "kritik", "color": "#FF0000"}
        elif value > 35:
            result = {"emoji": "🔴", "arrow": "⬆", "text": "Çok Yüksek", "severity": "siddetli", "color": "#FF4444"}
        elif value > 30:
            result = {"emoji": "🟠", "arrow": "⬆", "text": "Yüksek", "severity": "orta", "color": "#FF8800"}
        elif value > 26:
            result = {"emoji": "🟡", "arrow": "⬆", "text": "Hafif Yüksek", "severity": "hafif", "color": "#FFCC00"}
    
    elif param == "be":
        if value < -20:
            result = {"emoji": "🚨", "arrow": "⬇", "text": "KRİTİK Met. Asidoz", "severity": "kritik", "color": "#FF0000"}
        elif value < -15:
            result = {"emoji": "🔴", "arrow": "⬇", "text": "Şiddetli Met. Asidoz", "severity": "siddetli", "color": "#FF4444"}
        elif value < -10:
            result = {"emoji": "🟠", "arrow": "⬇", "text": "Orta Met. Asidoz", "severity": "orta", "color": "#FF8800"}
        elif value < -2:
            result = {"emoji": "🟡", "arrow": "⬇", "text": "Hafif Met. Asidoz", "severity": "hafif", "color": "#FFCC00"}
        elif value > 20:
            result = {"emoji": "🚨", "arrow": "⬆", "text": "KRİTİK Met. Alkaloz", "severity": "kritik", "color": "#FF0000"}
        elif value > 15:
            result = {"emoji": "🔴", "arrow": "⬆", "text": "Şiddetli Met. Alkaloz", "severity": "siddetli", "color": "#FF4444"}
        elif value > 10:
            result = {"emoji": "🟠", "arrow": "⬆", "text": "Orta Met. Alkaloz", "severity": "orta", "color": "#FF8800"}
        elif value > 2:
            result = {"emoji": "🟡", "arrow": "⬆", "text": "Hafif Met. Alkaloz", "severity": "hafif", "color": "#FFCC00"}
    
    return result


# Legacy functions for backward compatibility
def get_acidbase_indicator(direction: str) -> str:
    """DEPRECATED: Use get_value_indicator() instead."""
    indicators = {
        "acidosis": "🔴",
        "alkalosis": "🔵",
        "resp_acidosis": "🔴",
        "resp_alkalosis": "🔵",
        "normal": "🟢",
    }
    return indicators.get(direction, "⚪")


def format_ph_display(ph: float) -> Tuple[str, str, str]:
    """DEPRECATED: Use get_value_indicator() instead."""
    ind = get_value_indicator(ph, "ph")
    return ind["emoji"], ind["text"], ind["severity"]


def format_pco2_display(pco2: float) -> Tuple[str, str, str]:
    """DEPRECATED: Use get_value_indicator() instead."""
    ind = get_value_indicator(pco2, "pco2")
    return ind["emoji"], ind["text"], ind["severity"]


def format_be_display(be: float) -> Tuple[str, str, str]:
    """DEPRECATED: Use get_value_indicator() instead."""
    ind = get_value_indicator(be, "be")
    return ind["emoji"], ind["text"], ind["severity"]


def format_hco3_display(hco3: float) -> Tuple[str, str, str]:
    """DEPRECATED: Use get_value_indicator() instead."""
    ind = get_value_indicator(hco3, "hco3")
    return ind["emoji"], ind["text"], ind["severity"]


# =============================================================================
# SECTION RENDERERS
# =============================================================================

def render_headline(headline, mechanism_analysis=None):
    """Render summary result - mechanism-based, non-diagnostic"""
    st.markdown("### 🎯 Özet Sonuç")
    
    dominant_lower = headline.dominant_mechanism.lower() if headline.dominant_mechanism else ""
    if "asidoz" in dominant_lower:
        dominant_icon = "🔴"
    elif "alkaloz" in dominant_lower:
        dominant_icon = "🔵"
    elif "normal" in dominant_lower or "yok" in dominant_lower:
        dominant_icon = "🟢"
    else:
        dominant_icon = "⚪"
    
    st.markdown(f"**Dominant metabolik mekanizma:** {dominant_icon} {headline.dominant_mechanism}")
    
    if headline.significant_mechanisms:
        st.markdown("**Anlamlı katkıda bulunan mekanizmalar:**")
        for sm in headline.significant_mechanisms:
            sm_icon = "🔴" if "asidoz" in sm.lower() else "🔵" if "alkaloz" in sm.lower() else "⚪"
            st.markdown(f"  • {sm_icon} {sm}")
    
    if headline.contributing_mechanisms:
        with st.expander("Katkıda bulunan diğer mekanizmalar"):
            for cm in headline.contributing_mechanisms:
                st.markdown(f"  • {cm}")
    
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
    
    if headline.pattern_note:
        st.info(f"📋 {headline.pattern_note}")


def render_basic_values(ph: float, pco2: float, hco3_used: float, be_used: float,
                        hco3_source: str, be_source: str):
    """
    Render basic blood gas values with SINGLE arrow and severity-based coloring.
    
    FIXED in v3.3:
    - Removed st.metric delta parameter (was causing double arrows)
    - Added severity-based color coding
    - Single clear arrow direction per value
    """
    st.subheader("📊 Temel Değerler")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        ind = get_value_indicator(ph, "ph")
        st.metric("pH", f"{ph:.2f}")
        # Custom colored indicator below - NO DELTA, NO DOUBLE ARROWS
        arrow_text = f"{ind['arrow']} " if ind['arrow'] else ""
        st.markdown(
            f"<div style='text-align:center; padding:5px; border-radius:5px; "
            f"background-color:{ind['color']}20; border:1px solid {ind['color']};'>"
            f"<span style='color:{ind['color']}; font-weight:bold;'>"
            f"{ind['emoji']} {arrow_text}{ind['text']}</span></div>",
            unsafe_allow_html=True
        )
    
    with c2:
        ind = get_value_indicator(pco2, "pco2")
        st.metric("pCO₂", f"{pco2:.1f} mmHg")
        arrow_text = f"{ind['arrow']} " if ind['arrow'] else ""
        st.markdown(
            f"<div style='text-align:center; padding:5px; border-radius:5px; "
            f"background-color:{ind['color']}20; border:1px solid {ind['color']};'>"
            f"<span style='color:{ind['color']}; font-weight:bold;'>"
            f"{ind['emoji']} {arrow_text}{ind['text']}</span></div>",
            unsafe_allow_html=True
        )
    
    with c3:
        ind = get_value_indicator(hco3_used, "hco3")
        src = " (hes.)" if hco3_source == "calculated" else ""
        st.metric("HCO₃⁻", f"{hco3_used:.1f}{src}")
        arrow_text = f"{ind['arrow']} " if ind['arrow'] else ""
        st.markdown(
            f"<div style='text-align:center; padding:5px; border-radius:5px; "
            f"background-color:{ind['color']}20; border:1px solid {ind['color']};'>"
            f"<span style='color:{ind['color']}; font-weight:bold;'>"
            f"{ind['emoji']} {arrow_text}{ind['text']}</span></div>",
            unsafe_allow_html=True
        )
    
    with c4:
        ind = get_value_indicator(be_used, "be")
        src = " (hes.)" if be_source == "calculated" else ""
        st.metric("BE", f"{be_used:+.1f}{src}")
        arrow_text = f"{ind['arrow']} " if ind['arrow'] else ""
        st.markdown(
            f"<div style='text-align:center; padding:5px; border-radius:5px; "
            f"background-color:{ind['color']}20; border:1px solid {ind['color']};'>"
            f"<span style='color:{ind['color']}; font-weight:bold;'>"
            f"{ind['emoji']} {arrow_text}{ind['text']}</span></div>",
            unsafe_allow_html=True
        )
    
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
                st.markdown(f"• **{name}:** 🔴⬇ {val:+.1f} mEq/L\n  <small>{desc}</small>", unsafe_allow_html=True)
        else:
            st.markdown("*Belirgin etki yok*")
    
    with col_alk:
        st.markdown("**🔵 Alkaloz Yönündeki Etkiler**")
        if contribution.alkalosis_contributors:
            for name, val, desc in contribution.alkalosis_contributors:
                st.markdown(f"• **{name}:** 🔵⬆ {val:+.1f} mEq/L\n  <small>{desc}</small>", unsafe_allow_html=True)
        else:
            st.markdown("*Belirgin etki yok*")
    
    resp_dir, resp_val, resp_desc = contribution.respiratory_effect
    if "Asidoz" in resp_dir:
        resp_icon = "🔴⬆"
    elif "Alkaloz" in resp_dir:
        resp_icon = "🔵⬇"
    else:
        resp_icon = "🟢"
    st.markdown(f"**🌬️ Respiratuvar etki:** {resp_icon} {resp_dir} ({resp_desc})")
    
    if contribution.net_metabolic < -2:
        net_icon = "🔴⬇"
        net_text = "Net metabolik asidoz yönünde etki"
    elif contribution.net_metabolic > 2:
        net_icon = "🔵⬆"
        net_text = "Net metabolik alkaloz yönünde etki"
    else:
        net_icon = "🟢"
        net_text = "Net metabolik etki dengede"
    
    st.info(f"**Net metabolik etki:** {net_icon} **{contribution.net_metabolic:+.1f} mEq/L** — {net_text}\n\n{contribution.summary}")
    
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
         "Durum": "✓" if sid.sid_basic else f"✗ {sid.sid_basic_status}"},
        {"Katman": "SID_full (SIDa)", "Formül": "(Na+K+Ca+Mg) - (Cl+Lac)",
         "Değer": f"{sid.sid_full:.1f}" if sid.sid_full else "—",
         "Normal": f"~{SID_NORMAL_FULL}",
         "Yorum": sid_full_interp,
         "Durum": sid.sid_full_status + (f" (eksik: {', '.join(sid.sid_full_missing)})" if sid.sid_full_missing else "")}
    ]
    st.table(pd.DataFrame(data))
    
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
        
        if out.cl_na_ratio > 0.75:
            clna_icon = "🔴⬆"
            clna_text = "Yüksek (asidoz eğilimi)"
        else:
            clna_icon = "🟢"
            clna_text = "Normal"
        st.metric("Cl/Na Oranı", f"{out.cl_na_ratio:.3f}")
        st.caption(f"{clna_icon} {clna_text}")
    
    with c3:
        if out.sig is not None:
            if out.sig > 2:
                sig_icon = "🔴⬆"
            elif out.sig < -2:
                sig_icon = "🔵⬇"
            else:
                sig_icon = "🟢"
            st.metric("SIG", f"{out.sig:.1f}")
            st.caption(f"{sig_icon} {out.sig_interpretation}")
            if out.sig_reliability != "reliable":
                st.caption(f"⚠️ Güvenilirlik: {out.sig_reliability}")
    
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
    st.subheader("🔍 Anyon Gap")
    c1, c2 = st.columns(2)
    
    with c1:
        if out.anion_gap > 12:
            ag_icon = "🔴⬆"
            ag_text = "Yüksek (HAGMA?)"
        else:
            ag_icon = "🟢"
            ag_text = "Normal"
        st.metric("AG", f"{out.anion_gap:.1f}")
        st.caption(f"{ag_icon} {ag_text}")
    
    with c2:
        if out.anion_gap_corrected:
            if out.anion_gap_corrected > 16:
                agc_icon = "🔴⬆"
                agc_text = "Yüksek"
            else:
                agc_icon = "🟢"
                agc_text = "Normal"
            st.metric("AG (düzeltilmiş)", f"{out.anion_gap_corrected:.1f}")
            st.caption(f"{agc_icon} {agc_text}")
    
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


def render_warnings(out_warnings):
    """Render critical warnings"""
    for w in out_warnings:
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
        st.markdown(UI_TEXTS.get("landing", ""))


def render_footer(references: Dict[str, str], acknowledgments: Dict[str, str] = None):
    """Render footer with references, acknowledgments and disclaimer"""
    st.divider()
    with st.expander("📚 Referanslar"):
        for key, ref in references.items():
            st.caption(f"• {ref}")

    if acknowledgments:
        st.divider()
        st.markdown("### 🙏 Teşekkürler")
        for category, acknowledgment in acknowledgments.items():
            st.caption(f"• {acknowledgment}")

    st.caption("📖 *Bu parametreler fizyolojik mekanizmaları tanımlar; tanı veya tedavi önerisi değildir.*")
    st.caption(f"🔬 **v3.5** | Sprint 4: PDF Vaka Entegrasyonu + Siggaard-Andersen BE")
    st.caption(UI_TEXTS.get("disclaimer", ""))
