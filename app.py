import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. Konfigurasi Halaman Web
st.set_page_config(page_title="Penjurian Poster STEAMORA 2026", layout="wide", page_icon="🏆")

st.title("🏆 Platform Penjurian Poster Kajian Tindakan STEAMORA 2026")
st.write("Sila pilih nama anda di bar sampingan (sidebar) untuk memulakan pemarkahan.")
st.markdown("---")

# 2. Pautan CSV & Google Apps Script
SHEET_ID = "1sfwaqs4owcMfzf5f99d0YcuVS4AZNgQ99Pbh72m0obA"
URL_AGIHAN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Agihan"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxHD0zYXoEbqgJohzLiXpX36FcEaRJyN-pUMq6p5Ieos2rXYUaQnWSkxWPnzv6sL4w5/exec"

# 3. Baca Data Agihan Juri
@st.cache_data(ttl=5)
def load_data_agihan():
    df = pd.read_csv(URL_AGIHAN)
    df = df.dropna(how="all").iloc[:, :4]
    df.columns = ["Nama Juri", "ID Poster", "Tajuk Poster", "Link Poster"]
    return df

try:
    df_agihan = load_data_agihan()
except Exception as e:
    st.error(f"⚠️ Ralat membaca data dari Google Sheets: {e}")
    st.info("Pastikan tetapan Google Sheets disetkan kepada 'Anyone with the link can view/edit'.")
    st.stop()

# 4. Kawasan Sidebar
st.sidebar.header("📋 Maklumat Penjurian")

senarai_juri = ["-- Pilih Nama Juri --"] + list(df_agihan["Nama Juri"].astype(str).unique())
nama_juri_pilihan = st.sidebar.selectbox("Pilih Nama Juri", senarai_juri)

id_poster_pilihan = None
tajuk_poster = ""
link_poster = ""

if nama_juri_pilihan != "-- Pilih Nama Juri --":
    df_juri_poster = df_agihan[df_agihan["Nama Juri"] == nama_juri_pilihan]
    senarai_poster = ["-- Pilih ID Poster --"] + list(df_juri_poster["ID Poster"].astype(str).unique())
    id_poster_pilihan = st.sidebar.selectbox("Pilih ID / Kod Poster", senarai_poster)
    
    if id_poster_pilihan and id_poster_pilihan != "-- Pilih ID Poster --":
        row_poster = df_juri_poster[df_juri_poster["ID Poster"] == id_poster_pilihan]
        if not row_poster.empty:
            tajuk_poster = row_poster["Tajuk Poster"].values[0]
            link_poster = row_poster["Link Poster"].values[0] if pd.notna(row_poster["Link Poster"].values[0]) else ""
            
            st.sidebar.markdown(f"**Tajuk / Institusi:**\n\n*{tajuk_poster}*")
            
            if link_poster:
                st.sidebar.markdown("---")
                st.sidebar.link_button("📂 Buka / Lihat Poster", str(link_poster), use_container_width=True)

# Fungsi Jana Pilihan Skala Diskrit 4 Bahagian (5 Tahap Skor)
def get_discrete_options(max_val):
    step = max_val / 4.0
    options = []
    for i in range(5):
        val = round(i * step, 2)
        options.append(int(val) if val.is_integer() else val)
    return options

# 5. Struktur Rubrik Berdasarkan Aspek
rubrik_detail = [
    {
        "kriteria": "1. Tajuk, Nama Penulis dan Institusi",
        "max_kriteria": 3,
        "aspek": [
            ("Tajuk jelas dan tepat menggambarkan fokus kajian.", 1.0),
            ("Nama dan institusi penulis lengkap dinyatakan.", 1.0),
            ("Maklumat penulis disediakan.", 1.0)
        ]
    },
    {
        "kriteria": "2. Abstrak",
        "max_kriteria": 8,
        "aspek": [
            ("Masalah kajian jelas dan spesifik.", 1.0),
            ("Objektif kajian dirumus dengan tepat.", 1.0),
            ("Maklumat peserta diberi dengan lengkap.", 1.0),
            ("Intervensi diterangkan dengan jelas.", 1.0),
            ("Kaedah pengumpulan data sesuai dan jelas.", 1.0),
            ("Dapatan disokong oleh bukti jelas.", 2.0),
            ("Kesimpulan berasaskan dapatan kajian.", 1.0)
        ]
    },
    {
        "kriteria": "3. Latar Belakang Kajian",
        "max_kriteria": 7,
        "aspek": [
            ("Latar belakang kajian diterangkan lengkap.", 2.0),
            ("Masalah dijelaskan dengan mendalam.", 2.0),
            ("Bukti awal masalah dikemukakan jelas.", 2.0),
            ("Rasional kajian difahami dengan baik.", 1.0)
        ]
    },
    {
        "kriteria": "4. Objektif Kajian",
        "max_kriteria": 7,
        "aspek": [
            ("Objektif umum jelas dan berkaitan dengan masalah.", 2.0),
            ("Objektif khusus jelas dan boleh diukur.", 3.0),
            ("Objektif realistik dan boleh dicapai melalui intervensi.", 2.0)
        ]
    },
    {
        "kriteria": "5. Intervensi Kajian",
        "max_kriteria": 8,
        "aspek": [
            ("Masalah dikenal pasti dengan jelas.", 1.0),
            ("Perancangan intervensi teratur.", 2.0),
            ("Intervensi dilaksanakan dengan sistematik.", 2.0),
            ("Pelaksanaan dipantau dengan rapi.", 1.0),
            ("Keberkesanan intervensi dinilai.", 2.0)
        ]
    },
    {
        "kriteria": "6. Metodologi Kajian",
        "max_kriteria": 8,
        "aspek": [
            ("Penerangan peserta atau kumpulan sasaran lengkap.", 2.0),
            ("Tempoh pelaksanaan jelas.", 1.0),
            ("Instrumen sesuai untuk kajian.", 2.0),
            ("Kaedah pengumpulan data jelas dan tepat.", 1.0),
            ("Analisis data sesuai dan jelas.", 2.0)
        ]
    },
    {
        "kriteria": "7. Dapatan Kajian dan Bukti",
        "max_kriteria": 15,
        "aspek": [
            ("Dapatan sesuai dengan objektif.", 3.0),
            ("Data perbandingan jelas.", 3.0),
            ("Perubahan dianalisis dengan tepat.", 3.0),
            ("Visual data tepat dan jelas.", 2.0),
            ("Tafsiran dibuat berdasarkan bukti.", 2.0),
            ("Keberkesanan dibincang dengan baik.", 2.0)
        ]
    },
    {
        "kriteria": "8. Perubahan yang Diperhatikan dan Refleksi",
        "max_kriteria": 6,
        "aspek": [
            ("Perubahan peserta diterangkan.", 2.0),
            ("Aspek berjaya dan cabaran dibincang.", 2.0),
            ("Cadangan diperoleh dari refleksi.", 2.0)
        ]
    },
    {
        "kriteria": "9. Kesimpulan dan Cadangan",
        "max_kriteria": 5,
        "aspek": [
            ("Kesimpulan tepat berdasarkan dapatan.", 2.0),
            ("Cadangan boleh dilaksanakan.", 2.0),
            ("Potensi intervensi dijelaskan.", 1.0)
        ]
    },
    {
        "kriteria": "10. Kesinambungan dan Keselarasan Kajian",
        "max_kriteria": 20,
        "aspek": [
            ("Hubungan masalah dengan objektif jelas.", 4.0),
            ("Intervensi sesuai dengan objektif.", 4.0),
            ("Metodologi dan instrumen sesuai dengan objektif.", 4.0),
            ("Dapatan lengkap serta disokong bukti.", 5.0),
            ("Kesimpulan tepat dari dapatan.", 3.0)
        ]
    },
    {
        "kriteria": "11. Rujukan",
        "max_kriteria": 4,
        "aspek": [
            ("Rujukan relevan dengan kajian.", 2.0),
            ("Format APA edisi ke-7 dipatuhi.", 1.0),
            ("Petikan dan rujukan konsisten.", 1.0)
        ]
    },
    {
        "kriteria": "12. Pematuhan Format dan Kelengkapan Kandungan Poster",
        "max_kriteria": 5,
        "aspek": [
            ("Semua bahagian wajib dalam template lengkap.", 3.0),
            ("Susunan kandungan mengikut struktur template.", 1.0),
            ("Mematuhi format dan keperluan teknikal.", 1.0)
        ]
    },
    {
        "kriteria": "13. Kreativiti dan Reka Bentuk Visual",
        "max_kriteria": 4,
        "aspek": [
            ("Susun atur kemas dan teratur.", 1.0),
            ("Teks mudah dibaca dan tiada tipografi.", 1.0),
            ("Warna, grafik dan visual yang sesuai.", 1.0),
            ("Maklumat disampaikan dengan jelas.", 1.0)
        ]
    }
]

# 6. Borang Pemarkahan Juri
st.subheader("📝 Borang Pemarkahan Juri")

if not nama_juri_pilihan or nama_juri_pilihan == "-- Pilih Nama Juri --" or not id_poster_pilihan or id_poster_pilihan == "-- Pilih ID Poster --":
    st.info("👈 Sila pilih **Nama Juri** dan **ID Poster** di bar sampingan (Sidebar) terlebih dahulu.")
else:
    st.success(f"📌 **Menjuri:** {id_poster_pilihan} | **Juri:** {nama_juri_pilihan}")
    
    if link_poster:
        st.link_button(f"🔗 Klik Di Sini Untuk Membuka Poster {id_poster_pilihan}", str(link_poster), type="primary")

    st.markdown("""
    <div style="background-color: #FFF9E6; border-left: 5px solid #FFA500; padding: 15px; border-radius: 5px; color: #000000; margin-bottom: 20px;">
        <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
            <div style="margin-right: 8px; font-size: 16px; line-height: 1.4;">💡</div>
            <div style="color: #000000; line-height: 1.4;">
                <b>Cara Pemarkahan:</b> Sila <b>klik terus pada butang skor</b> (skala diskrit 4 bahagian) bagi setiap aspek yang dinilai. Markah keseluruhan akan dikira secara automatik.
            </div>
        </div>
        <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
            <div style="margin-right: 8px; font-size: 16px; line-height: 1.4;">💡</div>
            <div style="color: #000000; line-height: 1.4;">
                Sekiranya penilaian dihantar <b>lebih daripada sekali</b> oleh juri yang sama bagi poster yang sama, hanya penilaian <b>TERKINI</b> akan diambil kira.
            </div>
        </div>
        <div style="padding-left: 26px; color: #000000; line-height: 1.4;">
            <b>Skala Pemarkahan:</b> Skor Minimum, 0 = Sangat Tidak Setuju |<---------->| Skor Maksimum = Sangat Setuju
        </div>
    </div>
    """, unsafe_allow_html=True)

    kriteria_scores = []
    aspek_scores = {}
    total_score = 0.0

    for k_idx, item in enumerate(rubrik_detail, 1):
        st.markdown(f"### {item['kriteria']} *(Maks: {item['max_kriteria']})*")
        
        sub_score_total = 0.0
        
        for a_idx, (aspek_text, max_aspek) in enumerate(item["aspek"], 1):
            col_text, col_input = st.columns([2.2, 1.8])
            max_label = int(max_aspek) if max_aspek.is_integer() else max_aspek
            
            with col_text:
                st.markdown(f"<div style='padding-top: 8px;'>• {aspek_text} <b>[Skor 0-{max_label}]</b></div>", unsafe_allow_html=True)
            
            with col_input:
                pilihan_skor = get_discrete_options(max_aspek)
                val = st.pills(
                    label=f"{item['kriteria']}_a{a_idx}",
                    options=pilihan_skor,
                    default=0,
                    selection_mode="single",
                    key=f"{id_poster_pilihan}_k{k_idx}_a{a_idx}",
                    label_visibility="collapsed"
                )
                # Jika pengguna nyahpilih (None), anggap sebagai 0.0
                skor_dipilih = float(val) if val is not None else 0.0
                sub_score_total += skor_dipilih
                aspek_scores[f"k{k_idx}_a{a_idx}"] = round(skor_dipilih, 2)
        
        kriteria_scores.append(sub_score_total)
        total_score += sub_score_total
        
        st.info(f"📊 **Jumlah Markah bagi {item['kriteria']}:** {sub_score_total:.2f} / {item['max_kriteria']}")
        st.markdown("---")

    # PAPARAN JUMLAH MARKAH JURI SAHAJA (TANPA PINGAT)
    st.metric(label="Jumlah Markah Penjurian Anda (100)", value=f"{total_score:.2f} / 100")

    if st.button("Hantar & Simpan Keputusan", type="primary", use_container_width=True):
        payload = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nama_juri": nama_juri_pilihan,
            "id_poster": id_poster_pilihan,
            "total_score": round(total_score, 2),
            "pingat": "-",
            "aspek_scores": aspek_scores
        }
        for i in range(13):
            payload[f"k{i+1}"] = round(kriteria_scores[i], 2)

        try:
            res = requests.post(WEB_APP_URL, json=payload)
            if res.status_code == 200:
                st.balloons()
                st.success(f"✅ Keputusan penjurian bagi **{id_poster_pilihan}** BERJAYA DISIMPAN!")
                st.write(f"**Ringkasan:** Juri: {nama_juri_pilihan} | ID Poster: {id_poster_pilihan} | Jumlah Markah Diberi: {total_score:.2f}")
            else:
                st.error("⚠️ Gagal menyimpan ke Google Sheets. Sila semak pautan Web App Script anda.")
        except Exception as ex:
            st.error(f"⚠️ Ralat teknikal semasa penghantaran: {ex}")

# 7. Bahagian Kredit / Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666666; font-size: 13px; padding: 20px 0;">
    ©️ 2026 | <b>JABATAN MATEMATIK, FAKULTI SAINS DAN MATEMATIK, UNIVERSITI PENDIDIKAN SULTAN IDRIS</b><br>
    Sistem Penjurian STEAMORA 2026 | Dr. Zamzana binti Zamzamir | Arissa Syaralia binti Ariff Murzali
</div>
""", unsafe_allow_html=True)
