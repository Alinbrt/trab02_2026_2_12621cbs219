"""Tema visual do Inventário Cycat - paleta pastel, fontes, caminhos."""

from pathlib import Path

# ============ CORES ============
# Fundos
COR_FUNDO = "#f3eefb"            # lavanda suave (fundo externo / papel de parede)
COR_FUNDO_CLARO = "#ffffff"       # branco (cards internos)
COR_FUNDO_MEDIO = "#e9e2f5"       # lavanda média (frames, hover, sidebar)
COR_FUNDO_ESCURO = "#d6c9ec"      # lavanda forte (bordas de destaque)

# Primárias
COR_PRIMARIA = "#a78bfa"          # roxo lavanda
COR_PRIMARIA_HOVER = "#8b5cf6"    # roxo mais forte (hover + estados ativos)
COR_SECUNDARIA = "#5eead4"        # teal da Cycat

# Acentos
COR_ROSA = "#f9a8d4"
COR_PESSEGO = "#fecaca"

# Texto
COR_TEXTO = "#2e1065"             # roxo escuro (contraste)
COR_TEXTO_SUAVE = "#64748b"       # cinza médio

# Criticidade — tons mais profissionais, menos cansativos
COR_BAIXA = "#059669"             # verde esmeralda
COR_MEDIA = "#d97706"             # âmbar mostarda
COR_ALTA = "#ea580c"              # laranja escuro
COR_CRITICA = "#991b1b"           # vermelho vinho

# Para barras/fundos coloridos levemente da criticidade (versão translúcida)
COR_BAIXA_SUAVE = "#d1fae5"
COR_MEDIA_SUAVE = "#fef3c7"
COR_ALTA_SUAVE = "#fed7aa"
COR_CRITICA_SUAVE = "#fecaca"

# ============ FONTES ============
FONTE_NOME = "Segoe UI"
FONTE_TITULO = (FONTE_NOME, 28, "bold")
FONTE_SUBTITULO = (FONTE_NOME, 18)
FONTE_TEXTO = (FONTE_NOME, 14)
FONTE_BOTAO = (FONTE_NOME, 14, "bold")
FONTE_PEQUENA = (FONTE_NOME, 11)
FONTE_CARD_VALOR = (FONTE_NOME, 32, "bold")
FONTE_CARD_TITULO = (FONTE_NOME, 11, "bold")

# ============ IDENTIDADE ============
NOME_APP = "Inventário Cycat"
VERSAO_APP = "1.0"

# ============ CAMINHOS ============
PROJETO_ROOT = Path(__file__).resolve().parent.parent
PASTA_ASSETS_CYCAT = PROJETO_ROOT / "assets" / "cycat"