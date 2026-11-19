"""Integração com a NVD (National Vulnerability Database) do NIST para buscar
vulnerabilidades conhecidas pelo identificador CVE."""

from dataclasses import dataclass

import requests

from enums import Severidade

from deep_translator import MyMemoryTranslator

from concurrent.futures import ThreadPoolExecutor


URL_NVD = "https://services.nvd.nist.gov/rest/json/cves/2.0"
TIMEOUT_SEGUNDOS = 10

# Mapeia a severidade textual do NVD pra enum do nosso sistema
MAPA_SEVERIDADE = {
    "LOW": Severidade.BAIXA,
    "MEDIUM": Severidade.MEDIA,
    "HIGH": Severidade.ALTA,
    "CRITICAL": Severidade.CRITICA,
}

# Tradução das CWE mais comuns pra nomenclatura em português
TRADUCAO_CWE = {
    "CWE-79": "Injeção de Script entre Sites (XSS)",
    "CWE-89": "Injeção de SQL",
    "CWE-78": "Injeção de Comando no SO",
    "CWE-77": "Injeção de Comando",
    "CWE-287": "Autenticação Inadequada",
    "CWE-306": "Autenticação Ausente",
    "CWE-200": "Exposição de Informações Sensíveis",
    "CWE-352": "Falsificação de Requisição (CSRF)",
    "CWE-22": "Travessia de Caminho (Path Traversal)",
    "CWE-434": "Upload de Arquivo sem Restrições",
    "CWE-798": "Credenciais Fixas no Código",
    "CWE-862": "Falta de Autorização",
    "CWE-863": "Autorização Incorreta",
    "CWE-20": "Validação de Entrada Inadequada",
    "CWE-125": "Leitura Fora dos Limites de Memória",
    "CWE-787": "Escrita Fora dos Limites de Memória",
    "CWE-416": "Uso de Memória Após Liberação",
    "CWE-119": "Erro de Limites de Buffer",
    "CWE-269": "Gerenciamento de Privilégios Inadequado",
    "CWE-384": "Fixação de Sessão",
    "CWE-264": "Problemas de Permissões e Controle de Acesso",
    "NVD-CWE-Other": "Não classificada no CWE",
    "NVD-CWE-noinfo": "Sem informação de CWE",
}


class ErroCatalogo(Exception):
    """Erro ao consultar o catálogo de vulnerabilidades."""


@dataclass
class VulnerabilidadeConhecida:
    """Dados de uma vulnerabilidade retornada pelo NVD, já normalizados."""
    cve: str
    descricao: str
    categoria: str
    severidade: Severidade
    cvss: float


def buscar_no_nvd(cve_id: str) -> VulnerabilidadeConhecida:
    """Busca uma vulnerabilidade no NVD pelo identificador CVE."""
    cve_id = cve_id.strip().upper()

    try:
        resposta = requests.get(
            URL_NVD,
            params={"cveId": cve_id},
            timeout=TIMEOUT_SEGUNDOS,
        )
        resposta.raise_for_status()
    except requests.exceptions.RequestException as erro:
        raise ErroCatalogo(f"Não foi possível consultar o NVD: {erro}") from erro

    dados = resposta.json()
    lista = dados.get("vulnerabilities", [])
    if not lista:
        raise ErroCatalogo(f"Vulnerabilidade {cve_id} não encontrada no NVD.")

    cve = lista[0]["cve"]
    cvss, severidade = _extrair_metricas(cve)

    return VulnerabilidadeConhecida(
        cve=cve["id"],
        descricao=_extrair_descricao(cve),
        categoria=_extrair_categoria(cve),
        severidade=severidade,
        cvss=cvss,
    )


def _extrair_descricao(cve: dict) -> str:
    """Pega a descrição em inglês do NVD."""
    for d in cve.get("descriptions", []):
        if d.get("lang") == "en":
            return d["value"]
    return "Sem descrição disponível."


def _extrair_metricas(cve: dict) -> tuple[float, Severidade]:
    """Pega CVSS base e severidade. Tenta v3 primeiro, depois v2."""
    metrics = cve.get("metrics", {})

    for versao in ("cvssMetricV31", "cvssMetricV30"):
        if metrics.get(versao):
            dados = metrics[versao][0]["cvssData"]
            severidade_nvd = dados.get("baseSeverity", "MEDIUM")
            return dados["baseScore"], MAPA_SEVERIDADE.get(severidade_nvd, Severidade.MEDIA)

    if metrics.get("cvssMetricV2"):
        entrada = metrics["cvssMetricV2"][0]
        severidade_nvd = entrada.get("baseSeverity", "MEDIUM")
        return entrada["cvssData"]["baseScore"], MAPA_SEVERIDADE.get(severidade_nvd, Severidade.MEDIA)

    raise ErroCatalogo("Vulnerabilidade sem métricas CVSS no NVD.")


def _extrair_categoria(cve: dict) -> str:
    """Pega a categoria (CWE) e traduz pra português quando possível."""
    weaknesses = cve.get("weaknesses", [])
    if weaknesses:
        for descricao in weaknesses[0].get("description", []):
            if descricao.get("lang") == "en":
                cwe = descricao["value"]
                # Traduz se tiver no mapa; senão, devolve o código original
                return TRADUCAO_CWE.get(cwe, cwe)
    return "Não classificada"

# Tipos comuns pra busca em PT-BR
TIPOS_COMUNS_BUSCA = {
    "1": ("Injeção de SQL", "SQL injection"),
    "2": ("Cross-Site Scripting (XSS)", "cross-site scripting"),
    "3": ("Credenciais fracas", "weak credentials"),
    "4": ("Autenticação ausente", "missing authentication"),
    "5": ("Travessia de caminho (Path Traversal)", "path traversal"),
    "6": ("Injeção de comando", "command injection"),
    "7": ("Falsificação de requisição (CSRF)", "cross-site request forgery"),
    "8": ("Exposição de informações sensíveis", "information exposure"),
}


def buscar_por_palavra_chave(termo: str, limite: int = 5) -> list[VulnerabilidadeConhecida]:
    """Busca vulnerabilidades no NVD por palavra-chave. Retorna até 'limite' resultados válidos."""
    termo = termo.strip()
    if not termo:
        raise ErroCatalogo("Termo de busca não pode ser vazio.")

    try:
        resposta = requests.get(
            URL_NVD,
            params={
                "keywordSearch": termo,
                "keywordExactMatch": "",  # exige a frase exata, não só qualquer palavra
                "resultsPerPage": limite,
            },
            timeout=TIMEOUT_SEGUNDOS,
        )

        resposta.raise_for_status()
    except requests.exceptions.RequestException as erro:
        raise ErroCatalogo(f"Não foi possível consultar o NVD: {erro}") from erro

    dados = resposta.json()
    lista = dados.get("vulnerabilities", [])
    if not lista:
        raise ErroCatalogo(f"Nenhuma vulnerabilidade encontrada para '{termo}'.")

    resultados = []
    for item in lista:
        cve = item["cve"]
        try:
            cvss, severidade = _extrair_metricas(cve)
            resultados.append(VulnerabilidadeConhecida(
                cve=cve["id"],
                descricao=_extrair_descricao(cve),
                categoria=_extrair_categoria(cve),
                severidade=severidade,
                cvss=cvss,
            ))
        except ErroCatalogo:
            continue  # pula entradas sem métricas CVSS

    if not resultados:
        raise ErroCatalogo(f"Nenhuma vulnerabilidade válida encontrada para '{termo}'.")

    # Traduz todas as descrições em paralelo (rápido)
    descricoes_pt = _traduzir_em_paralelo([r.descricao for r in resultados])
    for r, descricao_pt in zip(resultados, descricoes_pt):
        r.descricao = descricao_pt

    return resultados


def _traduzir_para_portugues(texto: str) -> str:
    """Traduz texto do inglês pro português usando MyMemory Translator.
    Divide textos longos em pedaços porque o MyMemory limita 500 caracteres por chamada.
    Se falhar, devolve o original."""
    try:
        tradutor = MyMemoryTranslator(source="english", target="portuguese brazil")
        if len(texto) <= 500:
            return tradutor.translate(texto)
        # Divide em pedaços de ~450 chars, cortando em espaços pra não partir palavras
        pedacos = []
        restante = texto
        while len(restante) > 450:
            corte = restante.rfind(" ", 0, 450)
            if corte == -1:
                corte = 450
            pedacos.append(restante[:corte])
            restante = restante[corte:].lstrip()
        if restante:
            pedacos.append(restante)
        return " ".join(tradutor.translate(p) for p in pedacos)
    except Exception:
        return texto
    
    
def _traduzir_em_paralelo(textos: list[str]) -> list[str]:
    """Traduz vários textos ao mesmo tempo. ~2s pra 5 textos em vez de ~10s."""
    with ThreadPoolExecutor(max_workers=5) as executor:
        return list(executor.map(_traduzir_para_portugues, textos))