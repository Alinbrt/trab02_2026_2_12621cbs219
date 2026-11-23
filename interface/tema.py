"""Tema visual do Inventário Cycat - cores, fontes, caminhos."""

from pathlib import Path

# ============ CORES ============
# Fundo (dark base)
COR_FUNDO = "#1a1a2e"
COR_FUNDO_CLARO = "#16213e"

# Primárias (vindo da Cycat)
COR_PRIMARIA = "#8B5CF6"     # roxo
COR_PRIMARIA_HOVER = "#7c3aed"
COR_SECUNDARIA = "#5EEAD4"   # teal

# Texto
COR_TEXTO = "#e2e8f0"
COR_TEXTO_SUAVE = "#94a3b8"

# Criticidade
COR_BAIXA = "#10b981"    # verde
COR_MEDIA = "#f59e0b"    # amarelo
COR_ALTA = "#f97316"     # laranja
COR_CRITICA = "#ec4899"  # magenta

# ============ FONTES ============
# Nota: usando Segoe UI por ora (fallback do Windows parecida com Nunito).
# TODO: empacotar Nunito TTF em assets/fonts/ e carregar antes da apresentação.
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
# Resolve a raiz do projeto a partir deste arquivo (funciona de onde for rodado)
PROJETO_ROOT = Path(__file__).resolve().parent.parent
PASTA_ASSETS_CYCAT = PROJETO_ROOT / "assets" / "cycat"