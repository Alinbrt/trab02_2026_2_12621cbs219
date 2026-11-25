"""Tela de login - entrada do usuário com perfil (Analista ou Admin)."""

import customtkinter as ctk
from PIL import Image

from interface.tema import (
    COR_FUNDO, COR_FUNDO_CLARO, COR_FUNDO_MEDIO,
    COR_PRIMARIA, COR_PRIMARIA_HOVER, COR_TEXTO, COR_TEXTO_SUAVE, COR_CRITICA,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_TEXTO, FONTE_BOTAO, FONTE_PEQUENA,
    NOME_APP, PASTA_ASSETS_CYCAT,
)

CREDENCIAIS = {
    "admin":    ("admin",    "admin"),
    "analista": ("analista", "analista"),
}


class TelaLogin(ctk.CTkFrame):
    """Tela de autenticação. Chama ao_fazer_login(perfil) quando autenticado."""

    def __init__(self, master, ao_fazer_login):
        super().__init__(master, fg_color=COR_FUNDO)
        self.ao_fazer_login = ao_fazer_login
        self._construir()

    def _construir(self):
        # Card central com borda
        card = ctk.CTkFrame(
            self, fg_color=COR_FUNDO_CLARO, corner_radius=16,
            border_width=2, border_color=COR_PRIMARIA, width=420,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)
        card.configure(height=620)

        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(expand=True, padx=30, pady=25)

        ctk.CTkLabel(
            container, text=f"🐾  {NOME_APP}",
            font=FONTE_TITULO, text_color=COR_PRIMARIA,
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            container, text="Entre com suas credenciais para continuar",
            font=FONTE_SUBTITULO, text_color=COR_TEXTO_SUAVE,
        ).pack(pady=(0, 15))

        caminho = PASTA_ASSETS_CYCAT / "cycat_neutra.png"
        self.cycat_img = ctk.CTkImage(
            light_image=Image.open(caminho),
            dark_image=Image.open(caminho),
            size=(140, 140),
        )
        ctk.CTkLabel(container, image=self.cycat_img, text="").pack(pady=(0, 15))

        self.entry_usuario = ctk.CTkEntry(
            container, width=320, height=40,
            placeholder_text="Usuário", font=FONTE_TEXTO,
        )
        self.entry_usuario.pack(pady=5)

        self.entry_senha = ctk.CTkEntry(
            container, width=320, height=40,
            placeholder_text="Senha", show="●", font=FONTE_TEXTO,
        )
        self.entry_senha.pack(pady=5)

        self.label_erro = ctk.CTkLabel(
            container, text="", text_color=COR_CRITICA, font=FONTE_PEQUENA,
        )
        self.label_erro.pack(pady=(8, 0))

        ctk.CTkButton(
            container, text="Entrar",
            width=320, height=42,
            font=FONTE_BOTAO,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            text_color="white",
            command=self._tentar_login,
        ).pack(pady=(14, 4))

        ctk.CTkLabel(
            container,
            text="Teste:  admin / admin   •   analista / analista",
            font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
        ).pack(pady=(10, 0))

        self.entry_usuario.bind("<Return>", lambda e: self.entry_senha.focus())
        self.entry_senha.bind("<Return>", lambda e: self._tentar_login())
        self.entry_usuario.focus()

    def _tentar_login(self):
        usuario = self.entry_usuario.get().strip().lower()
        senha = self.entry_senha.get()

        if usuario in CREDENCIAIS:
            _, senha_correta = CREDENCIAIS[usuario]
            if senha == senha_correta:
                self.ao_fazer_login(perfil=usuario)
                return

        self.label_erro.configure(text="Usuário ou senha incorretos.")
        self.entry_senha.delete(0, "end")