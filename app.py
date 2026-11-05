import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Konfigurasi Halaman Web
st.set_page_config(page_title="Penjurian Poster STEMORA 2026", layout="wide", page_icon="🏆")

st.title("🏆 Platform Penjurian Poster Kajian Tindakan STEMORA 2026")
st.write("Sila isikan maklumat juri dan pemarkahan mengikut rubrik rasmi.")
st.markdown("---")

# Sambungan ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Maklumat Penjurian (Sidebar)
st.sidebar.header("📋 Maklumat Penjurian")
nama_juri = st.sidebar.text_input("Nama Juri", placeholder="Contoh: Dr. Ahmad")
id_poster = st.sidebar.text_input("ID / Kod Poster", placeholder="Contoh: P001")
tajuk_poster = st.sidebar.text_input("Tajuk Poster / Institusi")

# 3. Kriteria Rubrik (13 Kriteria Mengikut Susunan Baharu)
rubrik = [
    ("1. Tajuk, Nama Penulis dan Institusi", 3),
    ("2. Abstrak", 8),
    ("3. Latar Belakang Kajian", 7),
    ("4. Objektif Kajian", 7),
    ("5. Intervensi Kajian", 8),
    ("6. Metodologi Kajian", 8),
    ("7. Dapatan Kajian dan Bukti", 15),
    ("8. Perubahan yang Diperhatikan dan Refleksi", 6),
    ("9. Kesimpulan dan Cadangan", 5),
    ("10. Kesinambungan dan Keselarasan Kajian", 20),
    ("11. Rujukan", 4),
    ("12. Pematuhan Format dan Kelengkapan Kandungan Poster", 5),
    ("13. Kreativiti dan Reka Bentuk Visual", 4)
]

st.subheader("📝 Borang Pemarkahan Juri")

with st.form("borang_penjurian"):
    markah_input = {}
    total_score = 0.0

    # Header Tabular
    col_k, col_m = st.columns([3, 1])
    col_k.markdown("**Kriteria Pemarkahan**")
    col_m.markdown("**Markah Juri**")
    st.markdown("---")

    # Baris Input Markah
    for kriteria, max_mark in rubrik:
        c1, c2 = st.columns([3, 1])
        c1.write(f"**{kriteria}** *(Maks: {max_mark})*")
        score = c2.number_input(
            label=f"Markah {kriteria}",
            min_value=0.0,
            max_value=float(max_mark),
            step=0.5,
            key=kriteria,
            label_visibility="collapsed"
        )
        total_score += score

    st.markdown("---")

    # Logik Penentuan Pingat
    if total_score >= 85:
        pingat = "GOLD"
        badge = "🥇 GOLD"
    elif total_score >= 70:
        pingat = "SILVER"
        badge = "🥈 SILVER"
    else:
        pingat = "BRONZE"
        badge = "🥉 BRONZE"

    # Paparan Ringkasan Keputusan
    st.metric(label="Jumlah Markah Keseluruhan (100)", value=f"{total_score} / 100")
    st.subheader(f"Keputusan Pingat: {badge}")

    submitted = st.form_submit_button("Hantar & Simpan Keputusan", use_container_width=True)

    if submitted:
        if not nama_juri or not id_poster:
            st.error("⚠️ Sila lengkapkan Nama Juri dan ID Poster di bahagian bar sampingan (Sidebar)!")
        else:
            try:
                # Baca data sedia ada
                existing_data = conn.read(worksheet="Rekap", ttl=0)
                
                # Sediakan data baharu
                new_row = pd.DataFrame([{
                    "Nama Juri": nama_juri,
                    "ID Poster": id_poster,
                    "Tajuk Poster": tajuk_poster,
                    "Jumlah Markah": total_score,
                    "Peratus": f"{total_score}%",
                    "Pingat": pingat
                }])

                # Gabungkan & kemaskini ke Google Sheets
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(worksheet="Rekap", data=updated_df)
                
                st.success(f"✅ Keputusan penjurian untuk ID Poster {id_poster} berjaya disimpan ke pangkalan data!")
            except Exception as e:
                st.error(f"Ralat semasa menyimpan data: {e}")
