import streamlit as st
import json
import os
import re

# ========================================================
# 🛒 CENTRAL DE LINKS DE AFILIADOS & CUPONS REAIS
# (Apenas produtos com links fornecidos)
# ========================================================
LINKS = {
    # TikTok Shop & Vitrine Principal
    "tiktok_shop": "https://www.tiktok.com",

    # --- PROCESSADORES AMD ---
    # Ryzen 5 5500
    "r5_5500_ml": "https://meli.la/2QN5Pgh",          # Cupons: SITE50, OFFHOJE
    "r5_5500_amazon": "https://link.amazon/B0arOOyDV",
    "r5_5500_kabum": "https://tidd.ly/4dLyVMO",

    # Ryzen 5 5500X3D
    "r5_5500x3d_ml": "https://meli.la/1auyhNC",
    "r5_5500x3d_shopee": "https://s.shopee.com.br/7fafWPpbIM?share_channel_code=1",

    # Ryzen 5 5600X
    "r5_5600x_amazon": "https://link.amazon/B0eGWwc2v",

    # Ryzen 7 5700 & 5700X
    "r7_5700_shopee": "https://s.shopee.com.br/80DVu4Gy5Z?share_channel_code=1",
    "r7_5700x_amazon": "https://link.amazon/B089kG1h5",
    "r7_5700x_kabum": "https://tidd.ly/4jsw27b",

    # Ryzen 7 5800XT & 5800X3D
    "r7_5800xt_kabum": "https://tidd.ly/4yYLn4m",     # Cupom: CPUAGORA
    "r7_5800x3d_kabum": "https://tidd.y/4s7Amem",     # Cupom: CPUAGORA
    "r7_5800x3d_ml": "https://meli.la/1MKXidT",

    # --- PROCESSADORES INTEL (LGA 1700) ---
    "intel_i5_14600kf_kabum": "https://tidd.ly/4BbqRit",  # Cupom: CPUAGORA
    "intel_i5_14600k_kabum": "https://tidd.ly/4hRz57N",   # Cupom: CPUAGORA

    # --- KITS COMPLETOS (PLACA-MÃE + CPU + COOLER) ---
    "kit_5500f_mach1": "https://tidd.ly/4jZfG6b",      # MSI A520M-A PRO + R5 5500F (PCIe 4.0) + Air Cooler MACH1
    "kit_5500f_risemode": "https://tidd.ly/47oNTVy",   # MSI A520M-A PRO + R5 5500F (PCIe 4.0) + Rise Mode G700
    "kit_5700x_watercooler": "https://tidd.ly/3TXWsn6", # MSI B550M WiFi6E + R7 5700X + Water Cooler 240mm

    # --- PLACAS DE VÍDEO (GPUS) ---
    "gpu_rx7600_biostar_shopee": "https://s.shopee.com.br/8KqMOFGvEQ?share_channel_code=1",  # Promo R$ 1.800
    "gpu_rx7600_amazon": "https://link.amazon/B06yxGnXR",
    "gpu_rtx3070_kabum": "https://tidd.ly/3VMxBDi",                                           # Husky Alpha RTX 3070 8GB
    "gpu_rx9060xt_shopee": "https://s.shopee.com.br/Lo4rRNbor",                               # PowerColor RX 9060 XT 8GB
    "gpu_rtx5050_shopee": "https://s.shopee.com.br/50ZuNKgIbi?share_channel_code=1",
    "gpu_rtx5060_amazon": "https://link.amazon/B0cIU83OT",
    "gpu_rtx5060ti_shopee": "https://s.shopee.com.br/1W02ClNekQ",
}

# Identifica o ícone visual
nome_icone = None
for arq in [
    "gargalo_detectado_ampliado.webp",
    "gargalo detectado.webp",
    "gargalo_detectado.webp"
]:
    if os.path.exists(arq):
        nome_icone = arq
        break

st.set_page_config(
    page_title="Gargalômetro Gamer",
    page_icon=nome_icone if nome_icone else "🖥️",
    layout="wide"
)

@st.cache_data
def carregar_dados():
    with open("banco_hardware_completo.json", "r", encoding="utf-8") as f:
        return json.load(f)

db = carregar_dados()

def classificar_plataforma_cpu(nome_cpu):
    u = nome_cpu.upper()
    
    # 1. Defasadas (Xeon, FX, Athlon, Core 2, APUs antigas)
    if any(x in u for x in ["XEON", "FX-", "PHENOM", "ATHLON", "CORE2", "OPTERON", "SEMPRON", "A10-", "A8-", "A6-", "A4-"]):
        return "DEFASADA"
    
    # Intel de 10ª e 11ª (LGA 1200) e 12ª a 14ª (LGA 1700)
    m_intel_5d = re.search(r'I[3579]-(\d{2})\d{3}', u)
    if m_intel_5d:
        gen = int(m_intel_5d.group(1))
        if gen in [10, 11]:
            return "DEFASADA"
        elif 12 <= gen <= 14:
            return "LGA1700"

    # Intel de 2ª a 9ª geração (LGA 1155, 1150, 1151)
    if re.search(r'I[3579]-(\d)\d{3}', u) or re.search(r'I[3579]-\d{3}\b', u):
        return "DEFASADA"

    # AMD AM4 e AM5
    if "RYZEN" in u:
        m_ryzen = re.search(r'RYZEN\s+[3579]\s+(\d{4})', u)
        if m_ryzen:
            num = int(m_ryzen.group(1))
            if 1000 <= num < 6000:
                return "AM4"
            elif num >= 7000:
                return "AM5"
        if any(f" {g}" in u for g in ["5500", "5600", "5700", "5800", "5900", "5950", "3600", "2600", "1600"]):
            return "AM4"

    return "OUTRA"

def detectar_video_integrado(cpu_obj):
    nome = cpu_obj["nome"]
    u = nome.upper()
    
    gpu_int = cpu_obj.get("gpu_integrada", "")
    if gpu_int and "Requer placa de vídeo" in gpu_int:
        return False, 0.0, "Requer placa de vídeo dedicada (sem gráficos integrados)."
    
    if "XEON" in u:
        return False, 0.0, "Intel Xeon não possui vídeo integrado."
    if bool(re.search(r'\d{4,5}F\b', u)) or bool(re.search(r'\d{4,5}KF\b', u)):
        return False, 0.0, "Processadores Intel série 'F' / 'KF' não possuem vídeo integrado."
    if "7500F" in u or "9500F" in u or "9700F" in u or "5500F" in u:
        return False, 0.0, f"O {nome} não possui vídeo integrado."
        
    if "RYZEN" in u:
        eh_zen4_ou_novo = any(gen in u for gen in ["7600", "7700", "7800", "7900", "7950", "8500", "8600", "8700", "9600", "9700", "9800", "9900", "9950"])
        eh_mobile = cpu_obj.get("notebook", False) or any(u.endswith(m) or (m + " ") in u for m in ["U", "H", "HS", "HX", "C"])
        eh_g = any(g in u for g in ["G", "GE"])
        
        if not (eh_zen4_ou_novo or eh_mobile or eh_g):
            return False, 0.0, "Processadores Ryzen desktop das séries 1000 a 5000 sem o sufixo 'G' não possuem vídeo integrado."
