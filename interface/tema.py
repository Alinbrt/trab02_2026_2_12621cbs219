"""Tema visual do Inventário Cycat - paleta pastel, fontes, caminhos."""

from pathlib import Path

# ============ CORES ============
# Fundos — claros com tingimento pastel (lavanda)
COR_FUNDO = "#f3eefb"           # lavanda suave (papel de parede)
COR_FUNDO_CLARO = "#ffffff"      # branco puro (cards e header)
COR_FUNDO_MEDIO = "#e9e2f5"      # lavanda mais forte (sidebar, hover)

# Primárias — vindas da Cycat
COR_PRIMARIA = "#a78bfa"         # roxo lavanda (botões principais)
COR_PRIMARIA_HOVER = "#8b5cf6"   # roxo mais forte (hover + estados ativos)
COR_SECUNDARIA = "#5eead4"       # teal da Cycat

# Acentos pastéis
COR_ROSA = "#f9a8d4"             # rosa pink pastel
COR_PESSEGO = "#fecaca"          # pêssego

# Texto — escuro pra contrastar com fundos claros
COR_TEXTO = "#2e1065"            # roxo bem escuro
COR_TEXTO_SUAVE = "#64748b"      # cinza médio pra legendas

# Criticidade — pastel coerente com o resto
COR_BAIXA = "#86efac"    # verde menta
COR_MEDIA = "#fde68a"    # amarelo manteiga
COR_ALTA = "#fdba74"     # pêssego laranjado
COR_CRITICA = "#f9a8d4"  # rosa pink pastel

# ============ FONTES ============
FONTE_NOME = "Segoe UI"
FONTE_TITULO = (FONTE_NOME, 28, "bold")
FONTE_SUBTITULO = (FONTE_NOME, 18)
FONTE_TEXTO = (FONTE_NOME, 14)
FONTE_BOTAO = (FONTE_NOME, 14, "bold")
FONTE_PEQUENA = (FONTE_NOME, 11)

# ============ IDENTIDADE ============
NOME_APP = "Inventário Cycat"
VERSAO_APP = "1.0"

# ============ CAMINHOS ============
PROJETO_ROOT = Path(__file__).resolve().parent.parent
PASTA_ASSETS_CYCAT = PROJETO_ROOT / "assets" / "cycat"