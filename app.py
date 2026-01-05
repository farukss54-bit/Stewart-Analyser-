# app.py
# Stewart Asit-Baz Analizi - Streamlit UI
# Hesaplamalar core.py'de, bu dosya sadece arayüz.

import streamlit as st
import pandas as pd
from datetime import datetime
from io import StringIO
import sys
import os

# Modül yolunu ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import (
    StewartInput, StewartOutput, ValidationResult,
    analyze_stewart, output_to_dict, dict_to_input,
    calculate_hco3, calculate_be,
    interpret_ph, interpret_pco2, interpret_sid_effect,
    interpret_albumin_effect, interpret_lactate, interpret_sig, interpret_residual
)
from constants import (
    PH_MIN, PH_MAX, PCO2_MIN, PCO2_MAX,
    NA_MIN, NA_MAX, CL_MIN, CL_MAX, K_MIN, K_MAX,
    CA_MIN, CA_MAX, CA_NORMAL, MG_MIN, MG_MAX, MG_NORMAL,
    LACTATE_MIN, LACTATE_MAX, LACTATE_THRESHOLD,
    ALBUMIN_MIN_GL, ALBUMIN_MAX_GL, ALBUMIN_NORMAL_GL,
    ALBUMIN_MIN_GDL, ALBUMIN_MAX_GDL, ALBUMIN_NORMAL_GDL,
    PO4_MIN, PO4_MAX, PO4_NORMAL,
    BE_MIN, BE_MAX,
    SID_NORMAL_SIMPLE, SID_NORMAL_BASIC, SID_NORMAL_FULL,
    SIG_THRESHOLD, CLINICAL_SIGNIFICANCE_THRESHOLD,
    FLAGS
)

# === SAYFA AYARLARI ===
st.set_page_config(
    page_title="Stewart Asit-Baz Analizi",
    page_icon="🩸",
    layout="wide"
)

# === BAŞLIK ===
st.title("🩸 Stewart Asit-Baz Analizi")
st.markdown("*Fizikokimyasal yaklaşımla kan gazı değerlendirmesi*")

# Uyarı
st.warning("⚠️ **Eğitim amaçlıdır.** Klinik karar için mutlaka uzman değerlendirmesi gereklidir.")

# === SIDEBAR ===
st.sidebar.header("⚙️ Ayarlar")

# Mod seçimi
mod = st.sidebar.radio(
    "Hesaplama Modu",
    ["Hızlı (Klinik)", "Gelişmiş"],
    help="Hızlı mod: Fencl-derived residual yaklaşımı\nGelişmiş mod: SIG = SIDa - SIDe (Stewart)"
)

# Batch mode
st.sidebar.divider()
batch_mode = st.sidebar.checkbox("📊 Batch Modu (CSV)", help="Birden fazla hastayı CSV ile analiz et")

# === YARDIMCI FONKSİYONLAR ===

def get_status_emoji(level: str) -> str:
    """Seviyeye göre emoji döndür"""
    return {
        "normal": "🟢",
        "info": "🔵",
        "warning": "🟡",
        "critical": "🔴"
    }.get(level, "⚪")


def render_metric_with_interpretation(label: str, value: str, interpretation: str, level: str):
    """Metrik ve yorumunu göster"""
    emoji = get_status_emoji(level)
    st.metric(label, value, f"{emoji} {interpretation}")


def create_download_csv(inp: StewartInput, out: StewartOutput) -> str:
    """CSV indirme için string oluştur"""
    data = output_to_dict(inp, out)
    data["timestamp"] = datetime.now().isoformat()
    df = pd.DataFrame([data])
    return df.to_csv(index=False)


def show_flags_and_warnings(out: StewartOutput):
    """Flag ve uyarıları göster"""
    # Kritik flagler
    critical_flags = ["BE_MISMATCH", "HCO3_MISMATCH", "VALIDATION_FAILED"]
    for flag in out.flags:
        if flag in critical_flags:
            st.error(f"❌ **{flag}:** {FLAGS.get(flag, flag)}")
    
    # Bilgi flagleri
    info_flags = ["BE_CALCULATED", "HCO3_CALCULATED", "INCOMPLETE_DATA"]
    shown_info = []
    for flag in out.flags:
        if flag in info_flags and flag not in shown_info:
            st.info(f"ℹ️ {FLAGS.get(flag, flag)}")
            shown_info.append(flag)
    
    # SIG güvenilirlik
    sig_flags = ["SIG_APPROXIMATE", "SIG_UNDERESTIMATED", "SIG_UNRELIABLE"]
    for flag in out.flags:
        if flag in sig_flags:
            st.warning(f"⚠️ **SIG Güvenilirlik:** {FLAGS.get(flag, flag)}")
    
    # Uyarılar
    for warning in out.warnings:
        if "mismatch" in warning.lower():
            st.error(f"❌ {warning}")
        else:
            st.warning(f"⚠️ {warning}")


def show_sid_table(out: StewartOutput):
    """3 katmanlı SID tablosu"""
    sid = out.sid_values
    
    st.markdown("### SID Değerleri (3 Katmanlı)")
    
    data = []
    
    # SID simple
    data.append({
        "Katman": "SID_simple",
        "Formül": "Na - Cl",
        "Değer": f"{sid.sid_simple:.1f}",
        "Normal": f"~{SID_NORMAL_SIMPLE}",
        "Durum": sid.sid_simple_status
    })
    
    # SID basic
    if sid.sid_basic is not None:
        data.append({
            "Katman": "SID_basic",
            "Formül": "Na - Cl - Lac",
            "Değer": f"{sid.sid_basic:.1f}",
            "Normal": f"~{SID_NORMAL_BASIC}",
            "Durum": sid.sid_basic_status
        })
    else:
        data.append({
            "Katman": "SID_basic",
            "Formül": "Na - Cl - Lac",
            "Değer": "—",
            "Normal": f"~{SID_NORMAL_BASIC}",
            "Durum": f"❌ {sid.sid_basic_status}"
        })
    
    # SID full
    if sid.sid_full is not None:
        missing_str = f" (eksik: {', '.join(sid.sid_full_missing)})" if sid.sid_full_missing else ""
        data.append({
            "Katman": "SID_full (SIDa)",
            "Formül": "(Na+K+Ca+Mg) - (Cl+Lac)",
            "Değer": f"{sid.sid_full:.1f}",
            "Normal": f"~{SID_NORMAL_FULL}",
            "Durum": f"{sid.sid_full_status}{missing_str}"
        })
    else:
        data.append({
            "Katman": "SID_full (SIDa)",
            "Formül": "(Na+K+Ca+Mg) - (Cl+Lac)",
            "Değer": "—",
            "Normal": f"~{SID_NORMAL_FULL}",
            "Durum": f"❌ {sid.sid_full_status}"
        })
    
    st.table(pd.DataFrame(data))


# === BATCH MODE ===

if batch_mode:
    st.header("📊 Batch Analiz")
    st.markdown("CSV dosyası yükleyerek birden fazla hastayı analiz edin.")
    
    # Örnek CSV formatı
    with st.expander("📋 CSV Format Örneği"):
        st.markdown("""
        CSV dosyanız şu sütunları içermelidir:
        
        **Zorunlu:** `ph`, `pco2`, `na`, `cl`
        
        **Opsiyonel:** `k`, `ca`, `mg`, `lactate`, `albumin_gl`, `po4`, `be`, `hco3`
        
        **Not:** Eksik değerler boş bırakılabilir. Varsayım yapılmaz.
        """)
        
        example_csv = """ph,pco2,na,cl,k,ca,mg,lactate,albumin_gl,po4,be,hco3
7.28,36,138,112,4.5,1.2,,2,30,1.2,-7,
7.48,60,132,76,4.0,1.25,,1.9,18,,7.6,
7.35,40,140,100,4.2,,,1,40,1,0,24"""
        st.code(example_csv, language="csv")
        st.download_button(
            "📥 Örnek CSV İndir",
            example_csv,
            "ornek_kan_gazi.csv",
            "text/csv"
        )
    
    # CSV yükleme
    uploaded_file = st.file_uploader("CSV Dosyası Yükle", type=["csv"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ {len(df)} satır yüklendi")
            
            # Analiz et
            if st.button("🔬 Tümünü Analiz Et", type="primary"):
                results = []
                errors = []
                
                progress = st.progress(0)
                for idx, row in df.iterrows():
                    try:
                        inp = dict_to_input(row.to_dict())
                        out, validation = analyze_stewart(inp, mode="quick" if mod == "Hızlı (Klinik)" else "advanced")
                        
                        if validation.is_valid:
                            result = output_to_dict(inp, out)
                            result["row_number"] = idx + 1
                            result["status"] = "OK"
                            results.append(result)
                        else:
                            errors.append({
                                "row_number": idx + 1,
                                "errors": ", ".join(validation.errors)
                            })
                    except Exception as e:
                        errors.append({
                            "row_number": idx + 1,
                            "errors": str(e)
                        })
                    
                    progress = st.progress(0.0)
                    
                    for i, (_, row) in enumerate(df.iterrows(), start=1):
                        ...
                        progress.progress(min(i / len(df), 1.0))
                
                # Sonuçları göster
                if results:
                    st.subheader("✅ Başarılı Analizler")
                    results_df = pd.DataFrame(results)
                    
                    # Önemli sütunları öne al
                    important_cols = ["row_number", "status", "dominant_disorder", "flags", 
                                     "missing_params", "warnings", "sid_simple", "sig", "be_used"]
                    other_cols = [c for c in results_df.columns if c not in important_cols]
                    results_df = results_df[important_cols + other_cols]
                    
                    st.dataframe(results_df, use_container_width=True)
                    
                    # İndir
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        "📥 Sonuçları CSV Olarak İndir",
                        csv,
                        f"stewart_sonuclar_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        "text/csv"
                    )
                
                if errors:
                    st.subheader("❌ Hatalı Satırlar")
                    errors_df = pd.DataFrame(errors)
                    st.dataframe(errors_df, use_container_width=True)
        
        except Exception as e:
            st.error(f"CSV okuma hatası: {e}")

else:
    # === TEKİL ANALİZ ===
    
    # --- HIZLI MOD ---
    if mod == "Hızlı (Klinik)":
        st.header("📋 Hızlı Klinik Analiz")
        st.markdown("""
        **Fencl-derived Residual** yaklaşımı ile hızlı değerlendirme.  
        Residual = BE - (SID etkisi) - (Albümin etkisi) - (Laktat etkisi)
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Kan Gazı Değerleri")
            ph = st.number_input("pH", min_value=PH_MIN, max_value=PH_MAX, value=7.40, step=0.01, format="%.2f")
            pco2 = st.number_input("pCO₂ (mmHg)", min_value=PCO2_MIN, max_value=PCO2_MAX, value=40.0, step=0.1)
            
            # BE/BD - checkbox yaklaşımı (default 0 tuzağı kaldırıldı)
            st.markdown("---")
            be_var = st.checkbox("BE/BD değeri var", value=False, help="İşaretli değilse BE otomatik hesaplanır")
            
            if be_var:
                be_tipi = st.radio("Tip", ["Base Excess (BE)", "Base Deficit (BD)"], horizontal=True)
                be_deger = st.number_input(
                    "Değer (mEq/L)",
                    min_value=0.0 if be_tipi == "Base Deficit (BD)" else BE_MIN,
                    max_value=BE_MAX,
                    value=0.0,
                    step=0.1
                )
                be_input = be_deger
                is_bd = be_tipi == "Base Deficit (BD)"
            else:
                be_input = None
                is_bd = False
                st.caption("BE otomatik hesaplanacak")
        
        with col2:
            st.subheader("Elektrolit ve Biyokimya")
            na = st.number_input("Na⁺ (mmol/L)", min_value=NA_MIN, max_value=NA_MAX, value=140.0, step=0.1)
            cl = st.number_input("Cl⁻ (mmol/L)", min_value=CL_MIN, max_value=CL_MAX, value=100.0, step=0.1)
            
            # Laktat - checkbox
            laktat_var = st.checkbox("Laktat değeri var", value=False)
            if laktat_var:
                laktat = st.number_input("Laktat (mmol/L)", min_value=LACTATE_MIN, max_value=LACTATE_MAX, value=1.0, step=0.1)
            else:
                laktat = None
            
            # Albümin - checkbox
            albumin_var = st.checkbox("Albümin değeri var", value=False)
            if albumin_var:
                alb_col1, alb_col2 = st.columns([2, 1])
                with alb_col1:
                    alb_birim = st.selectbox("Birim", ["g/L", "g/dL"], index=0)
                    if alb_birim == "g/L":
                        albumin = st.number_input("Albümin (g/L)", min_value=ALBUMIN_MIN_GL, max_value=ALBUMIN_MAX_GL, value=ALBUMIN_NORMAL_GL, step=0.1)
                        albumin_gl = albumin
                    else:
                        albumin = st.number_input("Albümin (g/dL)", min_value=ALBUMIN_MIN_GDL, max_value=ALBUMIN_MAX_GDL, value=ALBUMIN_NORMAL_GDL, step=0.1)
                        albumin_gl = albumin * 10
            else:
                albumin_gl = None
            
            # HCO3 (opsiyonel)
            st.markdown("---")
            hco3_manuel = st.checkbox("HCO₃⁻ değerini manuel gir", value=False)
            if hco3_manuel:
                hco3 = st.number_input("HCO₃⁻ (mEq/L)", min_value=5.0, max_value=50.0, value=24.0, step=0.1)
            else:
                hco3 = None
                hco3_preview = calculate_hco3(ph, pco2)
                st.caption(f"HCO₃⁻ hesaplanacak: ~{hco3_preview:.1f} mEq/L")
        
        # Hesapla butonu
        if st.button("🔬 Analiz Et", type="primary", use_container_width=True):
            
            # Input oluştur
            inp = StewartInput(
                ph=ph,
                pco2=pco2,
                na=na,
                cl=cl,
                hco3=hco3,
                be=be_input,
                is_be_base_deficit=is_bd,
                lactate=laktat,
                albumin_gl=albumin_gl
            )
            
            # Analiz
            out, validation = analyze_stewart(inp, mode="quick")
            
            # Validasyon hataları
            if not validation.is_valid:
                for error in validation.errors:
                    st.error(f"❌ {error}")
                st.stop()
            
            st.divider()
            
            # === SONUÇLAR ===
            st.header("📊 Analiz Sonuçları")
            
            # Flags ve uyarılar
            show_flags_and_warnings(out)
            
            # pH, pCO2, HCO3, BE
            col_ph, col_pco2, col_hco3, col_be = st.columns(4)
            
            with col_ph:
                ph_interp, ph_level = interpret_ph(ph)
                emoji = get_status_emoji(ph_level)
                st.metric("pH", f"{ph:.2f}", f"{emoji} {ph_interp}")
            
            with col_pco2:
                pco2_interp, pco2_level = interpret_pco2(pco2)
                emoji = get_status_emoji(pco2_level)
                st.metric("pCO₂", f"{pco2:.1f} mmHg", f"{emoji} {pco2_interp}")
            
            with col_hco3:
                src_label = "Manuel" if out.hco3_source == "manual" else "Hesaplanan"
                st.metric("HCO₃⁻", f"{out.hco3_used:.1f} mEq/L", src_label)
            
            with col_be:
                src_label = "Girilen" if out.be_source == "manual" else "Hesaplanan"
                st.metric("Base Excess", f"{out.be_used:+.1f} mEq/L", src_label)
            
            st.divider()
            
            # SID Tablosu (3 katmanlı)
            show_sid_table(out)
            
            st.divider()
            
            # Fencl-derived Bileşenler
            st.subheader("Fencl-derived Bileşen Analizi")
            st.markdown("""
            <small>
            <b>Not:</b> Bu analiz BE'den bilinen bileşenlerin çıkarılmasıyla elde edilen 
            <b>Residual (Unmeasured component)</b> değerini gösterir. 
            Bu tam Stewart SIG (SIDa - SIDe) değildir. Kesin SIG için Gelişmiş Modu kullanın.
            </small>
            """, unsafe_allow_html=True)
            
            col_tablo, col_yorum = st.columns([1, 1])
            
            with col_tablo:
                # Tablo verisi
                tablo_data = {
                    "Bileşen": [],
                    "Değer": [],
                    "Etki (mEq/L)": [],
                    "Durum": []
                }
                
                # SID
                tablo_data["Bileşen"].append("SID (Na-Cl)")
                tablo_data["Değer"].append(f"{out.sid_values.sid_simple:.1f}")
                tablo_data["Etki (mEq/L)"].append(f"{out.sid_effect:+.1f}")
                tablo_data["Durum"].append("✓")
                
                # Albümin
                tablo_data["Bileşen"].append("Albümin")
                if out.albumin_effect is not None:
                    tablo_data["Değer"].append(f"{albumin_gl/10:.1f} g/dL" if albumin_gl else "—")
                    tablo_data["Etki (mEq/L)"].append(f"{out.albumin_effect:+.1f}")
                    tablo_data["Durum"].append("✓")
                else:
                    tablo_data["Değer"].append("—")
                    tablo_data["Etki (mEq/L)"].append("—")
                    tablo_data["Durum"].append("❌ eksik")
                
                # Laktat
                tablo_data["Bileşen"].append("Laktat")
                if out.lactate_effect is not None:
                    tablo_data["Değer"].append(f"{laktat:.1f}")
                    tablo_data["Etki (mEq/L)"].append(f"{out.lactate_effect:+.1f}")
                    tablo_data["Durum"].append("✓")
                else:
                    tablo_data["Değer"].append("—")
                    tablo_data["Etki (mEq/L)"].append("—")
                    tablo_data["Durum"].append("❌ eksik")
                
                # Residual
                tablo_data["Bileşen"].append("**Residual (Unmeasured)**")
                if out.residual_effect is not None:
                    tablo_data["Değer"].append("—")
                    tablo_data["Etki (mEq/L)"].append(f"{out.residual_effect:+.1f}")
                    tablo_data["Durum"].append("hesaplanan")
                else:
                    tablo_data["Değer"].append("—")
                    tablo_data["Etki (mEq/L)"].append("—")
                    tablo_data["Durum"].append("—")
                
                # Toplam
                tablo_data["Bileşen"].append("**Toplam (BE)**")
                tablo_data["Değer"].append("—")
                tablo_data["Etki (mEq/L)"].append(f"{out.be_used:+.1f}")
                tablo_data["Durum"].append("")
                
                st.table(pd.DataFrame(tablo_data))
            
            with col_yorum:
                st.markdown("**Yorumlar:**")
                
                # SID
                sid_interp, sid_level = interpret_sid_effect(out.sid_effect)
                st.markdown(f"{get_status_emoji(sid_level)} **SID:** {sid_interp}")
                
                # Albümin
                if out.albumin_effect is not None:
                    alb_interp, alb_level = interpret_albumin_effect(out.albumin_effect)
                    st.markdown(f"{get_status_emoji(alb_level)} **Albümin:** {alb_interp}")
                else:
                    st.markdown("⚪ **Albümin:** Değerlendirilemiyor (eksik)")
                
                # Laktat
                if laktat is not None:
                    lak_interp, lak_level = interpret_lactate(laktat)
                    st.markdown(f"{get_status_emoji(lak_level)} **Laktat:** {lak_interp}")
                else:
                    st.markdown("⚪ **Laktat:** Değerlendirilemiyor (eksik)")
                
                # Residual
                if out.residual_effect is not None:
                    res_interp, res_level = interpret_residual(out.residual_effect)
                    st.markdown(f"{get_status_emoji(res_level)} **Residual:** {res_interp}")
            
            st.divider()
            
            # Kompanzasyon
            st.subheader("Kompanzasyon Değerlendirmesi")
            
            if out.expected_pco2 is not None:
                st.markdown(f"**{out.compensation_details}**")
                
                if "Uygun" in out.compensation_status:
                    st.success(f"✅ {out.compensation_status}")
                else:
                    st.warning(f"⚠️ {out.compensation_status}")
                
                if out.observed_expected_diff is not None:
                    st.caption(f"Gözlenen - Beklenen fark: {out.observed_expected_diff:+.0f} mmHg")
            
            elif out.expected_hco3 is not None:
                st.markdown(f"**{out.compensation_details}**")
                st.info(f"ℹ️ {out.compensation_status}")
            
            else:
                st.info(f"ℹ️ {out.compensation_status}")
            
            st.divider()
            
            # Dominant Disorder
            st.subheader("🎯 Dominant Bozukluk")
            
            if out.dominant_disorder and out.dominant_disorder != "normal":
                disorder_display = out.dominant_disorder.replace("_", " ").title()
                st.markdown(f"**{disorder_display}**")
                
                if out.disorder_components:
                    st.caption(f"Bileşenler: {', '.join([c.replace('_', ' ') for c in out.disorder_components])}")
            else:
                st.success("Normal - Belirgin asit-baz bozukluğu saptanmadı")
            
            # Klinik Özet
            st.divider()
            st.subheader("🩺 Klinik Özet")
            
            if out.interpretations:
                for interp in out.interpretations:
                    st.markdown(f"• {interp}")
            else:
                st.success("Belirgin asit-baz bozukluğu saptanmadı.")
            
            # CSV Export
            st.divider()
            csv_data = create_download_csv(inp, out)
            st.download_button(
                "📥 Sonuçları CSV Olarak İndir",
                csv_data,
                f"stewart_analiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )

    # --- GELİŞMİŞ MOD ---
    elif mod == "Gelişmiş":
        st.header("🔬 Gelişmiş Stewart Analizi")
        st.markdown("""
        **SIG = SIDapparent - SIDeffective** (Stewart yaklaşımı)  
        Pozitif SIG → ölçülmemiş anyon yükü (HAGMA)
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Kan Gazı Değerleri")
            ph = st.number_input("pH", min_value=PH_MIN, max_value=PH_MAX, value=7.40, step=0.01, format="%.2f", key="adv_ph")
            pco2 = st.number_input("pCO₂ (mmHg)", min_value=PCO2_MIN, max_value=PCO2_MAX, value=40.0, step=0.1, key="adv_pco2")
            
            # HCO3 (opsiyonel)
            hco3_manuel = st.checkbox("HCO₃⁻ değerini manuel gir", value=False, key="adv_hco3_cb")
            if hco3_manuel:
                hco3 = st.number_input("HCO₃⁻ (mEq/L)", min_value=5.0, max_value=50.0, value=24.0, step=0.1, key="adv_hco3")
            else:
                hco3 = None
                hco3_preview = calculate_hco3(ph, pco2)
                st.caption(f"Hesaplanacak: ~{hco3_preview:.1f} mEq/L")
        
        with col2:
            st.subheader("Güçlü İyonlar")
            na = st.number_input("Na⁺ (mmol/L)", min_value=NA_MIN, max_value=NA_MAX, value=140.0, step=0.1, key="adv_na")
            k = st.number_input("K⁺ (mmol/L)", min_value=K_MIN, max_value=K_MAX, value=4.0, step=0.1, key="adv_k")
            cl = st.number_input("Cl⁻ (mmol/L)", min_value=CL_MIN, max_value=CL_MAX, value=100.0, step=0.1, key="adv_cl")
            
            # Laktat - checkbox (default False)
            laktat_var = st.checkbox("Laktat değeri var", value=False, key="adv_lac_cb")
            if laktat_var:
                laktat = st.number_input("Laktat (mmol/L)", min_value=LACTATE_MIN, max_value=LACTATE_MAX, value=1.0, step=0.1, key="adv_lac")
            else:
                laktat = None
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Opsiyonel İyonlar")
            st.caption("Varsayım yapılmaz. İşaretlemezseniz SIDa eksik hesaplanır.")
            
            # Ca - checkbox (default False, varsayım yok)
            ca_var = st.checkbox("Ca²⁺ değeri var", value=False, key="adv_ca_cb")
            if ca_var:
                ca = st.number_input("Ca²⁺ (mmol/L)", min_value=CA_MIN, max_value=CA_MAX, value=CA_NORMAL, step=0.01, key="adv_ca")
            else:
                ca = None
            
            # Mg - checkbox (default False)
            mg_var = st.checkbox("Mg²⁺ değeri var", value=False, key="adv_mg_cb")
            if mg_var:
                mg = st.number_input("Mg²⁺ (mmol/L)", min_value=MG_MIN, max_value=MG_MAX, value=MG_NORMAL, step=0.1, key="adv_mg")
            else:
                mg = None
        
        with col4:
            st.subheader("Zayıf Asitler")
            
            # Albümin - checkbox (default False)
            albumin_var = st.checkbox("Albümin değeri var", value=False, key="adv_alb_cb")
            if albumin_var:
                alb_birim = st.selectbox("Birim", ["g/L", "g/dL"], index=0, key="adv_alb_unit")
                if alb_birim == "g/L":
                    albumin = st.number_input("Albümin (g/L)", min_value=ALBUMIN_MIN_GL, max_value=ALBUMIN_MAX_GL, value=ALBUMIN_NORMAL_GL, step=0.1, key="adv_alb")
                    albumin_gl = albumin
                else:
                    albumin = st.number_input("Albümin (g/dL)", min_value=ALBUMIN_MIN_GDL, max_value=ALBUMIN_MAX_GDL, value=ALBUMIN_NORMAL_GDL, step=0.1, key="adv_alb_gdl")
                    albumin_gl = albumin * 10
            else:
                albumin_gl = None
            
            # Fosfat - checkbox (default False)
            po4_var = st.checkbox("Fosfat değeri var", value=False, key="adv_po4_cb")
            if po4_var:
                po4 = st.number_input("Fosfat PO₄³⁻ (mmol/L)", min_value=PO4_MIN, max_value=PO4_MAX, value=PO4_NORMAL, step=0.1, key="adv_po4")
            else:
                po4 = None
        
        # Hesapla butonu
        if st.button("🔬 Detaylı Analiz Et", type="primary", use_container_width=True):
            
            # Input oluştur
            inp = StewartInput(
                ph=ph,
                pco2=pco2,
                na=na,
                cl=cl,
                hco3=hco3,
                k=k,
                ca=ca,
                mg=mg,
                lactate=laktat,
                albumin_gl=albumin_gl,
                po4=po4
            )
            
            # Analiz
            out, validation = analyze_stewart(inp, mode="advanced")
            
            # Validasyon hataları
            if not validation.is_valid:
                for error in validation.errors:
                    st.error(f"❌ {error}")
                st.stop()
            
            st.divider()
            
            # === SONUÇLAR ===
            st.header("📊 Detaylı Analiz Sonuçları")
            
            # Flags ve uyarılar
            show_flags_and_warnings(out)
            
            # pH, pCO2, HCO3
            col_ph, col_pco2, col_hco3 = st.columns(3)
            
            with col_ph:
                ph_interp, ph_level = interpret_ph(ph)
                emoji = get_status_emoji(ph_level)
                st.metric("pH", f"{ph:.2f}", f"{emoji} {ph_interp}")
            
            with col_pco2:
                pco2_interp, pco2_level = interpret_pco2(pco2)
                emoji = get_status_emoji(pco2_level)
                st.metric("pCO₂", f"{pco2:.1f} mmHg", f"{emoji} {pco2_interp}")
            
            with col_hco3:
                src_label = "Manuel" if out.hco3_source == "manual" else "Hesaplanan"
                st.metric("HCO₃⁻", f"{out.hco3_used:.1f} mEq/L", src_label)
            
            st.divider()
            
            # SID Tablosu (3 katmanlı)
            show_sid_table(out)
            
            st.divider()
            
            # Stewart Parametreleri
            st.subheader("Stewart Parametreleri")
            st.markdown("**SIG = SIDapparent - SIDeffective** | Pozitif SIG → ölçülmemiş anyon yükü")
            
            col_sid, col_atot, col_sig = st.columns(3)
            
            with col_sid:
                if out.sid_values.sid_full is not None:
                    sid_delta = out.sid_values.sid_full - SID_NORMAL_FULL
                    if sid_delta < -CLINICAL_SIGNIFICANCE_THRESHOLD:
                        sid_status = "↓ Asidoz eğilimi"
                    elif sid_delta > CLINICAL_SIGNIFICANCE_THRESHOLD:
                        sid_status = "↑ Alkaloz eğilimi"
                    else:
                        sid_status = "Normal"
                    st.metric("SIDapparent", f"{out.sid_values.sid_full:.1f} mEq/L", sid_status)
                else:
                    st.metric("SIDapparent", "—", "Eksik parametreler")
                
                if out.sid_effective is not None:
                    st.metric("SIDeffective", f"{out.sid_effective:.1f} mEq/L")
            
            with col_atot:
                if out.atot is not None:
                    st.metric("Atot", f"{out.atot:.1f} mmol/L", help="Zayıf asitlerin toplam konsantrasyonu")
                else:
                    st.metric("Atot", "—", "Albümin eksik")
            
            with col_sig:
                if out.sig is not None:
                    sig_interp, sig_level = interpret_sig(out.sig)
                    emoji = get_status_emoji(sig_level)
                    reliability_note = f" ({out.sig_reliability})" if out.sig_reliability != "reliable" else ""
                    st.metric("SIG", f"{out.sig:.1f} mEq/L", f"{emoji} {sig_interp}")
                    if out.sig_reliability != "reliable":
                        st.caption(f"⚠️ Güvenilirlik: {out.sig_reliability}")
                else:
                    st.metric("SIG", "—", "Hesaplanamadı")
            
            st.divider()
            
            # Anyon Gap
            st.subheader("Anyon Gap")
            col_ag1, col_ag2 = st.columns(2)
            with col_ag1:
                st.metric("Anyon Gap", f"{out.anion_gap:.1f} mEq/L", help="AG = Na - (Cl + HCO₃)")
            with col_ag2:
                if out.anion_gap_corrected is not None:
                    st.metric("Düzeltilmiş AG", f"{out.anion_gap_corrected:.1f} mEq/L", help="Albümin için düzeltilmiş")
                else:
                    st.metric("Düzeltilmiş AG", "—", "Albümin eksik")
            
            st.divider()
            
            # Kompanzasyon
            st.subheader("Kompanzasyon Değerlendirmesi")
            
            if out.compensation_details:
                st.markdown(f"**{out.compensation_details}**")
            
            if out.compensation_status:
                if "Uygun" in out.compensation_status:
                    st.success(f"✅ {out.compensation_status}")
                elif "Akut" in out.compensation_status or "Kronik" in out.compensation_status:
                    st.info(f"ℹ️ {out.compensation_status}")
                else:
                    st.warning(f"⚠️ {out.compensation_status}")
            
            st.divider()
            
            # Dominant Disorder
            st.subheader("🎯 Dominant Bozukluk")
            
            if out.dominant_disorder and out.dominant_disorder != "normal":
                disorder_display = out.dominant_disorder.replace("_", " ").title()
                st.markdown(f"**{disorder_display}**")
                
                if out.disorder_components:
                    st.caption(f"Bileşenler: {', '.join([c.replace('_', ' ') for c in out.disorder_components])}")
            else:
                st.success("Normal - Belirgin asit-baz bozukluğu saptanmadı")
            
            # Klinik Özet
            st.divider()
            st.subheader("🩺 Klinik Özet")
            
            if out.interpretations:
                for interp in out.interpretations:
                    st.markdown(f"• {interp}")
            else:
                st.success("Belirgin asit-baz bozukluğu saptanmadı.")
            
            # CSV Export
            st.divider()
            csv_data = create_download_csv(inp, out)
            st.download_button(
                "📥 Sonuçları CSV Olarak İndir",
                csv_data,
                f"stewart_analiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )

# === FOOTER ===
st.divider()
st.caption("📚 **Referanslar:** Stewart PA (1983), Morgan TJ (2019), Story DA (2016), Fencl V (2000), Akoğlu H.")
st.caption("🔬 **Versiyon:** 2.1 | 3 katmanlı SID, HCO₃ kontrolü, SIG güvenilirlik, dominant disorder")
