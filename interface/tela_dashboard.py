"""Dashboard: barra de criticidade global + header + sidebar + conteúdo + painel Cycat."""

import customtkinter as ctk
from tkinter import messagebox

from enums import Severidade, StatusTratamento

from interface.tema import (
    COR_FUNDO, COR_FUNDO_CLARO, COR_FUNDO_MEDIO, COR_FUNDO_ESCURO,
    COR_PRIMARIA, COR_PRIMARIA_HOVER,
    COR_TEXTO, COR_TEXTO_SUAVE, COR_CRITICA,
    COR_BAIXA, COR_MEDIA, COR_ALTA,
    FONTE_SUBTITULO, FONTE_TEXTO, FONTE_BOTAO, FONTE_PEQUENA,
    NOME_APP,
)
from interface.widget_cycat_painel import CycatPainel
from interface.aba_ativos import AbaAtivos
from interface.aba_vulnerabilidades import AbaVulnerabilidades
from interface.aba_analise import AbaAnalise
from interface.aba_relatorios import AbaRelatorios


ABAS = [
    ("ativos",            "📦  Ativos"),
    ("vulnerabilidades",  "🛡️  Vulnerabilidades"),
    ("analise",           "📊  Análise de Risco"),
    ("relatorios",        "📄  Relatórios"),
]

# Dicas contextuais por aba (abertas pelo botão ❓ Dica)
DICAS = {
    "ativos": (
        "Aba Ativos",
        "Aqui você gerencia os equipamentos monitorados (servidores, bancos, "
        "roteadores, etc.). Como Admin, você pode cadastrar, editar e excluir. "
        "Como Analista, apenas visualiza."
    ),
    "vulnerabilidades": (
        "Aba Vulnerabilidades",
        "Lista todas as vulnerabilidades dos ativos. Você pode cadastrar manualmente "
        "OU buscar direto no NVD (banco oficial) — por CVE específico ou por tipo. "
        "A remoção é restrita ao Admin."
    ),
    "analise": (
        "Aba Análise de Risco",
        "Calcula o risco de cada ativo usando álgebra linear: b = W·M·v (risco próprio) "
        "e (I−A)·x = b (risco efetivo, já considerando dependências). "
        "Clique em 'Rodar Análise' e veja a tabela colorida com as barras."
    ),
    "relatorios": (
        "Aba Relatórios",
        "Gera um relatório em texto com todo o estado do inventário mais a análise "
        "de risco. Pode salvar como TXT para entregar à auditoria."
    ),
}


# Passos do tutorial guiado (quando o usuário clica 'Começar Tutorial')
PASSOS_TUTORIAL = [
    {
        "aba": None,
        "expressao": "cycat_tutorial",
        "titulo": "Bem-vindo(a)!",
        "mensagem": (
            "Vou te apresentar o sistema em um passeio rápido. "
            "Clique em 'Próximo' para começar."
        ),
    },
    {
        "aba": "ativos",
        "expressao": "cycat_tutorial",
        "titulo": "Aba Ativos",
        "mensagem": (
            "Aqui ficam os equipamentos monitorados. Servidores, bancos, "
            "roteadores, notebooks. Admin cadastra, edita e exclui; Analista só vê."
        ),
    },
    {
        "aba": "vulnerabilidades",
        "expressao": "cycat_vuln_critica",
        "titulo": "Aba Vulnerabilidades",
        "mensagem": (
            "Toda vulnerabilidade de cada ativo aparece aqui. Pode cadastrar "
            "manualmente ou buscar automaticamente no NVD (banco oficial), "
            "por CVE específico ou por tipo (ex: Injeção de SQL)."
        ),
    },
    {
        "aba": "analise",
        "expressao": "cycat_processando",
        "titulo": "Análise de Risco",
        "mensagem": (
            "O coração do sistema. Calcula o risco próprio e efetivo de cada ativo "
            "usando álgebra linear, considerando as dependências entre eles. "
            "Clique em 'Rodar Análise' para ver os resultados coloridos."
        ),
    },
    {
        "aba": "relatorios",
        "expressao": "cycat_cadastro_concluido",
        "titulo": "Relatórios",
        "mensagem": (
            "Gera um resumo completo do estado do sistema em TXT. "
            "Útil para auditorias ou para arquivar o estado atual."
        ),
    },
    {
        "aba": "ativos",
        "expressao": "cycat_orgulhosa",
        "titulo": "Pronto!",
        "mensagem": (
            "Esse é o básico. Se precisar de ajuda em alguma aba, "
            "clique no botão '❓ Dica' lá em cima. Bora começar!"
        ),
    },
]


class TelaDashboard(ctk.CTkFrame):
    """Dashboard principal. Topo com barra de criticidade, sidebar, conteúdo e painel Cycat."""

    def __init__(self, master, perfil, inventario, ao_sair, iniciar_tutorial=False):
        super().__init__(master, fg_color=COR_FUNDO)
        self.perfil = perfil
        self.inventario = inventario
        self.ao_sair = ao_sair
        self.aba_ativa = "ativos"
        self._construir()
        if iniciar_tutorial:
            # Dá um instante pro layout estabilizar antes de iniciar o tour
            self.after(200, self._iniciar_tutorial)

    # ============ Construção do layout ============
    def _construir(self):
        # Grid: 3 linhas (barra crit, header, conteúdo)
        # Linha 2 tem 3 colunas: sidebar | conteúdo | painel Cycat
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._construir_barra_criticidade()
        self._construir_header()
        self._construir_sidebar()

        self.area_conteudo = ctk.CTkFrame(self, fg_color=COR_FUNDO)
        self.area_conteudo.grid(row=2, column=1, sticky="nsew", padx=15, pady=15)

        self.painel_cycat = CycatPainel(self)
        self.painel_cycat.grid(row=2, column=2, sticky="ns")

        self._renderizar_aba()
        self._atualizar_barra_criticidade()

    def _construir_barra_criticidade(self):
        self.barra_criticidade = ctk.CTkFrame(
            self, height=6, fg_color=COR_BAIXA, corner_radius=0,
        )
        self.barra_criticidade.grid(row=0, column=0, columnspan=3, sticky="ew")

    def _construir_header(self):
        header = ctk.CTkFrame(
            self, fg_color=COR_FUNDO_CLARO, height=60, corner_radius=0,
        )
        header.grid(row=1, column=0, columnspan=3, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text=f"🐾  {NOME_APP}",
            font=FONTE_SUBTITULO, text_color=COR_PRIMARIA,
        ).grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Heartbeat central
        heartbeat = ctk.CTkFrame(
            header, fg_color=COR_FUNDO, corner_radius=8,
            border_width=1, border_color=COR_FUNDO_ESCURO,
        )
        heartbeat.grid(row=0, column=1, padx=20, pady=12)
        ctk.CTkLabel(
            heartbeat, text="❤️", font=("Segoe UI", 16), text_color="#ef4444",
        ).pack(side="left", padx=(10, 4), pady=6)
        ctk.CTkLabel(
            heartbeat, text="Sistema online",
            font=FONTE_PEQUENA, text_color=COR_TEXTO,
        ).pack(side="left", padx=(0, 10), pady=6)

        # Perfil + Dica + Sair
        direita = ctk.CTkFrame(header, fg_color="transparent")
        direita.grid(row=0, column=2, padx=20, pady=10, sticky="e")

        ctk.CTkLabel(
            direita, text=f"👤 {self.perfil.capitalize()}",
            font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
        ).pack(side="left", padx=(0, 15))

        ctk.CTkButton(
            direita, text="❓ Dica",
            width=80, height=30, font=FONTE_PEQUENA,
            fg_color="transparent",
            border_width=1, border_color=COR_PRIMARIA,
            text_color=COR_PRIMARIA, hover_color=COR_FUNDO,
            command=self._mostrar_dica,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            direita, text="↪ Sair",
            width=80, height=30, font=FONTE_PEQUENA,
            fg_color="transparent",
            border_width=1, border_color=COR_CRITICA,
            text_color=COR_CRITICA, hover_color=COR_FUNDO,
            command=self.ao_sair,
        ).pack(side="left", padx=5)

    def _construir_sidebar(self):
        sidebar = ctk.CTkFrame(
            self, fg_color=COR_FUNDO_CLARO, width=220, corner_radius=0,
        )
        sidebar.grid(row=2, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="", font=FONTE_PEQUENA).pack(pady=10)

        self.botoes_sidebar = {}
        for chave, rotulo in ABAS:
            btn = ctk.CTkButton(
                sidebar, text=rotulo,
                width=200, height=44, font=FONTE_BOTAO,
                anchor="w",
                fg_color="transparent",
                text_color=COR_TEXTO,
                hover_color=COR_FUNDO,
                command=lambda c=chave: self.trocar_aba(c),
            )
            btn.pack(pady=4, padx=10)
            self.botoes_sidebar[chave] = btn

        self._atualizar_destaque()

    # ============ Interação ============
    def _atualizar_destaque(self):
        for chave, btn in self.botoes_sidebar.items():
            if chave == self.aba_ativa:
                btn.configure(fg_color=COR_PRIMARIA, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=COR_TEXTO)

    def trocar_aba(self, chave):
        """Público (usado pelo tour também)."""
        self.aba_ativa = chave
        self._atualizar_destaque()
        self._renderizar_aba()
        self._atualizar_barra_criticidade()

    def _renderizar_aba(self):
        for widget in self.area_conteudo.winfo_children():
            widget.destroy()

        comum = dict(
            master=self.area_conteudo,
            inventario=self.inventario,
            perfil=self.perfil,
            cycat=self.painel_cycat,
        )

        if self.aba_ativa == "ativos":
            aba = AbaAtivos(**comum)
        elif self.aba_ativa == "vulnerabilidades":
            aba = AbaVulnerabilidades(**comum)
        elif self.aba_ativa == "analise":
            aba = AbaAnalise(**comum)
        elif self.aba_ativa == "relatorios":
            aba = AbaRelatorios(**comum)
        else:
            aba = ctk.CTkFrame(self.area_conteudo, fg_color=COR_FUNDO)

        aba.pack(fill="both", expand=True)

    # ============ Barra de criticidade global ============
    def _atualizar_barra_criticidade(self):
        """Atualiza a cor da barra fina do topo conforme a vuln mais crítica ABERTA."""
        maior = None
        for ativo in self.inventario.ativos:
            for v in ativo.vulnerabilidades:
                if v.status in (StatusTratamento.CORRIGIDA, StatusTratamento.ACEITA):
                    continue
                if maior is None or self._peso_severidade(v.severidade) > self._peso_severidade(maior):
                    maior = v.severidade

        if maior == Severidade.CRITICA:
            self.barra_criticidade.configure(fg_color=COR_CRITICA)
        elif maior == Severidade.ALTA:
            self.barra_criticidade.configure(fg_color=COR_ALTA)
        elif maior == Severidade.MEDIA:
            self.barra_criticidade.configure(fg_color=COR_MEDIA)
        else:
            self.barra_criticidade.configure(fg_color=COR_BAIXA)

    @staticmethod
    def _peso_severidade(sev):
        pesos = {Severidade.BAIXA: 1, Severidade.MEDIA: 2, Severidade.ALTA: 3, Severidade.CRITICA: 4}
        return pesos.get(sev, 0)

    # ============ Dica contextual ============
    def _mostrar_dica(self):
        titulo, mensagem = DICAS.get(
            self.aba_ativa,
            ("Dica", "Sem dica disponível para esta aba."),
        )
        self.painel_cycat.mostrar("cycat_tutorial", titulo, mensagem)

    # ============ Tutorial guiado ============
    def _iniciar_tutorial(self):
        self.painel_cycat.iniciar_tour(
            PASSOS_TUTORIAL,
            callback_trocar_aba=self.trocar_aba,
        )