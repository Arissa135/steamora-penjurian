import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman Web
st.set_page_config(page_title="Penjurian Poster STEMORA 2026", layout="wide", page_icon="🏆")

st.title("🏆 Platform Penjurian Poster Kajian Tindakan STEMORA 2026")
st.write("Sila pilih nama anda di bar sampingan (sidebar) untuk memulakan pemarkahan.")
st.markdown("---")

# 2. Pautan CSV Google Sheets Anda (Direct Export Link)
SHEET_ID = "1sfwaqs4owcMfzf5f99d0YcuVS4AZNgQ99Pbh72m0obA"
URL_AGIHAN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Agihan"

# 3. Baca Data Agihan Juri
@st.cache_data(ttl=10)
def load_data_agihan():
    df = pd.read_csv(URL_AGIHAN)
    df = df.dropna(how="all").iloc[:, :3]
    df.columns = ["Nama Juri", "ID Poster", "Tajuk Poster"]
    return df

try:
    df_agihan = load_data_agihan()
except Exception as e:
    st.error(f"⚠️ Ralat membaca data dari Google Sheets: {e}")
    st.info("Pastikan tetapan Google Sheets disetkan kepada 'Anyone with the link can view/edit'.")
    st.stop()

# 4. Kawasan Sidebar (Drop-down Dinamik)
st.sidebar.header("📋 Maklumat Penjurian")

# Drop-down 1: Pilih Nama Juri
senarai_juri = ["-- Pilih Nama Juri --"] + sorted(list(df_agihan["Nama Juri"].astype(str).unique()))
nama_juri_pilihan = st.sidebar.selectbox("Pilih Nama Juri", senarai_juri)

id_poster_pilihan = None
tajuk_poster = ""

if nama_juri_pilihan != "-- Pilih Nama Juri --":
    df_juri_poster = df_agihan[df_agihan["Nama Juri"] == nama_juri_pilihan]
    
    # Drop-down 2: Pilih ID Poster
    senarai_poster = ["-- Pilih ID Poster --"] + list(df_juri_poster["ID Poster"].astype(str).unique())
    id_poster_pilihan = st.sidebar.selectbox("Pilih ID / Kod Poster", senarai_poster)
    
    # Papar Tajuk Poster
    if id_poster_pilihan and id_poster_pilihan != "-- Pilih ID Poster --":
        match_tajuk = df_juri_poster[df_juri_poster["ID Poster"] == id_poster_pilihan]["Tajuk Poster"].values
        if len(match_tajuk) > 0:
            tajuk_poster = match_tajuk[0]
            st.sidebar.markdown(f"**Tajuk / Institusi:**\n\n*{tajuk_poster}*")

# 5. Rubrik Pemarkahan (13 Kriteria - Susunan Baharu)
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

# 6. Borang Pemarkahan Juri
st.subheader("📝 Borang Pemarkahan Juri")

if not nama_juri_pilihan or nama_juri_pilihan == "-- Pilih Nama Juri --" or not id_poster_pilihan or id_poster_pilihan == "-- Pilih ID Poster --":
    st.info("👈 Sila pilih **Nama Juri** dan **ID Poster** di bar sampingan (Sidebar) terlebih dahulu.")
else:
    st.success(f"📌 **Menjuri:** {id_poster_pilihan} | **Juri:** {nama_juri_pilihan}")
    
    with st.form("borang_penjurian"):
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

        submitted = st.form_submit_button("Hantar & Semak Keputusan", use_container_width=True)

        if submitted:
            st.balloons()
            st.success(f"✅ Keputusan penjurian bagi **{id_poster_pilihan}** disahkan!")
            st.write(f"**Ringkasan Data:** Juri: {nama_juri_pilihan} | ID: {id_poster_pilihan} | Markah: {total_score} | Pingat: {pingat}")
