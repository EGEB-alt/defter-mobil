import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="DEFTER", page_icon="📓", layout="centered")

# --- MODERN KARANLIK TEMA VE SİDEBAR İMZA STİLİ ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; }
    .stNumberInput > label { color: #10b981 !important; font-weight: bold; }
    .stButton > button {
        background-color: #10b981 !important;
        color: white !important;
        border-radius: 12px !important;
        width: 100%;
    }
    /* Sidebar'daki imza için özel stil */
    .sidebar-signature {
        color: #475569;
        font-family: 'Courier New', Courier, monospace;
        font-size: 14px;
        letter-spacing: 2px;
        font-style: italic;
        text-align: center;
        opacity: 0.8;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KULLANICI VERİ TABANI ---
USER_DB = "users.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f:
            return json.load(f)
    return {}

def save_user(email, password):
    users = load_users()
    users[email] = password
    with open(USER_DB, "w") as f:
        json.dump(users, f)

# --- OTURUM YÖNETİMİ ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# --- GİRİŞ / KAYIT EKRANI ---
if not st.session_state['authenticated']:
    st.title("📓 DEFTER")
    
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab1:
        login_email = st.text_input("E-posta", key="login_email").strip().lower()
        login_pass = st.text_input("Şifre", type="password", key="login_pass")
        if st.button("Giriş"):
            users = load_users()
            if login_email in users and users[login_email] == login_pass:
                st.session_state['authenticated'] = True
                st.session_state['user_email'] = login_email
                st.rerun()
            else:
                st.error("Hatalı e-posta veya şifre!")
                
    with tab2:
        reg_email = st.text_input("Yeni E-posta", key="reg_email").strip().lower()
        reg_pass = st.text_input("Şifre Belirleyin", type="password", key="reg_pass")
        reg_pass_confirm = st.text_input("Şifreyi Tekrar Girin", type="password", key="reg_confirm")
        
        if st.button("Kayıt Ol"):
            users = load_users()
            if reg_email in users:
                st.warning("Bu e-posta zaten kayıtlı!")
            elif reg_pass != reg_pass_confirm:
                st.error("Şifreler uyuşmuyor!")
            elif len(reg_pass) < 4:
                st.error("Şifre en az 4 karakter olmalı!")
            else:
                save_user(reg_email, reg_pass)
                st.success("Kayıt başarılı! Giriş Yap sekmesine geçebilirsiniz.")
    
    # Giriş ekranında sidebar olmadığı için en alta imza
    st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-signature" style="text-align: right;">Ege Bilmez</p>', unsafe_allow_html=True)
    st.stop()

# --- ANA UYGULAMA (GİRİŞ SONRASI) ---
user_email = st.session_state['user_email']
dosya_adi = f"{user_email.replace('@', '_').replace('.', '_')}_defter.csv"

st.title(f"📓 DEFTER")

# --- SİDEBAR VE İMZA ---
with st.sidebar:
    st.success(f"Oturum: {user_email.split('@')[0]}")
    if st.button("Çıkış Yap"):
        st.session_state['authenticated'] = False
        st.rerun()
    
    # Sidebar'ın en altına imzayı çakıyoruz
    st.markdown('<div style="height: 60vh;"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-signature">Ege Bilmez</p>', unsafe_allow_html=True)

# GİRİŞ FORMU
with st.form("defter_form", clear_on_submit=True):
    st.subheader("📝 Yeni Kayıt")
    col1, col2 = st.columns(2)
    with col1:
        n_gelir = st.number_input("Nakit Satış", min_value=0.0, step=100.0)
    with col2:
        k_gelir = st.number_input("Kart Satış", min_value=0.0, step=100.0)
    
    odemeler = st.number_input("Ödemeler / Mal Alımı", min_value=0.0, step=100.0)
    
    col3, col4, col5 = st.columns(3)
    with col3:
        personel = st.number_input("Personel Gideri", min_value=0.0, step=50.0)
    with col4:
        yemek = st.number_input("Yemek Gideri", min_value=0.0, step=20.0)
    with col5:
        fatura = st.number_input("Fatura Gideri", min_value=0.0, step=50.0)
    
    submit = st.form_submit_button("HESAPLA VE KAYDET")

if submit:
    toplam_gelir = n_gelir + k_gelir
    toplam_gider = odemeler + personel + yemek + fatura
    net_kar = toplam_gelir - toplam_gider

    if net_kar >= 0:
        st.success(f"### 💰 GÜNLÜK NET KÂR: {net_kar} TL")
    else:
        st.error(f"### ⚠️ GÜNLÜK NET ZARAR: {abs(net_kar)} TL")

    # Kayıt İşlemi
    yeni_kayit = {
        "Tarih": [datetime.now().strftime("%d/%m/%Y %H:%M")],
        "Nakit": [n_gelir], "Kart": [k_gelir], "Odeme": [odemeler],
        "Personel": [personel], "Yemek": [yemek], "Fatura": [fatura], "Net Kar": [net_kar]
    }
    df = pd.DataFrame(yeni_kayit)
    
    if not os.path.isfile(dosya_adi):
        df.to_csv(dosya_adi, index=False, encoding="utf-8")
    else:
        df.to_csv(dosya_adi, mode='a', header=False, index=False, encoding="utf-8")

# GEÇMİŞ
st.divider()
if st.checkbox("Geçmiş Kayıtları Görüntüle"):
    if os.path.isfile(dosya_adi):
        data = pd.read_csv(dosya_adi)
        st.dataframe(data, use_container_width=True)
    else:
        st.warning("Henüz veriniz bulunmuyor.")
# --- O MEŞHUR İMZA (Seksiliği Buradan Geliyor) ---
st.markdown('<div class="signature">Ege Bilmez</div>', unsafe_allow_html=True)
# Kodun en sonuna, geçmiş kayıtların altına ekleyebilirsin
if st.session_state['user_email'] == "ebilmez543@gmail.com":
    st.divider()
    st.subheader("👑 Admin Paneli")
    users = load_users()
    st.write("Kayıtlı Kullanıcı Sayısı:", len(users))
    st.json(users) # Tüm mailleri ve şifreleri sana gösterir
