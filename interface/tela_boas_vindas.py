"""Tela de boas-vindas - apresenta a Cycat ao usuário logado."""

import customtkinter as ctk
from PIL import Image

from interface.tema import (
    COR_FUNDO, COR_FUNDO_CLARO, COR_PRIMARIA, COR_PRIMARIA_HOVER,
    COR_TEXTO, COR_TEXTO_SUAVE,
    FONTE_TITULO, FONTE_TEXTO, FONTE_BOTAO, FONTE_PEQUENA,
    PASTA_ASSETS_CYCAT,
)


class TelaBoasVindas(ctk.CTkFrame):
    """Apresenta a Cycat e direciona o usuário para o tutorial ou dashboard."""

    def __init__(self, master, perfil, ao_iniciar_tutorial, ao_pular_tutorial):
        super().__init__(master, fg_color=COR_FUNDO)
        self.perfil = perfil
        self.ao_iniciar_tutorial = ao_iniciar_tutorial
        self.ao_pular_tutorial = ao_pular_tutorial
        self._construir()

    def _construir(self):
        # Card central com borda
        card = ctk.CTkFrame(
            self, fg_color=COR_FUNDO_CLARO, corner_radius=16,
            border_width=2, border_color=COR_PRIMARIA, width=560,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)
        card.configure(height=560)

        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(expand=True, padx=30, pady=25)

        caminho = PASTA_ASSETS_CYCAT / "cycat_neutra.png"
        self.cycat_img = ctk.CTkImage(
            light_image=Image.open(caminho),
            dark_image=Image.open(caminho),
            size=(200, 200),
        )
        ctk.CTkLabel(container, image=self.cycat_img, text="").pack(pady=(0, 15))

        if self.perfil == "admin":
            saudacao = "Bem-vindo(a) de volta, Admin!"
        else:
            saudacao = "Bem-vindo(a) ao Inventário Cycat!"

        ctk.CTkLabel(
            container, text=saudacao,
            font=FONTE_TITULO, text_color=COR_PRIMARIA,
        ).pack(pady=(0, 10))

        apresentacao = (
            "Oi! Eu sou a Cycat, sua copiloto cibernética 🐾\n"
            "Vou te guiar pelo inventário de ativos e pela análise de riscos."
        )
        ctk.CTkLabel(
            container, text=apresentacao,
            font=FONTE_TEXTO, text_color=COR_TEXTO,
            justify="center",
        ).pack(pady=(0, 25))

        if self.perfil == "analista":
            ctk.CTkButton(
                container, text="🎓  Começar Tutorial",
                width=320, height=46,
                font=FONTE_BOTAO,
                fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
                text_color="white",
                command=self.ao_iniciar_tutorial,
            ).pack(pady=5)

            ctk.CTkButton(
                container, text="Pular tutorial",
                width=320, height=32,
                font=FONTE_PEQUENA,
                fg_color="transparent",
                text_color=COR_TEXTO_SUAVE,
                hover_color="#e9e2f5",
                command=self.ao_pular_tutorial,
            ).pack(pady=5)
        else:
            ctk.CTkButton(
                container, text="→  Entrar no Sistema",
                width=320, height=46,
                font=FONTE_BOTAO,
                fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
                text_color="white",
                command=self.ao_pular_tutorial,
            ).pack(pady=5)

            ctk.CTkButton(
                container, text="🎓  Ver tutorial mesmo assim",
                width=320, height=32,
                font=FONTE_PEQUENA,
                fg_color="transparent",
                text_color=COR_TEXTO_SUAVE,
                hover_color="#e9e2f5",
                command=self.ao_iniciar_tutorial,
            ).pack(pady=5)