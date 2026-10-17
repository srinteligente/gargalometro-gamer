import streamlit as st
import json
import os
import re

# Identifica o ícone visual na pasta
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

# Carrega os bancos de dados JSON (Hardware e Links Afiliados)
@st.cache_data
def carregar_dados():
    with open("banco_hardware_completo.json", "r", encoding="utf-8") as f:
        dados_hw = json.load(f)
    
    # Carrega links externos se existirem
    dados_links = {}
    if os.path.exists("links.json"):
        with open("links.json", "r", encoding="utf-8") as f:
            dados_links = json.load(f)
            
    return dados_hw, dados_links

db, LINKS = carregar_dados()

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
            
        if "8065S" in gpu_int or "495" in u:
            return True, 6.0, "Radeon 8065S (40 CUs - Nível de GPU potente)"
        if "8050S" in gpu_int or "490" in u or "485" in u:
            return True, 5.4, "Radeon 8050S (32 CUs - Desempenho gráfico elevado)"
        if "890M" in gpu_int or "475" in u or "470" in u:
            return True, 5.0, "Radeon 890M (16 CUs - Excelente para competitivos e leves)"
        if "780M" in gpu_int or "8700G" in u or "260" in u or "250" in u or "180" in u:
            return True, 4.8, "Radeon 780M (Roda competitivos e lançamentos em 1080p)"
        if "680M" in gpu_int or "170" in u or "160" in u:
            return True, 4.2, "Radeon 680M (Ótimo desempenho em 1080p para iGPU)"
        if "760M" in gpu_int or "8600G" in u or "230" in u or "165" in u:
            return True, 4.0, "Radeon 760M"
        if "660M" in gpu_int or "150" in u or "130" in u or "110" in u:
            return True, 3.2, "Radeon 660M"
        if "5700G" in u or "5600G" in u or "5600GT" in u:
            return True, 2.9, "Radeon Vega 7 Integrada (Jogos leves: Valorant, CS2, GTA V)"
        if "3400G" in u or "2400G" in u:
            return True, 2.7, "Radeon Vega 11 Integrada"
        if "3200G" in u or "2200G" in u:
            return True, 2.4, "Radeon Vega 8 Integrada"
        if "4600G" in u or "4650G" in u or "4300G" in u:
            return True, 2.7, "Radeon Vega 6/7 Integrada"
        if eh_zen4_ou_novo:
            return True, 2.0, "RDNA 2 Básica Integrada (Apenas vídeo básico)"
        return True, 2.5, "Gráficos Integrados AMD Radeon"

    if "INTEL" in u:
        if any(g in u for g in ["12", "13", "14", "ULTRA"]):
            return True, 2.4, "Intel UHD 770 / Iris Xe Integrada"
        return True, 1.8, "Intel HD / UHD Graphics Básica"
        
    return True, 1.8, "Vídeo Integrado Básico"

# Topo do Programa
header_col1, header_col2 = st.columns([1, 8])
with header_col1:
    if nome_icone:
        st.image(nome_icone, width=90)
with header_col2:
    st.title("Gargalômetro Gamer")
    st.caption(f"Avaliador de Equilíbrio & Ranking (0 a 10) • Base: {len(db['gpus'])} GPUs e {len(db['cpus'])} CPUs")

st.divider()

col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.subheader("Configuração da Máquina")

    tipo_dispositivo = st.radio(
        "Tipo de Máquina",
        options=["🖥️ Desktop", "💻 Notebook"],
        horizontal=True
    )
    eh_notebook = tipo_dispositivo == "💻 Notebook"

    if eh_notebook:
        gpu_lista = [g["nome"] for g in db["gpus"] if g.get("notebook", False)]
        gpu_opcoes = ["Nenhuma (Gráficos Integrados / APU)"] + gpu_lista
        padrao_gpu_idx = next((i for i, n in enumerate(gpu_opcoes) if "RTX 4050 Mobile" in n or "4050" in n), 0)
    else:
        gpu_lista = [g["nome"] for g in db["gpus"] if g.get("desktop", True)]
        gpu_opcoes = ["Nenhuma (Gráficos Integrados / APU)"] + gpu_lista
        padrao_gpu_idx = next((i for i, n in enumerate(gpu_opcoes) if "RTX 5060" in n or "RTX 4060" in n), 0)

    gpu_sel = st.selectbox("Placa de Vídeo (GPU)", gpu_opcoes, index=padrao_gpu_idx)

    if eh_notebook:
        cpu_lista = [c["nome"] for c in db["cpus"] if c.get("notebook", False)]
        padrao_cpu_idx = next((i for i, n in enumerate(cpu_lista) if "Ryzen 7 170" in n or "7735" in n or "13700H" in n), 0)
    else:
        cpu_lista = [c["nome"] for c in db["cpus"] if c.get("desktop", True)]
        padrao_cpu_idx = next((i for i, n in enumerate(cpu_lista) if "Ryzen 5 5600" in n and "5600G" not in n), 0)

    cpu_sel = st.selectbox("Processador (CPU)", cpu_lista, index=padrao_cpu_idx)
    cpu_obj = next(c for c in db["cpus"] if c["nome"] == cpu_sel)

    resolucao_sel = st.radio(
        "Resolução Principal de Jogo",
        options=["1080p (Full HD)", "1440p (Quad HD)", "4K (Ultra HD)"],
        horizontal=True
    )

    c1, c2 = st.columns(2)
    with c1:
        ram_opcoes = {
            "2 GB DDR2 (Legado Extremo)": 1.0,
            "4 GB DDR2 (Básico Antigo)": 1.5,
            "4 GB DDR3 (Entrada Básica DDR3)": 2.0,
            "8 GB DDR3 (Obsoleto)": 2.8,
            "16 GB DDR3 (Defasado)": 3.5,
            "8 GB DDR4 (Apertado)": 4.0,
            "16 GB DDR4 (Básico Atual)": 6.0,
            "32 GB DDR4 (Confortável DDR4)": 7.5,
            "64 GB DDR4 (Sobra em DDR4)": 8.0,
            "16 GB DDR5 (Entrada Nova Geração)": 7.0,
            "32 GB DDR5 (Padrão Ouro Atual)": 9.0,
            "64 GB DDR5 (Topo Absoluto)": 10.0,
            "128 GB+ DDR5 (Workstation)": 10.0
        }
        padrao_ram_idx = list(ram_opcoes.keys()).index("16 GB DDR4 (Básico Atual)")
        ram_sel = st.selectbox("Memória RAM", list(ram_opcoes.keys()), index=padrao_ram_idx)
        ram_nota = ram_opcoes[ram_sel]

    with c2:
        ssd_opcoes = {
            "Apenas HD Mecânico (Penalizado)": 2.0,
            "SSD SATA (240GB - 500GB)": 4.5,
            "512 GB SSD NVMe M.2": 6.0,
            "1 TB SSD NVMe M.2": 7.5,
            "2 TB SSD NVMe Gen4": 9.0,
            "4 TB+ SSD NVMe Gen4 / Gen5 (Topo)": 10.0
        }
        padrao_ssd_idx = list(ssd_opcoes.keys()).index("1 TB SSD NVMe M.2")
        ssd_sel = st.selectbox("Armazenamento Principal", list(ssd_opcoes.keys()), index=padrao_ssd_idx)
        ssd_nota = ssd_opcoes[ssd_sel]

    if not eh_notebook:
        fonte_w = st.slider("Fonte de Alimentação (Watts)", min_value=300, max_value=1600, value=650, step=50)
    else:
        fonte_w = 230

    jogar_gta = st.checkbox("🎮 Pretendo jogar GTA VI nesta máquina", value=True)

# Identificação de Vídeo Integrado
usando_igpu = (gpu_sel == "Nenhuma (Gráficos Integrados / APU)")
tem_igpu, nota_igpu, msg_igpu = detectar_video_integrado(cpu_obj)

if usando_igpu:
    if tem_igpu:
        gpu_obj = {"nome": f"Gráficos Integrados ({msg_igpu})", "nota": nota_igpu, "tdp": 15}
    else:
        gpu_obj = {"nome": "SEM VÍDEO (Processador não possui iGPU)", "nota": 0.5, "tdp": 0}
else:
    gpu_obj = next(g for g in db["gpus"] if g["nome"] == gpu_sel)

# Cálculos Ponderados
fonte_nota = min(10.0, (fonte_w / 1200) * 10) if not eh_notebook else 8.5
nota_calculada = (gpu_obj["nota"] * 0.50) + (cpu_obj["nota"] * 0.25) + (ram_nota * 0.15) + (ssd_nota * 0.05) + (fonte_nota * 0.05)

penalidade_hd = 0.2 if "Apenas HD Mecânico" in ssd_sel else 0.0
nota_final = max(1.0, min(10.0, nota_calculada - penalidade_hd))

consumo_estimado = gpu_obj["tdp"] + cpu_obj["tdp"] + (40 if eh_notebook else 75)
fonte_recomendada = consumo_estimado * 1.35

pesos_resolucao = {
    "1080p (Full HD)": 0.80,
    "1440p (Quad HD)": 1.10,
    "4K (Ultra HD)":   1.50
}

eh_xeon = "XEON" in cpu_obj["nome"].upper()
fator_xeon = 1.0
if eh_xeon and resolucao_sel == "1080p (Full HD)" and gpu_obj["nota"] >= 5.0:
    fator_xeon = 0.65

fps_potencial_gpu = gpu_obj["nota"] / pesos_resolucao[resolucao_sel]
fps_potencial_cpu = (cpu_obj["nota"] * fator_xeon) / 0.85

if fps_potencial_gpu > fps_potencial_cpu:
    pct_gargalo = ((fps_potencial_gpu - fps_potencial_cpu) / fps_potencial_gpu) * 100.0
    componente_limitante = "Processador (CPU)"
else:
    pct_gargalo = ((fps_potencial_cpu - fps_potencial_gpu) / fps_potencial_cpu) * 100.0
    componente_limitante = "Placa de Vídeo (GPU)"

pct_gargalo = round(min(100.0, max(0.0, pct_gargalo)), 1)

with col_right:
    st.subheader("Resultado & Diagnóstico")
    
    st.metric(label="Nota Geral do Setup", value=f"{nota_final:.1f} / 10.0")
    st.progress(min(1.0, max(0.0, nota_final / 10.0)))

    st.write(f"• **GPU:** Nota {gpu_obj['nota']:.1f} ({gpu_obj['tdp']}W)")
    st.write(f"• **CPU:** Nota {cpu_obj['nota']:.1f} ({cpu_obj['tdp']}W)")
    st.write(f"• **RAM:** Nota {ram_nota:.1f} ({ram_sel.split(' ')[2]})")
    st.write(f"• **Armazenamento:** Nota {ssd_nota:.1f}")
    if not eh_notebook:
        st.write(f"• **Fonte:** Nota {fonte_nota:.1f} ({fonte_w}W)")

    if usando_igpu:
        if not tem_igpu:
            st.error(f"🚨 **SEM VÍDEO!** O processador `{cpu_obj['nome']}` não possui placa gráfica integrada.")
        else:
            st.info(f"🖥️ **Vídeo Integrado Ativo:** {msg_igpu}.")

    if penalidade_hd > 0:
        st.warning("⚠️ **Penalização Aplicada (-0.2):** O uso exclusivo de HD mecânico causa travamentos em jogos modernos.")

    if "DDR2" in ram_sel:
        st.error("🚨 **Memória DDR2:** Arquitetura obsoleta. Incompatível com jogos modernos.")
    elif "DDR3" in ram_sel:
        st.warning("⚠️ **Memória DDR3:** Plataforma defasada.")

    if not eh_notebook:
        st.markdown("---")
        if fonte_w < consumo_estimado:
            st.error(f"🚨 **Fonte insuficiente:** Consumo estimado é de ~{consumo_estimado}W e sua fonte tem {fonte_w}W!")
        elif fonte_w < fonte_recomendada:
            st.warning(f"⚠️ **Pouca folga:** Recomendável pelo menos {int(fonte_recomendada)}W.")
        else:
            st.success("✅ **Alimentação segura.**")

    st.markdown("---")
    st.subheader("Análise de Gargalo por Resolução")

    if eh_xeon and resolucao_sel == "1080p (Full HD)" and gpu_obj["nota"] >= 5.0:
        if nome_icone:
            st.image(nome_icone, width=200)
        st.error("🚨 **GARGALO DE XEON EM FULL HD DETECTADO!**")
        st.write(f"**Gargalo estimado de
