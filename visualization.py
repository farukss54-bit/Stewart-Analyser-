# visualization.py
# Stewart Asit-Baz Analizi - Visualization Module v3.2
# Gamblegram-style charts and contribution visualizations

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass


# =============================================================================
# COLOR SCHEMES
# =============================================================================

COLORS = {
    # Cations (positive, left side)
    "na": "#4CAF50",       # Green - Sodium
    "k": "#8BC34A",        # Light green - Potassium
    "ca": "#CDDC39",       # Yellow-green - Calcium
    "mg": "#FFEB3B",       # Yellow - Magnesium
    "unmeasured_cation": "#FFC107",  # Amber
    
    # Anions (negative, right side)
    "cl": "#2196F3",       # Blue - Chloride
    "hco3": "#03A9F4",     # Light blue - Bicarbonate
    "lactate": "#FF5722",  # Deep orange - Lactate
    "albumin": "#9C27B0",  # Purple - Albumin (Atot)
    "phosphate": "#E91E63", # Pink - Phosphate
    "sig": "#F44336",      # Red - SIG (unmeasured anions)
    
    # Acidosis/Alkalosis
    "acidosis": "#EF5350",  # Red
    "alkalosis": "#42A5F5", # Blue
    "neutral": "#66BB6A",   # Green
}


# =============================================================================
# GAMBLEGRAM VISUALIZATION
# =============================================================================

def create_gamblegram(
    na: float,
    cl: float,
    hco3: float,
    k: Optional[float] = None,
    ca: Optional[float] = None,
    mg: Optional[float] = None,
    lactate: Optional[float] = None,
    albumin_gl: Optional[float] = None,
    sig: Optional[float] = None,
    show_title: bool = True
) -> go.Figure:
    """
    Create Gamblegram-style visualization of plasma electrolytes.
    
    Shows the balance between cations and anions in plasma.
    Physiological principle: Sum of cations = Sum of anions (electroneutrality)
    
    Note: This is a simplified educational visualization.
    True Stewart analysis involves SID, Atot, and pCO2 as independent variables.
    """
    
    # Default values for missing parameters
    k = k or 4.0
    ca = ca or 1.25  # mmol/L (ionized)
    mg = mg or 0.5   # mmol/L
    lactate = lactate or 1.0
    
    # Convert albumin to Atot effect (simplified)
    # Atot ≈ 0.28 × Albumin(g/L) + 1.8 × Phosphate(mmol/L)
    # For simplicity, use albumin contribution only
    if albumin_gl:
        atot = 0.28 * albumin_gl / 10  # Rough mmol/L equivalent charge
    else:
        atot = 12  # Default ~4 g/dL albumin
    
    # Calculate SIG if not provided
    if sig is None:
        # Approximate from electroneutrality
        cations = na + k + (ca * 2) + (mg * 2)
        anions = cl + hco3 + lactate + atot
        sig = max(0, cations - anions)
    
    # Cations (left bar)
    cation_values = [na, k, ca * 2, mg * 2]  # Ca and Mg are divalent
    cation_labels = ["Na⁺", "K⁺", "Ca²⁺", "Mg²⁺"]
    cation_colors = [COLORS["na"], COLORS["k"], COLORS["ca"], COLORS["mg"]]
    
    # Anions (right bar)
    anion_values = [cl, hco3, lactate, atot]
    anion_labels = ["Cl⁻", "HCO₃⁻", "Laktat", "A⁻ (Atot)"]
    anion_colors = [COLORS["cl"], COLORS["hco3"], COLORS["lactate"], COLORS["albumin"]]
    
    # Add SIG if significant
    if sig and sig > 2:
        anion_values.append(sig)
        anion_labels.append("SIG")
        anion_colors.append(COLORS["sig"])
    
    # Create figure
    fig = go.Figure()
    
    # Cation bar (stacked)
    cumulative = 0
    for val, label, color in zip(cation_values, cation_labels, cation_colors):
        fig.add_trace(go.Bar(
            name=label,
            x=["Katyonlar"],
            y=[val],
            marker_color=color,
            text=f"{label}<br>{val:.1f}",
            textposition="inside",
            hovertemplate=f"{label}: {val:.1f} mEq/L<extra></extra>",
            base=cumulative
        ))
        cumulative += val
    
    # Anion bar (stacked)
    cumulative = 0
    for val, label, color in zip(anion_values, anion_labels, anion_colors):
        fig.add_trace(go.Bar(
            name=label,
            x=["Anyonlar"],
            y=[val],
            marker_color=color,
            text=f"{label}<br>{val:.1f}" if val > 3 else "",
            textposition="inside",
            hovertemplate=f"{label}: {val:.1f} mEq/L<extra></extra>",
            base=cumulative
        ))
        cumulative += val
    
    # Layout
    fig.update_layout(
        title="Plazma Elektrolit Dengesi (Gamblegram)" if show_title else "",
        barmode="stack",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="mEq/L",
        height=500,
        template="plotly_white"
    )
    
    return fig


# =============================================================================
# CONTRIBUTION BAR CHART
# =============================================================================

def create_contribution_chart(
    mechanism_analysis,
    show_title: bool = True
) -> go.Figure:
    """
    Create horizontal bar chart showing mechanism contributions to BE.
    
    Positive values = alkalosis direction
    Negative values = acidosis direction
    """
    
    if not mechanism_analysis or not mechanism_analysis.all_mechanisms:
        return None
    
    mechanisms = mechanism_analysis.all_mechanisms
    
    # Prepare data
    names = []
    values = []
    colors = []
    percentages = []
    
    for mc in mechanisms:
        names.append(mc.name)
        values.append(mc.effect_meq)
        percentages.append(mc.contribution_percent)
        
        if mc.direction == "acidosis":
            colors.append(COLORS["acidosis"])
        else:
            colors.append(COLORS["alkalosis"])
    
    # Sort by absolute value
    sorted_data = sorted(zip(names, values, colors, percentages), 
                        key=lambda x: abs(x[1]), reverse=True)
    names, values, colors, percentages = zip(*sorted_data) if sorted_data else ([], [], [], [])
    
    # Create figure
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=list(names),
        x=list(values),
        orientation='h',
        marker_color=list(colors),
        text=[f"{v:+.1f} mEq/L ({p:.0f}%)" for v, p in zip(values, percentages)],
        textposition='outside',
        hovertemplate="%{y}<br>Etki: %{x:.1f} mEq/L<extra></extra>"
    ))
    
    # Add zero line
    fig.add_vline(x=0, line_width=2, line_color="black")
    
    # Add annotations for direction
    fig.add_annotation(x=-5, y=-0.5, text="🔴 Asidoz", showarrow=False, font=dict(size=12))
    fig.add_annotation(x=5, y=-0.5, text="🔵 Alkaloz", showarrow=False, font=dict(size=12))
    
    # Layout
    fig.update_layout(
        title="Mekanizma Katkıları (BE'ye göre)" if show_title else "",
        xaxis_title="mEq/L",
        yaxis_title="",
        height=300 + len(names) * 30,
        template="plotly_white",
        showlegend=False
    )
    
    return fig


# =============================================================================
# SID WATERFALL CHART
# =============================================================================

def create_sid_waterfall(
    sid_simple: float,
    lactate: Optional[float] = None,
    k: Optional[float] = None,
    ca: Optional[float] = None,
    mg: Optional[float] = None,
    show_title: bool = True
) -> go.Figure:
    """
    Create waterfall chart showing SID calculation steps.
    
    SID_simple → SID_basic → SID_full
    """
    
    # Calculate values
    sid_basic = sid_simple - (lactate or 0)
    
    ca_contrib = (ca or 0) * 2  # Ionized Ca in mEq/L
    mg_contrib = (mg or 0) * 2  # Mg in mEq/L
    k_contrib = k or 0
    
    sid_full = sid_basic + k_contrib + ca_contrib + mg_contrib
    
    # Create waterfall
    fig = go.Figure(go.Waterfall(
        name="SID",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "total"],
        x=["SID_simple<br>(Na-Cl)", "- Laktat", "+ K⁺", "+ Ca²⁺", "+ Mg²⁺", "SID_full"],
        y=[sid_simple, -(lactate or 0), k_contrib, ca_contrib, mg_contrib, 0],
        text=[f"{sid_simple:.1f}", f"-{lactate or 0:.1f}", f"+{k_contrib:.1f}", 
              f"+{ca_contrib:.1f}", f"+{mg_contrib:.1f}", f"{sid_full:.1f}"],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": COLORS["acidosis"]}},
        increasing={"marker": {"color": COLORS["alkalosis"]}},
        totals={"marker": {"color": "#607D8B"}}
    ))
    
    # Add reference line for normal SID
    fig.add_hline(y=40, line_dash="dash", line_color="green", 
                  annotation_text="Normal SID ~40")
    
    fig.update_layout(
        title="SID Hesaplama Adımları" if show_title else "",
        yaxis_title="mEq/L",
        height=400,
        template="plotly_white",
        showlegend=False
    )
    
    return fig


# =============================================================================
# pH GAUGE CHART
# =============================================================================

def create_ph_gauge(ph: float) -> go.Figure:
    """Create pH gauge visualization"""
    
    # Determine color based on pH
    if ph < 7.35:
        color = COLORS["acidosis"]
    elif ph > 7.45:
        color = COLORS["alkalosis"]
    else:
        color = COLORS["neutral"]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=ph,
        delta={'reference': 7.40, 'position': "bottom"},
        number={'suffix': "", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [6.8, 7.8], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [6.8, 7.35], 'color': '#FFCDD2'},  # Light red - acidemia
                {'range': [7.35, 7.45], 'color': '#C8E6C9'},  # Light green - normal
                {'range': [7.45, 7.8], 'color': '#BBDEFB'}   # Light blue - alkalemia
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': ph
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        template="plotly_white"
    )
    
    return fig


# =============================================================================
# STREAMLIT RENDER FUNCTIONS
# =============================================================================

def render_gamblegram(
    na: float, cl: float, hco3: float,
    k: Optional[float] = None,
    ca: Optional[float] = None,
    mg: Optional[float] = None,
    lactate: Optional[float] = None,
    albumin_gl: Optional[float] = None,
    sig: Optional[float] = None
):
    """Render Gamblegram in Streamlit"""
    st.subheader("📊 Plazma Elektrolit Dengesi")
    
    fig = create_gamblegram(na, cl, hco3, k, ca, mg, lactate, albumin_gl, sig, show_title=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("""
    *Bu görselleştirme eğitim amaçlıdır. Katyonlar (sol) ve anyonlar (sağ) dengede olmalıdır 
    (elektronötralite prensibi). SIG, ölçülmemiş anyonları temsil eder.*
    """)


def render_contribution_chart(mechanism_analysis):
    """Render contribution chart in Streamlit"""
    if not mechanism_analysis or not mechanism_analysis.all_mechanisms:
        return
    
    fig = create_contribution_chart(mechanism_analysis, show_title=False)
    if fig:
        st.plotly_chart(fig, use_container_width=True)


def render_sid_waterfall(sid_simple: float, lactate: Optional[float] = None,
                         k: Optional[float] = None, ca: Optional[float] = None,
                         mg: Optional[float] = None):
    """Render SID waterfall in Streamlit"""
    fig = create_sid_waterfall(sid_simple, lactate, k, ca, mg, show_title=False)
    st.plotly_chart(fig, use_container_width=True)


def render_ph_gauge(ph: float):
    """Render pH gauge in Streamlit"""
    fig = create_ph_gauge(ph)
    st.plotly_chart(fig, use_container_width=True)


def render_visualization_section(inp, out):
    """Render complete visualization section"""
    st.subheader("📈 Görselleştirme")
    
    tab1, tab2, tab3 = st.tabs(["Gamblegram", "Katkı Grafiği", "SID Waterfall"])
    
    with tab1:
        render_gamblegram(
            na=inp.na,
            cl=inp.cl,
            hco3=out.hco3_used,
            k=inp.k,
            ca=inp.ca,
            mg=inp.mg,
            lactate=inp.lactate,
            albumin_gl=inp.albumin_gl,
            sig=out.sig
        )
    
    with tab2:
        if out.mechanism_analysis:
            render_contribution_chart(out.mechanism_analysis)
        else:
            st.info("Mekanizma analizi mevcut değil")
    
    with tab3:
        render_sid_waterfall(
            sid_simple=out.sid_values.sid_simple,
            lactate=inp.lactate,
            k=inp.k,
            ca=inp.ca,
            mg=inp.mg
        )
