"""Cards de resumo com ícone, valor grande e título. Reutilizável em todas as abas."""

import customtkinter as ctk

from interface.tema import (
    COR_FUNDO_CLARO, COR_FUNDO_MEDIO, COR_PRIMARIA,
    COR_TEXTO, COR_TEXTO_SUAVE,
    FONTE_CARD_VALOR, FONTE_CARD_TITULO,
)


def criar_cards_resumo(master, cards):
    """Cria uma linha horizontal de cards de resumo.

    cards = [{"icone": str, "titulo": str, "valor": str|int,
              "cor_valor": str (opcional)}, ...]
    """
    container = ctk.CTkFrame(master, fg_color="transparent")

    for coluna, card in enumerate(cards):
        container.grid_columnconfigure(coluna, weight=1, uniform="cards")
        frame = ctk.CTkFrame(
            container, fg_color=COR_FUNDO_CLARO, corner_radius=12,
            border_width=2, border_color=COR_FUNDO_MEDIO, height=100,
        )
        frame.grid(row=0, column=coluna, padx=5, sticky="nsew")
        frame.grid_propagate(False)

        ctk.CTkLabel(
            frame, text=card["icone"], font=("Segoe UI", 22),
        ).pack(pady=(10, 0))

        ctk.CTkLabel(
            frame, text=str(card["valor"]),
            font=FONTE_CARD_VALOR,
            text_color=card.get("cor_valor", COR_PRIMARIA),
        ).pack()

        ctk.CTkLabel(
            frame, text=card["titulo"],
            font=FONTE_CARD_TITULO,
            text_color=COR_TEXTO_SUAVE,
        ).pack(pady=(0, 8))

    return container