import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Konfigurasi Halaman Web
st.set_page_config(page_title="Penjurian Poster STEMORA 2026", layout="wide", page_icon="🏆")

st.title("🏆 Platform Penjurian Poster Kajian Tindakan STEMORA 2026")
st.write("Sila pilih nama juri dan ID poster untuk memulakan pemarkahan.")
st.markdown("---")

# Sambungan ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Muat Turun Data Agihan Juri dari Google Sheets
# Muat Turun Data Agihan Juri dari Google Sheets (Secara Spesifik)
# 2. Muat Turun Data Agihan Juri dari Google Sheets (Guna range 'A:C')
try:
    df_agihan = conn.read(worksheet="Agihan", range="A:C", ttl=10)
    df_agihan.dropna(how="all", inplace=True) # Buang baris kosong
except Exception as e:
    st.error(f"⚠️ Ralat membaca helaian 'Agihan': {e}")
    st.stop()
# Sidebar: Pilihan Nama Juri & Poster Dinamik
st.sidebar.header("📋 Maklumat Penjurian")

# Drop-down 1: Nama Juri
senarai_juri = ["-- Pilih Nama Juri --"] + list(df_agihan["Nama Juri"].unique())
nama_juri_pilihan = st.sidebar.selectbox("Pilih Nama Juri", senarai_juri)

id_poster_pilihan = None
tajuk_poster = ""

if nama_juri_pilihan != "-- Pilih Nama Juri --":
    # Tapis senarai poster milik juri yang dipilih sahaja
    df_juri_poster = df_agihan[df_agihan["Nama Juri"] == nama_juri_pilihan]
    
    # Drop-down 2: ID Poster
    senarai_poster = ["-- Pilih ID Poster --"] + list(df_juri_poster["ID Poster"].unique())
    id_poster_pilihan = st.sidebar.selectbox("Pilih ID / Kod Poster", senarai_poster)
    
    # Paparan Tajuk Poster Automatik
    if id_poster_pilihan and id_poster_pilihan != "-- Pilih ID Poster --":
        tajuk_poster = df_juri_poster[df_juri_poster["ID Poster"] == id_poster_pilihan]["Tajuk Poster"].values[0]
        st.sidebar.markdown(f"**Tajuk / Institusi:**\n\n*{tajuk_poster}*")

# 3. Kriteria Rubrik Pemarkahan (13 Kriteria)
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

if not nama_juri_pilihan or nama_juri_pilihan == "-- Pilih Nama Juri --" or not id_poster_pilihan or id_poster_pilihan == "-- Pilih ID Poster --":
    st.info("👈 Sila pilih **Nama Juri** dan **ID Poster** di bar sampingan (Sidebar) terlebih dahulu untuk membuka borang pemarkahan.")
else:
    # Papar info poster yang sedang dijuri
    st.success(f"📌 **Menjuri:** {id_poster_pilihan} | **Tajuk:** {tajuk_poster} | **Juri:** {nama_juri_pilihan}")
    
    with st.form("borang_penjurian"):
        markah_input = {}
        total_score = 0.0

        col_k, col_m = st.columns([3, 1])
        col_k.markdown("**Kriteria Pemarkahan**")
        col_m.markdown("**Markah Juri**")
        st.markdown("---")

        for kriteria, max_mark in rubrik:
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{kriteria}** *(Maks: {max_mark})*")
            score = c2.number_input(
                label=f"Markah {kriteria}",
                min_value=0.0,
                max_value=float(max_mark),
                step=0.5,
                key=f"{id_poster_pilihan}_{kriteria}",
                label_visibility="collapsed"
            )
            total_score += score

        st.markdown("---")

        # Penentuan Pingat
        if total_score >= 85:
            pingat = "GOLD"
            badge = "🥇 GOLD"
        elif total_score >= 70:
            pingat = "SILVER"
            badge = "🥈 SILVER"
        else:
            pingat = "BRONZE"
            badge = "🥉 BRONZE"

        st.metric(label="Jumlah Markah Keseluruhan (100)", value=f"{total_score} / 100")
        st.subheader(f"Keputusan Pingat: {badge}")

        submitted = st.form_submit_button("Hantar & Simpan Keputusan", use_container_width=True)

        if submitted:
            try:
                # Baca data sedia ada di Rekap
                existing_data = conn.read(worksheet="Rekap", ttl=0)
                
                # Sediakan data baharu
                new_row = pd.DataFrame([{
                    "Nama Juri": nama_juri_pilihan,
                    "ID Poster": id_poster_pilihan,
                    "Tajuk Poster": tajuk_poster,
                    "Jumlah Markah": total_score,
                    "Peratus": f"{total_score}%",
                    "Pingat": pingat
                }])

                # Gabung & simpan ke Google Sheets
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(worksheet="Rekap", data=updated_df)
                
                st.balloons()
                st.success(f"✅ Keputusan penjurian bagi **{id_poster_pilihan}** berjaya disimpan!")
            except Exception as e:
                st.error(f"Ralat semasa menyimpan data: {e}")
