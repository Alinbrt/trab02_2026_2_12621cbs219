"""Tela de login - entrada do usuário com perfil (Analista ou Admin)."""

import customtkinter as ctk
from PIL import Image
from interface.tema import (
    COR_FUNDO, COR_PRIMARIA, COR_PRIMARIA_HOVER, COR_TEXTO_SUAVE,
    COR_CRITICA, FONTE_TITULO, FONTE_SUBTITULO, FONTE_TEXTO,
    FONTE_BOTAO, FONTE_PEQUENA, NOME_APP, PASTA_ASSETS_CYCAT,
)

# Credenciais fake (apenas pra demonstração do TCC)
CREDENCIAIS = {
    "admin":    ("admin",    "admin"),
    "analista": ("analista", "analista"),
}


class TelaLogin(ctk.CTkFrame):
    """Tela de autenticação. Chama `ao_fazer_login(perfil)` quando sucesso."""

    def __init__(self, master, ao_fazer_login):
        super().__init__(master, fg_color=COR_FUNDO)
        self.ao_fazer_login = ao_fazer_login
        self._construir()

    def _construir(self):
        # Container central (não usa toda tela, fica no meio)
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Título
        titulo = ctk.CTkLabel(
            container,
            text=f"🐾 {NOME_APP}",
            font=FONTE_TITULO,
            text_color=COR_PRIMARIA,
        )
        titulo.pack(pady=(0, 6))

        subtitulo = ctk.CTkLabel(
            container,
            text="Entre com suas credenciais",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO_SUAVE,
        )
        subtitulo.pack(pady=(0, 20))

        # Cycat neutra como "boas-vindas visual"
        caminho_cycat = PASTA_ASSETS_CYCAT / "cycat_neutra.png"
        self.cycat_img = ctk.CTkImage(
            light_image=Image.open(caminho_cycat),
            dark_image=Image.open(caminho_cycat),
            size=(140, 140),
        )
        ctk.CTkLabel(container, image=self.cycat_img, text="").pack(pady=(0, 20))

        # Campos de entrada
        self.entry_usuario = ctk.CTkEntry(
            container, width=280, height=40,
            placeholder_text="Usuário", font=FONTE_TEXTO,
        )
        self.entry_usuario.pack(pady=5)

        self.entry_senha = ctk.CTkEntry(
            container, width=280, height=40,
            placeholder_text="Senha", show="●", font=FONTE_TEXTO,
        )
        self.entry_senha.pack(pady=5)

        # Mensagem de erro (fica vazia até dar ruim)
        self.label_erro = ctk.CTkLabel(
            container, text="", text_color=COR_CRITICA, font=FONTE_PEQUENA,
        )
        self.label_erro.pack(pady=(8, 0))

        # Botão Entrar
        ctk.CTkButton(
            container, text="Entrar",
            width=280, height=42,
            font=FONTE_BOTAO,
            fg_color=COR_PRIMARIA,
            hover_color=COR_PRIMARIA_HOVER,
            command=self._tentar_login,
        ).pack(pady=(14, 4))

        # Dica de credenciais (porque é TCC e o avaliador precisa testar)
        ctk.CTkLabel(
            container,
            text="Teste:  admin / admin   •   analista / analista",
            font=FONTE_PEQUENA,
            text_color=COR_TEXTO_SUAVE,
        ).pack(pady=(10, 0))

        # Enter nos campos também submete
        self.entry_usuario.bind("<Return>", lambda e: self.entry_senha.focus())
        self.entry_senha.bind("<Return>", lambda e: self._tentar_login())

        # Começa com foco no campo usuário
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