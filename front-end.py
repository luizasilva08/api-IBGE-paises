"""Front-end Streamlit – API – Dados de Países.

Este arquivo cuida apenas da interface. Os dados principais vêm do
codigo_original.py (API do IBGE), executado sem alterações. Os dados
complementares (localização no mapa, população, brasão etc.) vêm da
REST Countries API, pois o IBGE não fornece coordenadas geográficas.

Execução:  streamlit run front-end.py
"""

import base64
import html
import re
from functools import lru_cache
from pathlib import Path

import requests
import streamlit as st

try:
    import plotly.graph_objects as go
except ImportError:  # sem plotly, o mapa usa o st.map simples
    go = None

ARQUIVO_ORIGINAL = Path(__file__).parent / "app.py"
URL_COMPLEMENTO = "https://restcountries.com/v3.1/alpha/{}"
COR_DESTAQUE = "#1e6fd0"

# Cores ANSI do terminal (usadas na aba Terminal)
CORES_ANSI = {
    31: "#cd3131", 32: "#0dbc79", 33: "#e5e510",
    34: "#3b8eea", 35: "#bc3fbc", 36: "#11a8cd",
}

# Ícones (traçados no estilo "feather")
ICONES = {
    "globo": '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "area": '<polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/>',
    "lingua": '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>',
    "pino": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    "capital": '<path d="M3 21h18M5 21V10M9 21V10M15 21V10M19 21V10M2 10l10-7 10 7"/>',
    "moeda": '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "busca": '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
    "alerta": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    "info": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
    "livro": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "codigo": '<polyline points="8 6 2 12 8 18"/><polyline points="16 6 22 12 16 18"/>',
    "pessoas": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "relogio": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "fronteira": '<rect x="3" y="3" width="18" height="18" rx="2"/><line x1="12" y1="3" x2="12" y2="21"/>',
    "telefone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "dominio": '<circle cx="12" cy="12" r="4"/><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-3.92 7.94"/>',
    "carro": '<path d="M5 17h14M3 13l2-6h14l2 6v4H3z"/><circle cx="7.5" cy="17" r="1.5"/><circle cx="16.5" cy="17" r="1.5"/>',
    "ondas": '<path d="M2 6c2 0 2 2 4 2s2-2 4-2 2 2 4 2 2-2 4-2 2 2 4 2M2 12c2 0 2 2 4 2s2-2 4-2 2 2 4 2 2-2 4-2 2 2 4 2M2 18c2 0 2 2 4 2s2-2 4-2 2 2 4 2 2-2 4-2 2 2 4 2"/>',
    "bandeira": '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/>',
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
.stApp {font-family: 'Inter', 'Segoe UI', sans-serif; background: #f3f7fb; color: #0f2a4a;}
#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}
.block-container {padding-top: 1.2rem; max-width: 1150px;}

/* Barra superior */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    background: linear-gradient(90deg, #0a2540 0%, #103a63 100%);
    border-radius: 14px; padding: 1.1rem 1.6rem; margin-bottom: 1.2rem;
    box-shadow: 0 6px 20px rgba(10,37,64,.25);
}
.topbar-left {display: flex; align-items: center; gap: 1rem;}
.topbar-title {color: #fff; font-size: 1.45rem; font-weight: 700; line-height: 1.2;}
.topbar-sub {color: #9cc7f0; font-size: .9rem; margin-top: .1rem;}
.topbar-right {opacity: .9;}

/* Menu lateral */
[data-testid="stSidebar"] {background: #ffffff; border-right: 1px solid #e3ecf6;}
[data-testid="stSidebar"] div[role="radiogroup"] {gap: .3rem;}
[data-testid="stSidebar"] div[role="radiogroup"] label {
    width: 100%; padding: .65rem .9rem; border-radius: 10px; cursor: pointer;
}
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {display: none;}
[data-testid="stSidebar"] div[role="radiogroup"] label p {font-weight: 600; color: #4a6785;}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {background: #dbeafe;}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {color: #1565c0;}

/* Cartão de busca */
[data-testid="stForm"], .st-key-form_consulta {
    background: #fff; border: 1px solid #e3ecf6 !important; border-radius: 14px;
    padding: 1.3rem 1.5rem; box-shadow: 0 2px 12px rgba(16,42,80,.05);
}
.busca-titulo {display: flex; align-items: center; gap: .7rem; margin-bottom: .6rem;}
.busca-titulo b {font-size: 1.05rem; color: #0f2a4a;}
.busca-sub {color: #6b829c; font-size: .85rem; margin-top: .1rem;}
.aviso-info {
    background: #eaf3fd; border-radius: 10px; padding: .9rem 1rem; color: #1e4d82;
    font-size: .85rem; line-height: 1.45;
}
.aviso-info b {display: flex; align-items: center; gap: .4rem; margin-bottom: .2rem; color: #1565c0;}
[data-baseweb="select"] > div {background: #fff; border-color: #cbd8e8; border-radius: 10px; min-height: 46px;}
[data-testid="stFormSubmitButton"] button {
    width: 100%; min-height: 46px; background: #1e6fd0; color: #fff; border: 0;
    border-radius: 10px; font-weight: 600;
}
[data-testid="stFormSubmitButton"] button:hover {background: #1858a8; color: #fff;}

/* Avisos */
.banner {
    display: flex; align-items: center; gap: .9rem; border-radius: 12px;
    padding: .9rem 1.2rem; margin: 1.1rem 0; border: 1px solid;
}
.banner.ok {background: #eaf8f1; border-color: #bfe6d3;}
.banner.erro {background: #fdeeee; border-color: #f2c4c4;}
.banner-icon {
    width: 34px; height: 34px; border-radius: 50%; display: flex;
    align-items: center; justify-content: center; flex-shrink: 0;
}
.banner.ok .banner-icon {background: #2e9e6b;}
.banner.erro .banner-icon {background: #d64545;}
.banner-title {font-weight: 700; color: #134e36;}
.banner.erro .banner-title {color: #7a1f1f;}
.banner-sub {font-size: .85rem; color: #4a7a66;}
.banner.erro .banner-sub {color: #8a4a4a;}

/* Cartão do país */
.st-key-cartao_resultado {
    background: #fff; border: 1px solid #e3ecf6; border-radius: 14px;
    padding: 1.4rem 1.5rem; box-shadow: 0 2px 12px rgba(16,42,80,.05);
}
.pais {display: flex; align-items: center; gap: 1.1rem; padding-top: .3rem;}
.flag {height: 62px; border-radius: 6px; box-shadow: 0 3px 10px rgba(0,0,0,.2);}
.pais-nome {font-size: 1.8rem; font-weight: 800; color: #0f2a4a; line-height: 1.1;}
.pais-sigla {color: #6b829c; font-weight: 600; margin-top: .2rem;}
.info-grid {
    display: grid; gap: 14px; margin: 1.1rem 0;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}
.info-card {
    display: flex; align-items: center; gap: .9rem; background: #f2f7fd;
    border: 1px solid #e1ebf7; border-radius: 12px; padding: .9rem 1rem;
}
.info-icon {
    width: 40px; height: 40px; border-radius: 50%; background: #1e88e5;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.info-label {font-size: .78rem; color: #5d7590; font-weight: 500;}
.info-value {font-size: 1.05rem; font-weight: 700; color: #0f2a4a; word-break: break-word;}
.hist-card {
    display: flex; gap: 1rem; background: #f2f7fd; border: 1px solid #e1ebf7;
    border-radius: 12px; padding: 1.1rem 1.2rem;
}
.hist-title {font-weight: 700; color: #0f2a4a; margin-bottom: .4rem;}
.hist-text {margin: 0; line-height: 1.65; color: #334e68; font-size: .92rem;}
.simbolos {display: flex; gap: 2rem; align-items: flex-end; margin: .5rem 0 1.4rem;}
.simbolo {text-align: center;}
.simbolo img {height: 110px; max-width: 220px; object-fit: contain; border-radius: 6px; box-shadow: 0 3px 10px rgba(0,0,0,.15);}
.simbolo div {font-size: .8rem; color: #6b829c; margin-top: .45rem;}
.secao-titulo {font-size: 1.1rem; font-weight: 700; margin: 1.6rem 0 .4rem; color: #0f2a4a;}

/* Estados vazios e página Sobre */
.vazio {
    text-align: center; padding: 2.5rem 1rem; border-radius: 14px; margin-top: 1.1rem;
    border: 2px dashed #c4d4e6; background: #f8fbfe; color: #4a6785;
}
.vazio b {display: block; font-size: 1.15rem; color: #0f2a4a; margin: .6rem 0 .2rem;}
.sobre {
    background: #fff; border: 1px solid #e3ecf6; border-radius: 14px;
    padding: 1.4rem 1.6rem; margin-bottom: 1rem; line-height: 1.65; color: #334e68;
}
.sobre h3 {margin: 0 0 .5rem; color: #0f2a4a; font-size: 1.1rem;}
.sobre ul {margin: .3rem 0 0 1.1rem; padding: 0;}
.rodape {text-align: center; color: #8aa0b8; font-size: .82rem; margin-top: 2rem;}
"""


# ----------------------------------------------------------------------
# Consulta ao código original (IBGE)
# ----------------------------------------------------------------------
class AguardandoEntrada(Exception):
    """Interrompe o script no input() enquanto nenhuma sigla foi digitada."""


def executar_codigo_original(entrada: str):
    """Executa o código original. Devolve (saída_do_terminal, erro, variáveis)."""
    saida = []

    def _print(*args, sep=" ", end="\n", **kwargs):
        saida.append(sep.join(str(a) for a in args) + end)

    def _input(prompt=""):
        saida.append(str(prompt))
        if not entrada:
            raise AguardandoEntrada
        saida.append(entrada + "\n")
        return entrada

    codigo = compile(ARQUIVO_ORIGINAL.read_text(encoding="utf-8"), str(ARQUIVO_ORIGINAL), "exec")
    ambiente = {"__name__": "__main__", "print": _print, "input": _input}

    erro = None
    try:
        exec(codigo, ambiente)
    except AguardandoEntrada:
        pass
    except Exception as e:  # falha de rede, país inexistente, etc.
        erro = f"{type(e).__name__}: {e}"
    return "".join(saida), erro, ambiente


@st.cache_data(show_spinner=False)
def carregar_paises() -> dict:
    """Lê a lista de países definida no código original ({sigla: nome})."""
    _, _, ambiente = executar_codigo_original("")
    paises = {}
    for linha in ambiente.get("paises", "").strip().splitlines():
        sigla, nome = linha.split(" - ", 1)
        paises[sigla.strip()] = nome.strip()
    return paises


CAMPOS_ORIGINAL = ["area", "linguas", "continente", "sub_continente", "capital", "moeda", "historico"]


@st.cache_data(show_spinner=False, ttl=3600)
def consultar(sigla: str) -> dict:
    """Consulta um país (via código original) e devolve apenas dados simples."""
    saida, erro, ambiente = executar_codigo_original(sigla)
    resposta = ambiente.get("resposta")
    return {
        "saida": saida,
        "erro": erro,
        "status": getattr(resposta, "status_code", None),
        "dados": {campo: ambiente.get(campo) for campo in CAMPOS_ORIGINAL},
    }


# ----------------------------------------------------------------------
# Dados complementares (mapa, população, brasão...)
# ----------------------------------------------------------------------
def _coordenadas(valor):
    try:
        return float(valor[0]), float(valor[1])
    except (TypeError, ValueError, IndexError):
        return None


def _simplificar(p: dict) -> dict:
    idd = p.get("idd") or {}
    raiz, sufixos = idd.get("root") or "", idd.get("suffixes") or []
    telefone = (raiz + sufixos[0] if len(sufixos) == 1 else raiz) or None
    maps = p.get("maps") or {}
    return {
        "cca3": p.get("cca3"),
        "coord": _coordenadas(p.get("latlng")),
        "coord_capital": _coordenadas((p.get("capitalInfo") or {}).get("latlng")),
        "area": p.get("area"),
        "populacao": p.get("population"),
        "fusos": p.get("timezones") or [],
        "fronteiras": p.get("borders") or [],
        "tld": p.get("tld") or [],
        "telefone": telefone,
        "direcao": (p.get("car") or {}).get("side"),
        "sem_litoral": p.get("landlocked"),
        "onu": p.get("unMember"),
        "moedas": list((p.get("currencies") or {}).keys()),
        "bandeira": (p.get("flags") or {}).get("png"),
        "brasao": (p.get("coatOfArms") or {}).get("png"),
        "google_maps": maps.get("googleMaps"),
        "osm": maps.get("openStreetMaps"),
    }


@st.cache_data(show_spinner=False, ttl=86400)
def _buscar_complemento(sigla: str) -> dict:
    resposta = requests.get(URL_COMPLEMENTO.format(sigla), timeout=10)
    resposta.raise_for_status()
    dados = resposta.json()
    return _simplificar(dados[0] if isinstance(dados, list) else dados)


def obter_complemento(sigla: str):
    """Devolve os dados complementares ou None se o serviço estiver indisponível."""
    try:
        return _buscar_complemento(sigla)
    except Exception:
        return None  # falhas não ficam em cache; tenta de novo na próxima consulta


# ----------------------------------------------------------------------
# Utilitários de formatação
# ----------------------------------------------------------------------
@lru_cache(maxsize=None)
def icone(nome: str, cor: str = "#ffffff", tamanho: int = 20) -> str:
    """Ícone SVG embutido (data URI) para uso em HTML."""
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
        f'fill="none" stroke="{cor}" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round">{ICONES[nome]}</svg>'
    )
    b64 = base64.b64encode(svg.encode()).decode()
    return f'<img src="data:image/svg+xml;base64,{b64}" width="{tamanho}" height="{tamanho}" alt="">'


def formatar_numero(valor) -> str:
    try:
        return f"{float(str(valor)):,.0f}".replace(",", ".")
    except ValueError:
        return html.escape(str(valor))


def ansi_para_html(texto: str) -> str:
    """Converte os códigos ANSI (\\033[0XXm ... \\033[m) em <span> coloridos."""
    texto = html.escape(texto)
    aberto = False

    def trocar(m):
        nonlocal aberto
        codigo = int(m.group(1) or 0)
        fechar = "</span>" if aberto else ""
        aberto = False
        cor = CORES_ANSI.get(codigo)
        if cor:
            aberto = True
            return f'{fechar}<span style="color:{cor}">'
        return fechar

    resultado = re.sub(r"\x1b\[(\d*)m", trocar, texto)
    return resultado + ("</span>" if aberto else "")


def escala_do_mapa(area) -> float:
    """Zoom do mapa plano conforme o tamanho do país."""
    try:
        area = float(area)
    except (TypeError, ValueError):
        return 6
    for limite, escala in ((5e6, 2.2), (1e6, 4), (2e5, 7), (5e4, 12), (1e4, 22)):
        if area > limite:
            return escala
    return 40


# ----------------------------------------------------------------------
# Componentes visuais
# ----------------------------------------------------------------------
def aplicar_estilo() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def exibir_barra_superior() -> None:
    st.markdown(
        '<div class="topbar"><div class="topbar-left">'
        f'{icone("globo", "#3b9cff", 44)}'
        '<div><div class="topbar-title">API – Dados de Países</div>'
        '<div class="topbar-sub">Consulte informações sobre países utilizando a API do IBGE.</div></div>'
        f'</div><div class="topbar-right">{icone("codigo", "#3b9cff", 24)}</div></div>',
        unsafe_allow_html=True,
    )


def menu_lateral() -> str:
    with st.sidebar:
        pagina = st.radio(
            "Navegação",
            ["Consulta", "Sobre"],
            format_func=lambda p: {"Consulta": "🏠  Consulta", "Sobre": "ℹ️  Sobre"}[p],
            label_visibility="collapsed",
        )
    return pagina


def formulario_consulta(paises: dict):
    """Cartão de busca. Devolve a sigla consultada (mantida entre execuções)."""
    with st.form("form_consulta", border=False):
        col_busca, col_aviso = st.columns([2.4, 1])
        with col_busca:
            st.markdown(
                '<div class="busca-titulo">'
                f'{icone("busca", "#1e6fd0", 26)}'
                '<div><b>Escolha um país para consultar</b>'
                '<div class="busca-sub">Você pode digitar o nome do país ou a sigla (ex: BR, US, PT).</div></div>'
                "</div>",
                unsafe_allow_html=True,
            )
            col_campo, col_botao = st.columns([3, 1.1])
            escolha = col_campo.selectbox(
                "País",
                options=list(paises.keys()),
                index=None,
                placeholder="Digite o nome ou a sigla do país...",
                format_func=lambda s: f"{s} - {paises[s]}",
                label_visibility="collapsed",
            )
            enviado = col_botao.form_submit_button("🔍  Consultar país", type="primary")
        col_aviso.markdown(
            '<div class="aviso-info">'
            f'<b>{icone("info", "#1565c0", 18)} Países disponíveis</b>'
            "Você pode consultar qualquer um dos países listados na API do IBGE."
            "</div>",
            unsafe_allow_html=True,
        )

    if enviado:
        if escolha:
            st.session_state["consulta"] = escolha
        else:
            st.warning("Selecione um país para consultar.")
    return st.session_state.get("consulta")


def exibir_estado_inicial(total: int) -> None:
    st.markdown(
        f'<div class="vazio">{icone("globo", "#1e6fd0", 44)}'
        "<b>Nenhum país consultado ainda</b>"
        f"Escolha um dos {total} países disponíveis e clique em “Consultar país”."
        "</div>",
        unsafe_allow_html=True,
    )


def exibir_aviso(sucesso: bool, titulo: str, subtitulo: str) -> None:
    classe, nome_icone = ("ok", "check") if sucesso else ("erro", "alerta")
    st.markdown(
        f'<div class="banner {classe}"><div class="banner-icon">{icone(nome_icone, "#ffffff", 20)}</div>'
        f'<div><div class="banner-title">{html.escape(titulo)}</div>'
        f'<div class="banner-sub">{html.escape(subtitulo)}</div></div></div>',
        unsafe_allow_html=True,
    )


def exibir_cartoes(itens: list) -> None:
    """itens: lista de (rótulo, valor_html, nome_do_ícone)."""
    cartoes = "".join(
        f'<div class="info-card"><div class="info-icon">{icone(ic)}</div>'
        f'<div><div class="info-label">{rotulo}</div><div class="info-value">{valor}</div></div></div>'
        for rotulo, valor, ic in itens
    )
    st.markdown(f'<div class="info-grid">{cartoes}</div>', unsafe_allow_html=True)


def cartoes_principais(dados: dict, comp) -> list:
    def txt(campo):
        valor = dados.get(campo)
        return html.escape(str(valor)) if valor not in (None, "") else "Não informado"

    area = dados.get("area")
    moeda = txt("moeda")
    if comp and dados.get("moeda") and len(comp["moedas"]) == 1:
        moeda += f" ({html.escape(comp['moedas'][0])})"
    return [
        ("Área total", f"{formatar_numero(area)} km²" if area not in (None, "") else "Não informado", "area"),
        ("Língua", txt("linguas"), "lingua"),
        ("Continente", txt("continente"), "globo"),
        ("Sub-região", txt("sub_continente"), "pino"),
        ("Capital do país", txt("capital"), "capital"),
        ("Moeda", moeda, "moeda"),
    ]


def cartoes_extras(comp: dict) -> list:
    fusos = comp["fusos"]
    fusos_txt = ", ".join(fusos[:3]) + (f" (+{len(fusos) - 3})" if len(fusos) > 3 else "") if fusos else "Não informado"
    fronteiras = comp["fronteiras"]
    fronteiras_txt = f"{len(fronteiras)}: {', '.join(fronteiras)}" if fronteiras else "Nenhuma fronteira terrestre"
    direcao = {"right": "Mão direita", "left": "Mão esquerda"}.get(comp["direcao"], "Não informado")
    return [
        ("População", formatar_numero(comp["populacao"]) if comp["populacao"] else "Não informado", "pessoas"),
        ("Fuso(s) horário(s)", html.escape(fusos_txt), "relogio"),
        ("Fronteiras", html.escape(fronteiras_txt), "fronteira"),
        ("Código telefônico", html.escape(comp["telefone"] or "Não informado"), "telefone"),
        ("Domínio na internet", html.escape(", ".join(comp["tld"]) or "Não informado"), "dominio"),
        ("Direção no trânsito", direcao, "carro"),
        ("Litoral", "Sem acesso ao mar" if comp["sem_litoral"] else "Com acesso ao mar", "ondas"),
        ("ONU", "Membro da ONU" if comp["onu"] else "Não é membro da ONU", "bandeira"),
    ]


def exibir_cabecalho_pais(sigla: str, nome: str, comp) -> None:
    bandeira = (comp or {}).get("bandeira") or f"https://flagcdn.com/w160/{sigla.lower()}.png"
    st.markdown(
        '<div class="pais">'
        f'<img class="flag" src="{html.escape(bandeira)}" alt="Bandeira de {html.escape(nome)}">'
        f'<div><div class="pais-nome">{html.escape(nome)}</div>'
        f'<div class="pais-sigla">{html.escape(sigla)}</div></div></div>',
        unsafe_allow_html=True,
    )


def montar_miniatura(comp: dict):
    """Mini-mapa do país destacado em azul (canto do cartão)."""
    lat, lon = comp["coord"]
    fig = go.Figure(go.Choropleth(
        locations=[comp["cca3"]], locationmode="ISO-3", z=[1], hoverinfo="skip",
        colorscale=[[0, COR_DESTAQUE], [1, COR_DESTAQUE]], showscale=False,
        marker_line_color="#ffffff", marker_line_width=0.6,
    ))
    try:
        pequeno = float(comp["area"]) < 20000
    except (TypeError, ValueError):
        pequeno = False
    if pequeno:  # países minúsculos ficam invisíveis; marca com um ponto
        fig.add_trace(go.Scattergeo(lat=[lat], lon=[lon], mode="markers", hoverinfo="skip",
                                    marker=dict(size=8, color="#ef4444")))
    escala = max(1.2, min(escala_do_mapa(comp["area"]) * 0.55, 6))
    fig.update_layout(
        geo=dict(projection_type="natural earth", center=dict(lat=lat, lon=lon), projection_scale=escala,
                 showland=True, landcolor="#d6e0ee", showcountries=True, countrycolor="#ffffff",
                 showcoastlines=False, showocean=False, showlakes=False, showframe=False,
                 bgcolor="rgba(0,0,0,0)"),
        height=190, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
    )
    return fig


def montar_figura(nome: str, capital, comp: dict, globo: bool):
    """Mapa interativo grande (globo 3D ou mapa plano)."""
    lat, lon = comp["coord"]
    mlat, mlon = comp["coord_capital"] or comp["coord"]
    fig = go.Figure()
    fig.add_trace(go.Choropleth(
        locations=[comp["cca3"]], locationmode="ISO-3", z=[1], text=[nome], hoverinfo="text",
        colorscale=[[0, COR_DESTAQUE], [1, COR_DESTAQUE]], showscale=False,
        marker_line_color="#ffffff", marker_line_width=1,
    ))
    fig.add_trace(go.Scattergeo(
        lat=[mlat], lon=[mlon], mode="markers", hoverinfo="text",
        text=[f"Capital: {capital}" if capital else nome],
        marker=dict(size=10, color="#ef4444", line=dict(color="#ffffff", width=2)),
    ))
    geo = dict(
        showland=True, landcolor="#f3f4f6", showocean=True, oceancolor="#dbeafe",
        showcountries=True, countrycolor="#9ca3af", showcoastlines=True,
        coastlinecolor="#9ca3af", showframe=False, bgcolor="rgba(0,0,0,0)",
    )
    if globo:
        geo.update(projection_type="orthographic", projection_rotation=dict(lon=lon, lat=lat, roll=0))
    else:
        geo.update(projection_type="natural earth", center=dict(lat=lat, lon=lon),
                   projection_scale=escala_do_mapa(comp["area"]))
    fig.update_layout(geo=geo, height=520, margin=dict(l=0, r=0, t=0, b=0),
                      paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
    return fig


def exibir_mapa(nome: str, capital, comp) -> None:
    if not comp or not comp["coord"]:
        st.info("Não foi possível carregar a localização deste país no momento (serviço complementar indisponível).")
        return

    if go is not None and comp["cca3"]:
        modo = st.radio("Visualização", ["Globo 3D", "Mapa plano"], horizontal=True, label_visibility="collapsed")
        st.plotly_chart(montar_figura(nome, capital, comp, modo == "Globo 3D"), config={"displayModeBar": False})
    else:
        import pandas as pd
        st.map(pd.DataFrame({"lat": [comp["coord"][0]], "lon": [comp["coord"][1]]}))
        st.caption("Instale o plotly (pip install plotly) para ver o país destacado no globo.")

    col1, col2, _ = st.columns([1, 1, 2])
    if comp["google_maps"]:
        col1.link_button("📍 Google Maps", comp["google_maps"], use_container_width=True)
    if comp["osm"]:
        col2.link_button("🗺️ OpenStreetMap", comp["osm"], use_container_width=True)


def exibir_simbolos(comp) -> None:
    st.markdown("##### 🏳️ Símbolos nacionais")
    imagens = "".join(
        f'<div class="simbolo"><img src="{html.escape(comp[chave])}" alt="{legenda}">'
        f"<div>{legenda}</div></div>"
        for chave, legenda in (("bandeira", "Bandeira"), ("brasao", "Brasão de armas"))
        if comp and comp.get(chave)
    )
    if imagens:
        st.markdown(f'<div class="simbolos">{imagens}</div>', unsafe_allow_html=True)


def exibir_historia(historico) -> None:
    texto = html.escape(str(historico)).strip().replace("\n", "<br>") if historico else "Histórico não disponível."
    st.markdown(
        f'<div class="hist-card"><div class="info-icon">{icone("livro")}</div>'
        f'<div><div class="hist-title">História do país</div><p class="hist-text">{texto}</p></div></div>',
        unsafe_allow_html=True,
    )


def exibir_terminal(saida: str) -> None:
    estilo = (
        "background:#0c0c0c;color:#cccccc;padding:16px;border-radius:8px;"
        "font-family:Consolas,'Courier New',monospace;font-size:13px;"
        "white-space:pre-wrap;max-height:50vh;overflow:auto;margin:0;"
    )
    st.caption("Saída original do código, exatamente como no terminal.")
    st.markdown(f'<pre style="{estilo}">{ansi_para_html(saida)}</pre>', unsafe_allow_html=True)


# ----------------------------------------------------------------------
# Páginas
# ----------------------------------------------------------------------
def exibir_resultado(sigla: str, nome: str, resultado: dict) -> None:
    dados = resultado["dados"]
    comp = obter_complemento(sigla)

    exibir_aviso(True, "Requisição realizada com sucesso!", "Dados do país carregados.")

    with st.container(key="cartao_resultado"):
        col_pais, col_mapa = st.columns([3, 1.4])
        with col_pais:
            exibir_cabecalho_pais(sigla, nome, comp)
        if go is not None and comp and comp["coord"] and comp["cca3"]:
            with col_mapa:
                st.plotly_chart(montar_miniatura(comp), config={"displayModeBar": False, "staticPlot": True})
        exibir_cartoes(cartoes_principais(dados, comp))
        exibir_historia(dados["historico"])

    st.markdown('<div class="secao-titulo">Explore mais</div>', unsafe_allow_html=True)
    aba_mapa, aba_info, aba_terminal = st.tabs(["🗺️ Mapa interativo", "📊 Mais informações", "🖥️ Terminal"])
    with aba_mapa:
        exibir_mapa(nome, dados.get("capital"), comp)
    with aba_info:
        exibir_simbolos(comp)
        if comp:
            exibir_cartoes(cartoes_extras(comp))
        else:
            st.info("Informações adicionais indisponíveis no momento (serviço complementar fora do ar).")
    with aba_terminal:
        exibir_terminal(resultado["saida"])


def pagina_consulta() -> None:
    paises = carregar_paises()
    sigla = formulario_consulta(paises)

    if sigla is None:
        exibir_estado_inicial(len(paises))
        return

    with st.spinner("Consultando a API do IBGE..."):
        resultado = consultar(sigla)

    if resultado["status"] == 200 and not resultado["erro"]:
        exibir_resultado(sigla, paises[sigla], resultado)
    else:
        detalhe = resultado["erro"] or "A API retornou uma resposta inesperada."
        exibir_aviso(False, "Erro na requisição.", detalhe)
        with st.expander("Ver saída do terminal"):
            exibir_terminal(resultado["saida"])


def pagina_sobre() -> None:
    st.markdown(
        '<div class="sobre"><h3>Sobre o projeto</h3>'
        "Aplicação que consulta a API de Países do IBGE e apresenta as informações de forma visual: "
        "bandeira, localização no mapa, dados geográficos, língua, moeda e história do país."
        "</div>"
        '<div class="sobre"><h3>Como usar</h3><ul>'
        "<li>Na página <b>Consulta</b>, digite o nome ou a sigla do país (ex.: BR, US, PT).</li>"
        "<li>Clique em <b>Consultar país</b>.</li>"
        "<li>Explore o mapa, as informações adicionais e a saída original do código nas abas.</li>"
        "</ul></div>"
        '<div class="sobre"><h3>Fontes de dados</h3><ul>'
        "<li><b>API de Países do IBGE:</b> área, língua, continente, sub-região, capital, moeda e história.</li>"
        "<li><b>REST Countries:</b> localização no mapa, população, fusos horários, fronteiras e brasão.</li>"
        "</ul></div>",
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="API – Dados de Países", page_icon="🌍", layout="wide",
                       initial_sidebar_state="expanded")
    aplicar_estilo()
    pagina = menu_lateral()
    exibir_barra_superior()

    if pagina == "Sobre":
        pagina_sobre()
    else:
        pagina_consulta()

    st.markdown('<div class="rodape">Dados: API de Países do IBGE e REST Countries</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()