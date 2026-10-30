import streamlit as st
import json
import os
import re
import urllib.request
import urllib.parse

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
    page_title="Gargalômetro Gamer - Calculadora de Gargalo de PC e Setup",
    page_icon=nome_icone if nome_icone else "🖥️",
    layout="wide"
)

st.markdown("""
    <style>
        /* 1. Oculta navegação lateral nativa e botões */
        [data-testid="stSidebarNav"], 
        button[data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }

        /* 2. MATA A MOLDURA BRANCA/CINZA DO MODO EMBED */
        .stAppEmbedded, 
        div[data-testid="stAppViewContainer"] > section,
        .main,
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            background: transparent !important;
        }

        /* 3. Remove restrição de altura que cria scroll duplo */
        iframe, body, html {
            height: 100% !important;
        }

        /* 4. Ajuste responsivo para tela vertical (<= 1050px) */
        @media (max-width: 1050px) {
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 2rem !important;
                padding-left: 0.8rem !important;
                padding-right: 0.8rem !important;
                max-width: 100% !important;
            }
            [data-testid="stHorizontalBlock"] {
                flex-wrap: wrap !important;
            }
            .stButton button, .stLinkButton a {
                width: 100% !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Injeção de Meta Tags de SEO e Google Search Console
st.markdown("""
    <head>
        <meta name="description" content="Descubra se o seu processador limita sua placa de vídeo. Calculadora precisa de gargalo (bottleneck) para PC Desktop e Notebook Gamer.">
        <meta name="keywords" content="calculadora de gargalo, bottleneck calculator pc, gargalômetro, teste gargalo gpu cpu, gta vi requisitos pc">
        <meta name="robots" content="index, follow">
        <meta property="og:title" content="Gargalômetro Gamer - Calculadora de Gargalo CPU e GPU">
        <meta property="og:description" content="Avalie o equilíbrio do seu setup gamer de 0 a 10 e veja testes de prontidão para jogos pesados.">
        <meta property="og:url" content="https://gargalometro.com.br/">
        <meta property="og:type" content="website">
    </head>
""", unsafe_allow_html=True)

# 1. Hardware pesado fica em cache para o site abrir rápido
@st.cache_data
def carregar_hardware():
    arquivos_hw = [
        "banco_hardware_completo.json",
        "hardware.json",
        "dados.json",
        "banco.json",
        "cpus_gpus.json"
    ]
    for nome in arquivos_hw:
        if os.path.exists(nome):
            try:
                with open(nome, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    if isinstance(dados, dict) and "gpus" in dados and "cpus" in dados:
                        return dados
            except Exception as e:
                st.error(f"Erro ao ler {nome}: {e}")
    return {"gpus": [], "cpus": []}

# 2. Vitrine SEM cache para atualizar no F5 sempre que você mudar o vitrine.json
def carregar_vitrine():
    for nome in ["vitrine.json", "vitrine_4.json", "links.json"]:
        if os.path.exists(nome):
            try:
                with open(nome, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Erro ao ler {nome}: {e}")
    return {}

db = carregar_hardware()
VITRINE = carregar_vitrine()

def renderizar_botoes_em_colunas(itens):
    """Gera botões organizados automaticamente em 2 colunas"""
    if not itens:
        return
    c1, c2 = st.columns(2)
    for i, item in enumerate(itens):
        col = c1 if i % 2 == 0 else c2
        with col:
            st.link_button(item["texto"], item["url"], use_container_width=True)

def classificar_plataforma_cpu(nome_cpu):
    u = nome_cpu.upper()
    
    if any(x in u for x in ["XEON", "FX-", "PHENOM", "ATHLON", "CORE2", "OPTERON", "SEMPRON", "A10-", "A8-", "A6-", "A4-"]):
        return "DEFASADA"
    
    m_intel_5d = re.search(r'I[3579]-(\d{2})\d{3}', u)
    if m_intel_5d:
        gen = int(m_intel_5d.group(1))
        if gen in [10, 11]:
            return "DEFASADA"
        elif 12 <= gen <= 14:
            return "LGA1700"

    if re.search(r'I[3579]-(\d)\d{3}', u) or re.search(r'I[3579]-\d{3}\b', u):
        return "DEFASADA"

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
        if any(f" {g}" in u for g in ["7500", "7600", "7700", "7800", "7900", "7950", "8400", "8500", "8600", "8700", "9600", "9700", "9800", "9900", "9950"]):
            return "AM5"

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
    if "7500F" in u or "9500F" in u or "9700F" in u or "5500F" in u or "8400F" in u or "8700F" in u:
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

# Cabeçalho
header_col1, header_col2 = st.columns([1, 8])
with header_col1:
    if nome_icone:
        st.image(nome_icone, width=90)
with header_col2:
    st.title("Gargalômetro Gamer")
    
    st.markdown(
        """
        <div style="margin-top: -10px; margin-bottom: 8px;">
            <a href="https://www.tiktok.com/@srinteligente.shop" target="_blank" style="text-decoration: none; font-weight: 700; font-size: 1.05rem; color: #ff0050;">
                📱 Siga nosso perfil no TikTok (@srinteligente.shop) 🚀
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.caption(f"Avaliador de Equilíbrio & Ranking (0 a 10) • Base: {len(db.get('gpus', []))} GPUs e {len(db.get('cpus', []))} CPUs")

st.divider()

# BOTÃO ÚNICO E DESTACADO: MONTE SEU PC GAMER
st.markdown("""
    <style>
        div[data-testid="stPageLink-NavLink"] {
            background: linear-gradient(90deg, #1e293b, #0f172a) !important;
            border: 2px solid #ff4b4b !important;
            border-radius: 12px !important;
            padding: 16px 20px !important;
            text-align: center !important;
            justify-content: center !important;
            box-shadow: 0 4px 15px rgba(255, 75, 75, 0.25) !important;
            transition: all 0.2s ease-in-out !important;
        }
        div[data-testid="stPageLink-NavLink"]:hover {
            border-color: #ff2b2b !important;
            box-shadow: 0 0 22px rgba(255, 75, 75, 0.45) !important;
            transform: scale(1.01) !important;
        }
        div[data-testid="stPageLink-NavLink"] p,
        div[data-testid="stPageLink-NavLink"] span {
            font-size: 1.4rem !important;
            font-weight: 800 !important;
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

st.page_link(
    "pages/monte_seu_pc.py", 
    label="🛠️🎯 Monte seu PC GAMER no GARGALÔMETRO", 
    use_container_width=True
)

st.divider()

st.markdown("<br>", unsafe_allow_html=True)

# ========================================================
# 🚨 ACHADOS DO DIA DINÂMICOS (LÊ VITRINE.JSON)
# ========================================================
achados = VITRINE.get("achados_do_dia", [])
if achados:
    st.markdown("#### ⚡ Achados do Dia com Menor Preço Histórico:")
    colunas_achados = st.columns(len(achados))
    for idx, achado in enumerate(achados):
        with colunas_achados[idx]:
            with st.container(border=True):
                st.markdown(f"##### {achado.get('titulo', 'Oferta Imperdível')}")
                st.caption(achado.get('descricao', ''))
                st.link_button(achado.get('texto_botao', 'Conferir Oferta'), achado.get('url', '#'), use_container_width=True)

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
        gpu_lista = [g["nome"] for g in db.get("gpus", []) if g.get("notebook", False)]
        gpu_opcoes = ["Nenhuma (Gráficos Integrados / APU)"] + gpu_lista
        padrao_gpu_idx = next((i for i, n in enumerate(gpu_opcoes) if "RTX 4080 Mobile" in n or "4080" in n or "4060" in n), 0)
    else:
        gpu_lista = [g["nome"] for g in db.get("gpus", []) if g.get("desktop", True)]
        gpu_opcoes = ["Nenhuma (Gráficos Integrados / APU)"] + gpu_lista
        padrao_gpu_idx = next((i for i, n in enumerate(gpu_opcoes) if "RTX 5060" in n or "RTX 4060" in n), 0)

    gpu_sel = st.selectbox("Placa de Vídeo (GPU)", gpu_opcoes, index=padrao_gpu_idx if padrao_gpu_idx < len(gpu_opcoes) else 0)

    if eh_notebook:
        cpu_lista = [c["nome"] for c in db.get("cpus", []) if c.get("notebook", False)]
        padrao_cpu_idx = next((i for i, n in enumerate(cpu_lista) if "13700H" in n or "Ryzen 7 170" in n or "7735" in n), 0)
    else:
        cpu_lista = [c["nome"] for c in db.get("cpus", []) if c.get("desktop", True)]
        padrao_cpu_idx = next((i for i, n in enumerate(cpu_lista) if "Ryzen 5 5600" in n and "5600G" not in n), 0)

    cpu_sel = st.selectbox("Processador (CPU)", cpu_lista, index=padrao_cpu_idx if padrao_cpu_idx < len(cpu_lista) else 0)
    cpu_obj = next((c for c in db.get("cpus", []) if c["nome"] == cpu_sel), {"nome": cpu_sel, "nota": 5.0, "tdp": 65})

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
            "16 GB DDR4 (Básico Atual)": 6.5,
            "32 GB DDR4 (Confortável DDR4)": 8.0,
            "48 GB DDR4 (Capacidade Alta DDR4)": 8.3,
            "64 GB DDR4 (Sobra em DDR4)": 8.5,
            "16 GB DDR5 (Entrada Nova Geração)": 7.5,
            "32 GB DDR5 (Padrão Ouro Atual)": 9.5,
            "48 GB DDR5 (Alta Performance 2x24GB)": 9.8,
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
        fonte_w = 280

    jogar_gta = st.checkbox("🎮 Pretendo jogar GTA VI nesta máquina", value=True)

usando_igpu = (gpu_sel == "Nenhuma (Gráficos Integrados / APU)")
tem_igpu, nota_igpu, msg_igpu = detectar_video_integrado(cpu_obj)

if usando_igpu:
    if tem_igpu:
        gpu_obj = {"nome": f"Gráficos Integrados ({msg_igpu})", "nota": nota_igpu, "tdp": 15}
    else:
        gpu_obj = {"nome": "SEM VÍDEO (Processador não possui iGPU)", "nota": 0.5, "tdp": 0}
else:
    gpu_obj = next((g for g in db.get("gpus", []) if g["nome"] == gpu_sel), {"nome": gpu_sel, "nota": 5.0, "tdp": 120})

# ========================================================
# ⚖️ CÁLCULO DE NOTA RECALIBRADO (DESKTOP & NOTEBOOK)
# ========================================================
if eh_notebook:
    nota_calculada = (gpu_obj["nota"] * 0.60) + (cpu_obj["nota"] * 0.30) + (ram_nota * 0.07) + (ssd_nota * 0.03)
    fonte_nota = 9.5
else:
    fonte_nota = min(10.0, (fonte_w / 1200) * 10)
    nota_calculada = (gpu_obj["nota"] * 0.50) + (cpu_obj["nota"] * 0.25) + (ram_nota * 0.15) + (ssd_nota * 0.05) + (fonte_nota * 0.05)

penalidade_hd = 0.5 if "Apenas HD Mecânico" in ssd_sel else 0.0
nota_final = max(1.0, min(10.0, nota_calculada - penalidade_hd))

consumo_estimado = gpu_obj["tdp"] + cpu_obj["tdp"] + (35 if eh_notebook else 75)
fonte_recomendada = consumo_estimado * 1.35

# ========================================================
# 🎯 CÁLCULO DE GARGALO CALIBRADO (PADRÃO DE MERCADO)
# ========================================================
pesos_resolucao = {
    "1080p (Full HD)": 1.00,
    "1440p (Quad HD)": 1.25,
    "4K (Ultra HD)":   1.60
}

eh_xeon = "XEON" in cpu_obj["nome"].upper()
fator_xeon = 1.0
if eh_xeon and resolucao_sel == "1080p (Full HD)" and gpu_obj["nota"] >= 5.0:
    fator_xeon = 0.65

fps_potencial_gpu = gpu_obj["nota"] / pesos_resolucao[resolucao_sel]
fps_potencial_cpu = (cpu_obj["nota"] * fator_xeon) / 1.00

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
    st.write(f"• **RAM:** Nota {ram_nota:.1f} ({ram_sel.split(' ')[0]} GB)")
    st.write(f"• **Armazenamento:** Nota {ssd_nota:.1f}")
    if not eh_notebook:
        st.write(f"• **Fonte:** Nota {fonte_nota:.1f} ({fonte_w}W)")
    else:
        st.caption("⚡ Notebook Gamer: gerenciamento de energia e arrefecimento integrado de fábrica.")

    if usando_igpu:
        if not tem_igpu:
            st.error(f"🚨 **SEM VÍDEO!** O processador `{cpu_obj['nome']}` não possui placa gráfica integrada.")
        else:
            st.info(f"🖥️ **Vídeo Integrado Ativo:** {msg_igpu}.")

    if penalidade_hd > 0:
        st.warning("⚠️ **Penalização Aplicada (-0.5):** O uso exclusivo de HD mecânico causará congelamentos em jogos modernos.")

    if "DDR2" in ram_sel:
        st.error("🚨 **Memória DDR2:** Arquitetura obsoleta. Incompatível com jogos modernos.")
    elif "DDR3" in ram_sel:
        st.warning("⚠️ **Memória DDR3:** Plataforma defasada.")

    if not eh_notebook:
        st.markdown("---")
        if fonte_w < consumo_estimado:
            st.error(f"🚨 **Fonte insuficiente:** Consumo estimado é de ~{consumo_estimado}W e a sua fonte tem {fonte_w}W!")
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
        st.write(f"**Gargalo estimado de CPU:** `{pct_gargalo}%`")
        st.progress(min(1.0, pct_gargalo / 100.0))
        st.write(f"O seu **{cpu_obj['nome']}** limita a **{gpu_obj['nome']}** em 1080p devido a clock e IPC antigos.")
        
    elif pct_gargalo >= 20.0 and componente_limitante == "Processador (CPU)":
        if nome_icone:
            st.image(nome_icone, width=200)
        st.error(f"🚨 **GARGALO DETECTADO EM {resolucao_sel.upper()}!**")
        st.write(f"**Gargalo estimado de CPU:** `{pct_gargalo}%`")
        st.progress(min(1.0, pct_gargalo / 100.0))
        st.write(f"O seu **{cpu_obj['nome']}** limita expressivamente a **{gpu_obj['nome']}**.")
        
    elif pct_gargalo >= 25.0 and componente_limitante == "Placa de Vídeo (GPU)":
        st.info(f"💡 **Limite Gráfico em {resolucao_sel}:** Gargalo natural de GPU de `{pct_gargalo}%`.")
        st.write("A placa gráfica trabalhará a 99%/100% de uso, o comportamento esperado em jogos pesados.")
        
    else:
        st.success(f"🎯 **Setup Perfeitamente Equilibrado em {resolucao_sel}!**")
        st.write(f"Variação estimada de apenas `{pct_gargalo}%`. O processador e a placa de vídeo trabalham em harmonia.")

    # ========================================================
    # 🌴 TESTE DE PRONTIDÃO: GTA VI (CORRIGIDO)
    # ========================================================
    if jogar_gta:
        st.markdown("---")
        st.subheader("🌴 Teste de Prontidão: GTA VI")
        tem_hd = "Apenas HD Mecânico" in ssd_sel
        gpu_n = gpu_obj["nota"]
        cpu_n = cpu_obj["nota"]
        
        m_ram = re.search(r'(\d+)\s*GB', ram_sel)
        gb_ram = int(m_ram.group(1)) if m_ram else 16

        gpu_nome_u = gpu_obj["nome"].upper()
        gpu_eh_8gb_gddr6 = any(x in gpu_nome_u for x in ["2060 SUPER", "2060S", "6600", "3060", "4060", "7600", "5050", "3070", "4070", "4080", "4090", "5060", "5070", "5080"])
        
        if usando_igpu:
            st.error("❌ **INCOMPATÍVEL COM GTA VI:** Exigirá GPU dedicada com VRAM física.")
        elif tem_hd:
            st.error("❌ **INCOMPATÍVEL COM GTA VI (Armazenamento):** Exige SSD obrigatoriamente.")
        elif gb_ram < 16:
            st.error(f"❌ **MEMÓRIA RAM INSUFICIENTE ({gb_ram} GB):** GTA VI exigirá no mínimo 16 GB.")
        elif (gpu_n < 4.2 and not gpu_eh_8gb_gddr6) or cpu_n < 3.8:
            st.error(f"⚠️ **ABAIXO DO MÍNIMO ESTIMADO:** GPU ({gpu_n:.1f}) / CPU ({cpu_n:.1f}).")
        elif gpu_n >= 7.8 and cpu_n >= 7.0 and gb_ram >= 16:
            st.balloons()
            st.success("👑 **PRONTO PARA O ALTO / ULTRA EM ALTA TAXA DE FPS!** A sua máquina roda com folga.")
        elif (gpu_n >= 5.8 or gpu_eh_8gb_gddr6) and cpu_n >= 5.0 and gb_ram >= 16:
            st.success("✅ **CONFIGURAÇÃO RECOMENDADA ATENDIDA (60 FPS 1080p/1440p).**")
        else:
            st.warning("⚠️ **CONFIGURAÇÃO MÍNIMA ATENDIDA (1080p 30-45+ FPS em qualidade Normal).**")

    # ========================================================
    # 💰 HUB DE UPGRADE 100% DINÂMICO (LÊ VITRINE.JSON)
    # ========================================================
    st.markdown("---")
    st.subheader("🛒 Melhores Ofertas de Upgrade")

    plat_atual = classificar_plataforma_cpu(cpu_obj["nome"])
    ram_antiga = ("DDR2" in ram_sel) or ("DDR3" in ram_sel)
    precisa_trocar_plataforma = (plat_atual == "DEFASADA") or ram_antiga

    kits = VITRINE.get("kits_upgrade", [])
    if precisa_trocar_plataforma and kits:
        st.markdown("##### 🛠️ Migração de Plataforma Recomendada (Kits com Placa-Mãe + CPU + Cooler):")
        st.info(
            f"💡 A sua plataforma atual ({cpu_obj['nome']}) opera com barramentos ou IPC antigos. "
            "A saída inteligente é migrar para um kit novo:"
        )
        renderizar_botoes_em_colunas(kits)

    # Processadores por Aba Dinâmica
    cpus_dict = VITRINE.get("cpus", {})
    if cpus_dict:
        st.markdown("##### ⚡ Processadores Recomendados por Plataforma:")
        abas_cpu = st.tabs(list(cpus_dict.keys()))
        for idx, (nome_aba, dados) in enumerate(cpus_dict.items()):
            with abas_cpu[idx]:
                if "cupom" in dados and dados["cupom"]:
                    st.caption(dados["cupom"])
                renderizar_botoes_em_colunas(dados.get("itens", []))

    # Placas-Mãe por Aba Dinâmica
    mbs_dict = VITRINE.get("placas_mae", {})
    if mbs_dict:
        st.markdown("##### 🧩 Placas-Mãe Recomendadas:")
        abas_mb = st.tabs(list(mbs_dict.keys()))
        for idx, (nome_aba, dados) in enumerate(mbs_dict.items()):
            with abas_mb[idx]:
                if "cupom" in dados and dados["cupom"]:
                    st.caption(dados["cupom"])
                renderizar_botoes_em_colunas(dados.get("itens", []))

    # Placas de Vídeo por Aba Dinâmica
    gpus_dict = VITRINE.get("gpus", {})
    if gpus_dict:
        st.markdown("##### 🎮 Placas de Vídeo Recomendadas para Jogos Modernos:")
        abas_gpu = st.tabs(list(gpus_dict.keys()))
        for idx, (nome_aba, dados) in enumerate(gpus_dict.items()):
            with abas_gpu[idx]:
                if "cupom" in dados and dados["cupom"]:
                    st.caption(dados["cupom"])
                renderizar_botoes_em_colunas(dados.get("itens", []))

# ========================================================
# 💼 CONSULTORIA PERSONALIZADA DE SETUP (R$ 20,00) VIA WHATSAPP
# ========================================================
st.markdown("---")
st.subheader("🎯 Consultoria VIP para Montagem de PC")

with st.container(border=True):
    col_info, col_form = st.columns([1, 1.2])
    
    with col_info:
        st.markdown("### Monte o PC Perfeito Sem Errar!")
        st.write(
            "Quer ajuda personalizada para escolher as melhores peças dentro do seu orçamento, "
            "evitar gargalos e garantir as melhores ofertas do dia?"
        )
        st.markdown("#### **Valor simbólico: R$ 20,00**")
        st.caption("Receba uma lista balanceada de peças sob medida direto no seu WhatsApp.")
        
        st.info(
            "📱 **Como funciona:**\n\n"
            "1. Preencha seus dados ao lado.\n"
            "2. Clique em **Gerar Pedido no WhatsApp**.\n"
            "3. O WhatsApp abrirá com tudo preenchido para iniciarmos a montagem!"
        )

    with col_form:
        with st.form("form_consultoria_zap"):
            nome_cli = st.text_input("Seu Nome:")
            zap_cli = st.text_input("Seu WhatsApp (com DDD):", placeholder="(61) 99999-9999")
            orcamento_cli = st.text_input("Quanto pretende investir no total (R$)?", placeholder="Ex: R$ 3.500,00")
            msg_cli = st.text_area(
                "O que pretende jogar ou trabalhar?", 
                placeholder="Ex: Quero jogar Warzone e GTA VI em 1080p, preciso apenas do gabinete completo."
            )
            
            btn_gerar = st.form_submit_button("🚀 Gerar Pedido de Consultoria (R$ 20,00)", use_container_width=True)
            
        if btn_gerar:
            if not zap_cli.strip() or not orcamento_cli.strip():
                st.warning("⚠️ Por favor, informe pelo menos o seu WhatsApp e o orçamento disponível.")
            else:
                texto_msg = f"""Olá Sr. Inteligente! Gostaria de contratar a Consultoria VIP (R$ 20,00):
━━━━━━━━━━━━━━━━━━━━
👤 *Nome:* {nome_cli.strip() if nome_cli.strip() else 'Não informado'}
📱 *WhatsApp:* {zap_cli.strip()}
💰 *Orçamento:* {orcamento_cli.strip()}
🎯 *Foco / Jogos:* {msg_cli.strip() if msg_cli.strip() else 'Gabinete completo'}
━━━━━━━━━━━━━━━━━━━━
Aguardo orientações para o Pix e início da montagem!"""
                
                texto_codificado = urllib.parse.quote(texto_msg)
                
                # Substitua pelo seu número com DDI 55 + DDD (apenas números)
                NUMERO_MEU_ZAP = "5561985587047"
                
                link_whatsapp = f"https://api.whatsapp.com/send?phone={NUMERO_MEU_ZAP}&text={texto_codificado}"
                
                st.success("✅ Pedido pronto! Clique no botão abaixo para enviar no WhatsApp:")
                st.link_button(
                    "📲 Enviar Pedido no WhatsApp do Sr. Inteligente", 
                    link_whatsapp, 
                    type="primary", 
                    use_container_width=True
                )
