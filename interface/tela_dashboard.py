"""Tela do Dashboard - sidebar + area central + Cycat flutuante + sair."""

import customtkinter as ctk
from PIL import Image

from interface.tema import (
    COR_FUNDO, COR_FUNDO_CLARO, COR_PRIMARIA,
    COR_TEXTO, COR_TEXTO_SUAVE, COR_CRITICA,
    FONTE_SUBTITULO, FONTE_PEQUENA,
    NOME_APP, PASTA_ASSETS_CYCAT,
)
from interface.aba_ativos import AbaAtivos
from interface.aba_vulnerabilidades import AbaVulnerabilidades
from interface.aba_analise import AbaAnalise
from interface.aba_relatorios import AbaRelatorios


ABAS = [
    ("ativos",            "📦  Ativos"),
    ("vulnerabilidades",  "🛡️  Vulnerabilidades"),
    ("analise",           "📊  Analise de Risco"),
    ("relatorios",        "📄  Relatorios"),
]


class TelaDashboard(ctk.CTkFrame):
    """Dashboard: sidebar + area central + Cycat flutuante."""

    def __init__(self, master, perfil, inventario, ao_sair):
        super().__init__(master, fg_color=COR_FUNDO)
        self.perfil = perfil
        self.inventario = inventario
        self.ao_sair = ao_sair
        self.aba_ativa = "ativos"
        self._cache_cycat = {}
        self._construir()

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

    def mudar_cycat_flutuante(self, nome_cycat):
        img = self._carregar_cycat(nome_cycat, tamanho=(90, 90))
        self.label_cycat.configure(image=img)

    def _construir(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construir_header()
        self._construir_sidebar()

        self.area_conteudo = ctk.CTkFrame(self, fg_color=COR_FUNDO)
        self.area_conteudo.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)

        self._construir_cycat_flutuante()
        self._renderizar_aba()

    def _construir_header(self):
        header = ctk.CTkFrame(self, fg_color=COR_FUNDO_CLARO, height=60, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text=f"🐾  {NOME_APP}",
            font=FONTE_SUBTITULO, text_color=COR_PRIMARIA,
        ).grid(row=0, column=0, padx=20, pady=15, sticky="w")

        heartbeat = ctk.CTkFrame(header, fg_color=COR_FUNDO, corner_radius=8)
        heartbeat.grid(row=0, column=1, padx=20, pady=12)
        ctk.CTkLabel(heartbeat, text="❤️",
                     font=("Segoe UI", 16), text_color="#ef4444",
                     ).pack(side="left", padx=(10, 4), pady=6)
        ctk.CTkLabel(heartbeat, text="Sistema online",
                     font=FONTE_PEQUENA, text_color=COR_TEXTO,
                     ).pack(side="left", padx=(0, 10), pady=6)

        direita = ctk.CTkFrame(header, fg_color="transparent")
        direita.grid(row=0, column=2, padx=20, pady=10, sticky="e")

        ctk.CTkLabel(
            direita, text=f"👤 {self.perfil.capitalize()}",
            font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
        ).pack(side="left", padx=(0, 15))

        ctk.CTkButton(
            direita, text="❓ Dica",
            width=70, height=30, font=FONTE_PEQUENA,
            fg_color="transparent",
            border_width=1, border_color=COR_PRIMARIA,
            text_color=COR_PRIMARIA,
            hover_color=COR_FUNDO,
            command=self._mostrar_dica,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            direita, text="↪ Sair",
            width=70, height=30, font=FONTE_PEQUENA,
            fg_color="transparent",
            border_width=1, border_color=COR_CRITICA,
            text_color=COR_CRITICA,
            hover_color=COR_FUNDO,
            command=self.ao_sair,
        ).pack(side="left", padx=5)

    def _construir_sidebar(self):
        from interface.tema import FONTE_BOTAO
        sidebar = ctk.CTkFrame(self, fg_color=COR_FUNDO_CLARO, width=220, corner_radius=0)
        sidebar.grid(row=1, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="", font=FONTE_PEQUENA).pack(pady=10)

        self.botoes_sidebar = {}
        for chave, rotulo in ABAS:
            btn = ctk.CTkButton(
                sidebar, text=rotulo,
                width=200, height=42, font=FONTE_BOTAO,
                anchor="w",
                fg_color="transparent",
                text_color=COR_TEXTO,
                hover_color=COR_FUNDO,
                command=lambda c=chave: self._trocar_aba(c),
            )
            btn.pack(pady=3, padx=10)
            self.botoes_sidebar[chave] = btn

        self._atualizar_destaque()

    def _construir_cycat_flutuante(self):
        img = self._carregar_cycat("cycat_neutra", tamanho=(90, 90))
        self.label_cycat = ctk.CTkLabel(self, image=img, text="")
        self.label_cycat.place(relx=0.98, rely=0.97, anchor="se")

    def _atualizar_destaque(self):
        for chave, btn in self.botoes_sidebar.items():
            if chave == self.aba_ativa:
                btn.configure(fg_color=COR_PRIMARIA, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=COR_TEXTO)

    def _trocar_aba(self, chave):
        self.aba_ativa = chave
        self._atualizar_destaque()
        self._renderizar_aba()

    def _renderizar_aba(self):
        for widget in self.area_conteudo.winfo_children():
            widget.destroy()

        comum = dict(
            master=self.area_conteudo,
            inventario=self.inventario,
            perfil=self.perfil,
            ao_mudar_cycat=self.mudar_cycat_flutuante,
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

    def _mostrar_dica(self):
        from tkinter import messagebox
        dicas = {
            "ativos": "Esta aba lista todos os ativos de TI cadastrados. Admin pode cadastrar, editar e remover; Analista apenas visualiza.",
            "vulnerabilidades": "Lista todas as vulnerabilidades do inventario. Voce pode cadastrar manualmente OU buscar direto no NVD (banco oficial, em ingles traduzido pra PT). Admin pode remover; Analista pode criar e atualizar status.",
            "analise": "Calcula o risco de cada ativo usando algebra linear (M*v*W e depois (I-A)x=b). Admin gerencia dependencias; Analista roda analise. Quanto maior o numero, maior o risco.",
            "relatorios": "Gera um relatorio em texto com todo o estado do inventario + analise de risco. Pode salvar como TXT pra entregar.",
        }
        texto = dicas.get(self.aba_ativa, "Sem dica disponivel pra essa aba.")
        messagebox.showinfo(f"Dica - {self.aba_ativa.capitalize()}", texto)