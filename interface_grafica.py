"""
Inventário Cycat - Interface Gráfica
Entry point. Rode com: python interface_grafica.py
"""

import customtkinter as ctk

from inventario import Inventario

from interface.tela_login import TelaLogin
from interface.tela_boas_vindas import TelaBoasVindas
from interface.tela_dashboard import TelaDashboard
from interface.tema import NOME_APP, COR_FUNDO


class InventarioCycatApp(ctk.CTk):
    """Janela principal. Orquestra a troca entre telas."""

    def __init__(self):
        super().__init__()
        self.title(NOME_APP)
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(fg_color=COR_FUNDO)

        ctk.set_appearance_mode("light")
        self.after(100, lambda: self.state("zoomed"))

        # Backend compartilhado pelas telas
        self.inventario = Inventario()

        self.perfil_logado = None
        self.tela_atual = None

        self._mostrar_login()

    def _trocar_tela(self, nova_tela):
        if self.tela_atual is not None:
            self.tela_atual.destroy()
        self.tela_atual = nova_tela
        self.tela_atual.pack(fill="both", expand=True)

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
            ao_iniciar_tutorial=lambda: self._ir_para_dashboard(com_tutorial=True),
            ao_pular_tutorial=lambda: self._ir_para_dashboard(com_tutorial=False),
        ))

    def _ir_para_dashboard(self, com_tutorial=False):
        print(f"[FLUXO] dashboard para {self.perfil_logado} (tutorial={com_tutorial})")
        self._trocar_tela(TelaDashboard(
            self,
            perfil=self.perfil_logado,
            inventario=self.inventario,
            ao_sair=self._fazer_logout,
            iniciar_tutorial=com_tutorial,
        ))

    def _fazer_logout(self):
        print("[FLUXO] logout -> volta para login")
        self.perfil_logado = None
        self._mostrar_login()


if __name__ == "__main__":
    app = InventarioCycatApp()
    app.mainloop()