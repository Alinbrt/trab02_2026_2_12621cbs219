"""Painel lateral direito com a Cycat grande + balão de mensagem contextual.
Também suporta modo tutorial guiado."""

import customtkinter as ctk
from PIL import Image

from interface.tema import (
    COR_FUNDO, COR_FUNDO_CLARO, COR_FUNDO_MEDIO,
    COR_PRIMARIA, COR_PRIMARIA_HOVER, COR_TEXTO, COR_TEXTO_SUAVE,
    FONTE_SUBTITULO, FONTE_TEXTO, FONTE_BOTAO, FONTE_PEQUENA,
    PASTA_ASSETS_CYCAT,
)


class CycatPainel(ctk.CTkFrame):
    """Painel lateral direito. Modo normal reage ao contexto; modo tutorial é guiado."""

    LARGURA = 260

    def __init__(self, master, ao_terminar_tour=None):
        super().__init__(
            master, fg_color=COR_FUNDO_MEDIO, width=self.LARGURA, corner_radius=0,
        )
        self.pack_propagate(False)
        self._cache = {}
        self.modo_tour = False
        self.passos_tour = []
        self.passo_atual = 0
        self.callback_trocar_aba = None
        self.ao_terminar_tour = ao_terminar_tour
        self._construir()
        # Mensagem inicial padrão
        self.mostrar("cycat_neutra", "Olá!",
                     "Sou a Cycat, sua copiloto. Clique em '❓ Dica' lá em cima se precisar de ajuda.")

    def _carregar_cycat(self, nome, tamanho=(170, 170)):
        chave = (nome, tamanho)
        if chave not in self._cache:
            caminho = PASTA_ASSETS_CYCAT / f"{nome}.png"
            self._cache[chave] = ctk.CTkImage(
                light_image=Image.open(caminho),
                dark_image=Image.open(caminho),
                size=tamanho,
            )
        return self._cache[chave]

    def _construir(self):
        # Cycat grande no topo
        self.label_cycat = ctk.CTkLabel(self, text="")
        self.label_cycat.pack(pady=(25, 10))

        # "Balão" de mensagem — card branco com borda lilás
        self.balao = ctk.CTkFrame(
            self, fg_color=COR_FUNDO_CLARO, corner_radius=12,
            border_width=2, border_color=COR_PRIMARIA,
        )
        self.balao.pack(fill="x", padx=15, pady=(0, 15))

        self.label_titulo = ctk.CTkLabel(
            self.balao, text="", font=(FONTE_SUBTITULO[0], 15, "bold"),
            text_color=COR_PRIMARIA, wraplength=210, justify="center",
        )
        self.label_titulo.pack(padx=12, pady=(12, 4))

        self.label_mensagem = ctk.CTkLabel(
            self.balao, text="", font=FONTE_PEQUENA,
            text_color=COR_TEXTO, wraplength=210, justify="left",
        )
        self.label_mensagem.pack(padx=12, pady=(0, 12))

        # Área de botões do tour (escondida em modo normal)
        self.frame_tour = ctk.CTkFrame(self, fg_color="transparent")

        self.label_passo = ctk.CTkLabel(
            self.frame_tour, text="", font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
        )
        self.label_passo.pack(pady=(0, 6))

        self.botao_proximo = ctk.CTkButton(
            self.frame_tour, text="Próximo  →",
            width=220, height=38, font=FONTE_BOTAO,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            text_color="white", command=self._proximo_passo,
        )
        self.botao_proximo.pack(pady=4, padx=15)

        self.botao_pular = ctk.CTkButton(
            self.frame_tour, text="Pular tutorial",
            width=220, height=30, font=FONTE_PEQUENA,
            fg_color="transparent", text_color=COR_TEXTO_SUAVE,
            hover_color=COR_FUNDO,
            command=self._encerrar_tour,
        )
        self.botao_pular.pack(pady=(2, 10), padx=15)

    # ------- Modo normal -------
    def mostrar(self, expressao, titulo="", mensagem=""):
        """Troca expressão da Cycat e atualiza o balão. Ignorado em modo tour."""
        if self.modo_tour:
            return
        img = self._carregar_cycat(expressao)
        self.label_cycat.configure(image=img)
        self.label_titulo.configure(text=titulo)
        self.label_mensagem.configure(text=mensagem)

    # ------- Modo tutorial -------
    def iniciar_tour(self, passos, callback_trocar_aba):
        """passos = lista de dicts {aba, expressao, titulo, mensagem}."""
        self.modo_tour = True
        self.passos_tour = passos
        self.callback_trocar_aba = callback_trocar_aba
        self.passo_atual = 0
        self.frame_tour.pack(fill="x", pady=(5, 0))
        self._mostrar_passo()

    def _mostrar_passo(self):
        passo = self.passos_tour[self.passo_atual]
        if passo.get("aba"):
            self.callback_trocar_aba(passo["aba"])
        # Força update visual mesmo em modo tour
        img = self._carregar_cycat(passo["expressao"])
        self.label_cycat.configure(image=img)
        self.label_titulo.configure(text=passo["titulo"])
        self.label_mensagem.configure(text=passo["mensagem"])
        self.label_passo.configure(
            text=f"Passo {self.passo_atual + 1} de {len(self.passos_tour)}",
        )
        if self.passo_atual == len(self.passos_tour) - 1:
            self.botao_proximo.configure(text="Concluir  ✓")
        else:
            self.botao_proximo.configure(text="Próximo  →")

    def _proximo_passo(self):
        if self.passo_atual < len(self.passos_tour) - 1:
            self.passo_atual += 1
            self._mostrar_passo()
        else:
            self._encerrar_tour()

    def _encerrar_tour(self):
        self.modo_tour = False
        self.frame_tour.pack_forget()
        self.label_cycat.configure(image=self._carregar_cycat("cycat_sucesso"))
        self.label_titulo.configure(text="Pronto!")
        self.label_mensagem.configure(
            text="Tutorial concluído. Agora é com você! Qualquer dúvida, "
                 "clique em '❓ Dica' lá em cima.",
        )
        if self.ao_terminar_tour:
            self.ao_terminar_tour()