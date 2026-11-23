"""
Inventário Cycat - Interface Gráfica
Entry point. Rode com: python interface_grafica.py
"""

import customtkinter as ctk

from interface.tela_login import TelaLogin
from interface.tela_boas_vindas import TelaBoasVindas
from interface.tema import NOME_APP, COR_FUNDO


class InventarioCycatApp(ctk.CTk):
    """Janela principal. Orquestra a troca entre telas."""

    def __init__(self):
        super().__init__()
        self.title(NOME_APP)
        self.geometry("900x650")
        self.minsize(700, 500)
        self.configure(fg_color=COR_FUNDO)

        ctk.set_appearance_mode("dark")

        self.perfil_logado = None
        self.tela_atual = None

        self._mostrar_login()

    # -------- Troca de telas --------
    def _trocar_tela(self, nova_tela):
        if self.tela_atual is not None:
            self.tela_atual.destroy()
        self.tela_atual = nova_tela
        self.tela_atual.pack(fill="both", expand=True)

    # -------- Fluxo --------
    def _mostrar_login(self):
        self._trocar_tela(TelaLogin(self, ao_fazer_login=self._apos_login))

    def _apos_login(self, perfil):
        self.perfil_logado = perfil
        print(f"[LOGIN OK] perfil={perfil}")
        self._mostrar_boas_vindas()

    def _mostrar_boas_vindas(self):
        self._trocar_tela(TelaBoasVindas(
            self,
            perfil=self.perfil_logado,
            ao_iniciar_tutorial=self._iniciar_tutorial,
            ao_pular_tutorial=self._ir_para_dashboard,
        ))

    def _iniciar_tutorial(self):
        print("[FLUXO] tutorial solicitado")
        self._placeholder("🎓 TODO: Tela de Tutorial (próximo passo)")

    def _ir_para_dashboard(self):
        print(f"[FLUXO] dashboard para {self.perfil_logado}")
        self._placeholder(
            f"🏠 TODO: Dashboard ({self.perfil_logado.capitalize()})"
        )

    # -------- Placeholder temporário --------
    def _placeholder(self, texto):
        frame = ctk.CTkFrame(self, fg_color=COR_FUNDO)
        ctk.CTkLabel(
            frame, text=texto, font=("Segoe UI", 24, "bold"),
        ).place(relx=0.5, rely=0.5, anchor="center")
        self._trocar_tela(frame)


if __name__ == "__main__":
    app = InventarioCycatApp()
    app.mainloop()