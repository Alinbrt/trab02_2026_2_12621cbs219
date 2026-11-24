"""Tela do Dashboard - sidebar + área central + Cycat flutuante.

Esqueleto por enquanto: as abas mostram só placeholders.
Depois cada aba vira o conteúdo real (ativos, vulns, análise, relatórios).
"""

import customtkinter as ctk
from PIL import Image
from interface.tema import (
    COR_FUNDO, COR_FUNDO_CLARO, COR_PRIMARIA,
    COR_TEXTO, COR_TEXTO_SUAVE,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_TEXTO, FONTE_BOTAO, FONTE_PEQUENA,
    NOME_APP, PASTA_ASSETS_CYCAT,
)


# Abas do sistema (chave interna, rótulo mostrado)
ABAS = [
    ("ativos",            "📦  Ativos"),
    ("vulnerabilidades",  "🛡️  Vulnerabilidades"),
    ("analise",           "📊  Análise de Risco"),
    ("relatorios",        "📄  Relatórios"),
]


class TelaDashboard(ctk.CTkFrame):
    """Dashboard com sidebar, área central e Cycat flutuante."""

    def __init__(self, master, perfil):
        super().__init__(master, fg_color=COR_FUNDO)
        self.perfil = perfil
        self.aba_ativa = "ativos"
        self._cache_cycat = {}
        self._construir()

    # -------- Helpers --------
    def _carregar_cycat(self, nome, tamanho):
        chave = (nome, tamanho)
        if chave not in self._cache_cycat:
            caminho = PASTA_ASSETS_CYCAT / f"{nome}.png"
            self._cache_cycat[chave] = ctk.CTkImage(
                light_image=Image.open(caminho),
                dark_image=Image.open(caminho),
                size=tamanho,
            )
        return self._cache_cycat[chave]

    # -------- Construção --------
    def _construir(self):
        # Layout: header em cima, sidebar à esquerda, conteúdo à direita
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construir_header()
        self._construir_sidebar()

        self.area_conteudo = ctk.CTkFrame(self, fg_color=COR_FUNDO)
        self.area_conteudo.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        self._renderizar_aba()

        self._construir_cycat_flutuante()

    def _construir_header(self):
        header = ctk.CTkFrame(self, fg_color=COR_FUNDO_CLARO, height=60, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        # Logo + nome
        ctk.CTkLabel(
            header, text=f"🐾  {NOME_APP}",
            font=FONTE_SUBTITULO, text_color=COR_PRIMARIA,
        ).grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Heartbeat (centralizado-ish)
        heartbeat = ctk.CTkFrame(header, fg_color=COR_FUNDO, corner_radius=8)
        heartbeat.grid(row=0, column=1, padx=20, pady=12)
        ctk.CTkLabel(
            heartbeat, text="❤️",
            font=("Segoe UI", 16),
            text_color="#ef4444",
        ).pack(side="left", padx=(10, 4), pady=6)
        ctk.CTkLabel(
            heartbeat, text="Sistema online",
            font=FONTE_PEQUENA, text_color=COR_TEXTO,
        ).pack(side="left", padx=(0, 10), pady=6)

        # Perfil + botão dica
        direita = ctk.CTkFrame(header, fg_color="transparent")
        direita.grid(row=0, column=2, padx=20, pady=10, sticky="e")

        ctk.CTkLabel(
            direita, text=f"👤 {self.perfil.capitalize()}",
            font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
        ).pack(side="left", padx=(0, 15))

        ctk.CTkButton(
            direita, text="❓ Dica",
            width=70, height=30,
            font=FONTE_PEQUENA,
            fg_color="transparent",
            border_width=1, border_color=COR_PRIMARIA,
            text_color=COR_PRIMARIA,
            hover_color=COR_FUNDO,
            command=self._mostrar_dica,
        ).pack(side="left", padx=5)

    def _construir_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=COR_FUNDO_CLARO, width=220, corner_radius=0)
        sidebar.grid(row=1, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        # Espaço no topo
        ctk.CTkLabel(sidebar, text="", font=FONTE_PEQUENA).pack(pady=10)

        self.botoes_sidebar = {}
        for chave, rotulo in ABAS:
            btn = ctk.CTkButton(
                sidebar, text=rotulo,
                width=200, height=42,
                font=FONTE_BOTAO,
                anchor="w",
                fg_color="transparent",
                text_color=COR_TEXTO,
                hover_color=COR_FUNDO,
                command=lambda c=chave: self._trocar_aba(c),
            )
            btn.pack(pady=3, padx=10)
            self.botoes_sidebar[chave] = btn

        self._atualizar_destaque_sidebar()

    def _construir_cycat_flutuante(self):
        img = self._carregar_cycat("cycat_neutra", tamanho=(90, 90))
        self.label_cycat = ctk.CTkLabel(self, image=img, text="")
        self.label_cycat.place(relx=0.98, rely=0.97, anchor="se")

    # -------- Interação --------
    def _atualizar_destaque_sidebar(self):
        for chave, btn in self.botoes_sidebar.items():
            if chave == self.aba_ativa:
                btn.configure(fg_color=COR_PRIMARIA, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=COR_TEXTO)

    def _trocar_aba(self, chave):
        self.aba_ativa = chave
        self._atualizar_destaque_sidebar()
        self._renderizar_aba()

    def _renderizar_aba(self):
        for widget in self.area_conteudo.winfo_children():
            widget.destroy()

        rotulo = dict(ABAS)[self.aba_ativa]
        ctk.CTkLabel(
            self.area_conteudo, text=rotulo,
            font=FONTE_TITULO, text_color=COR_PRIMARIA,
        ).pack(anchor="w", pady=(0, 20))

        placeholder = ctk.CTkFrame(self.area_conteudo, fg_color=COR_FUNDO_CLARO)
        placeholder.pack(fill="both", expand=True)
        ctk.CTkLabel(
            placeholder,
            text=f"🚧 Conteúdo de '{self.aba_ativa}' em construção",
            font=FONTE_TEXTO, text_color=COR_TEXTO_SUAVE,
        ).place(relx=0.5, rely=0.5, anchor="center")

    def _mostrar_dica(self):
        print(f"[DICA] solicitada para aba: {self.aba_ativa}")