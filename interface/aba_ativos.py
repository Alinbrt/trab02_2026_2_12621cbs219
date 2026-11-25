"""Aba Ativos - lista, cadastra, edita e remove ativos. Respeita permissões."""

import customtkinter as ctk
from tkinter import messagebox

from enums import TipoAtivo
from inventario import Inventario, ErroInventario
from modelos import criar_equipamento

from interface.tema import (
    COR_FUNDO, COR_FUNDO_CLARO, COR_FUNDO_MEDIO, COR_FUNDO_ESCURO,
    COR_PRIMARIA, COR_PRIMARIA_HOVER, COR_CRITICA,
    COR_TEXTO, COR_TEXTO_SUAVE,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_TEXTO,
    FONTE_BOTAO, FONTE_PEQUENA,
)
from interface.widget_cards_resumo import criar_cards_resumo


class AbaAtivos(ctk.CTkFrame):
    """Aba que lista ativos. Admin pode cadastrar/editar/excluir; Analista só lê."""

    def __init__(self, master, inventario: Inventario, perfil: str, cycat=None):
        super().__init__(master, fg_color=COR_FUNDO)
        self.inventario = inventario
        self.perfil = perfil
        self.eh_admin = (perfil == "admin")
        self.cycat = cycat
        self._construir()

    def _notificar_cycat(self, expressao, titulo="", mensagem=""):
        if self.cycat:
            self.cycat.mostrar(expressao, titulo, mensagem)

    def _construir(self):
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            topo, text="📦  Ativos",
            font=FONTE_TITULO, text_color=COR_PRIMARIA,
        ).pack(side="left")

        if self.eh_admin:
            ctk.CTkButton(
                topo, text="+  Cadastrar Ativo",
                width=200, height=38,
                font=FONTE_BOTAO,
                fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
                text_color="white",
                command=self._abrir_cadastro,
            ).pack(side="right")

        # Cards de resumo
        self._construir_cards_resumo()

        # Lista (card com borda)
        self.card_lista = ctk.CTkFrame(
            self, fg_color=COR_FUNDO_CLARO, corner_radius=12,
            border_width=2, border_color=COR_FUNDO_MEDIO,
        )
        self.card_lista.pack(fill="both", expand=True)

        self.lista = ctk.CTkScrollableFrame(
            self.card_lista, fg_color="transparent",
        )
        self.lista.pack(fill="both", expand=True, padx=10, pady=10)

        if not self.eh_admin:
            ctk.CTkLabel(
                self,
                text="🔒  Como Analista, você pode visualizar os ativos. "
                     "Para cadastrar, editar ou remover, use o perfil Admin.",
                font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
                wraplength=800, justify="left",
            ).pack(anchor="w", pady=(10, 0))

        self._renderizar()

    def _construir_cards_resumo(self):
        ativos = self.inventario.ativos
        total = len(ativos)
        servidores = sum(1 for a in ativos if a.tipo == TipoAtivo.SERVIDOR)
        bancos = sum(1 for a in ativos if a.tipo == TipoAtivo.BANCO_DE_DADOS)
        outros = total - servidores - bancos
        com_vulns = sum(1 for a in ativos if len(a.vulnerabilidades) > 0)

        cards = criar_cards_resumo(self, [
            {"icone": "📦", "titulo": "TOTAL", "valor": total},
            {"icone": "🖥️", "titulo": "SERVIDORES", "valor": servidores},
            {"icone": "🗄️", "titulo": "BANCOS", "valor": bancos},
            {"icone": "📁", "titulo": "OUTROS", "valor": outros},
            {"icone": "⚠️", "titulo": "COM VULNS", "valor": com_vulns,
             "cor_valor": COR_CRITICA if com_vulns else COR_PRIMARIA},
        ])
        cards.pack(fill="x", pady=(0, 15))

    def _renderizar(self):
        for widget in self.lista.winfo_children():
            widget.destroy()

        ativos = self.inventario.ativos

        if not ativos:
            ctk.CTkLabel(
                self.lista,
                text="Nenhum ativo cadastrado ainda.",
                font=FONTE_TEXTO, text_color=COR_TEXTO_SUAVE,
                justify="center",
            ).pack(pady=50)
            self._notificar_cycat("cycat_vazio", "Inventário vazio",
                                  "Nenhum ativo cadastrado. Que tal começar cadastrando um?")
            return

        self._notificar_cycat("cycat_neutra", "Ativos carregados",
                              f"{len(ativos)} ativo(s) no inventário.")

        cab = ctk.CTkFrame(self.lista, fg_color="transparent")
        cab.pack(fill="x", padx=10, pady=(5, 5))
        colunas = [("ID", 50), ("Hostname", 200), ("Tipo", 160),
                   ("Responsável", 180), ("", 180)]
        for texto, largura in colunas:
            ctk.CTkLabel(
                cab, text=texto,
                font=(FONTE_BOTAO[0], 12, "bold"),
                text_color=COR_TEXTO_SUAVE,
                width=largura, anchor="w",
            ).pack(side="left")

        sep = ctk.CTkFrame(self.lista, height=1, fg_color=COR_FUNDO_ESCURO)
        sep.pack(fill="x", padx=10)

        for ativo in ativos:
            self._linha_ativo(ativo)

    def _linha_ativo(self, ativo):
        linha = ctk.CTkFrame(self.lista, fg_color="transparent")
        linha.pack(fill="x", padx=10, pady=3)

        for texto, largura in [
            (str(ativo.id_ativo), 50),
            (ativo.hostname, 200),
            (ativo.tipo.rotulo, 160),
            (ativo.responsavel, 180),
        ]:
            ctk.CTkLabel(
                linha, text=texto,
                font=FONTE_TEXTO, text_color=COR_TEXTO,
                width=largura, anchor="w",
            ).pack(side="left")

        acoes = ctk.CTkFrame(linha, fg_color="transparent", width=180)
        acoes.pack(side="left")

        if self.eh_admin:
            ctk.CTkButton(
                acoes, text="Editar",
                width=80, height=30, font=FONTE_PEQUENA,
                fg_color="transparent",
                border_width=1, border_color=COR_PRIMARIA,
                text_color=COR_PRIMARIA, hover_color=COR_FUNDO,
                command=lambda a=ativo: self._abrir_edicao(a),
            ).pack(side="left", padx=(0, 5))

            ctk.CTkButton(
                acoes, text="Excluir",
                width=80, height=30, font=FONTE_PEQUENA,
                fg_color="transparent",
                border_width=1, border_color=COR_CRITICA,
                text_color=COR_CRITICA, hover_color=COR_FUNDO,
                command=lambda a=ativo: self._remover(a),
            ).pack(side="left")

    def _abrir_cadastro(self):
        FormularioAtivo(
            master=self, inventario=self.inventario,
            ao_salvar=lambda: (
                self._reconstruir_tudo(),
                self._notificar_cycat("cycat_sucesso", "Ativo salvo!",
                                      "Já conta na análise de risco."),
            ),
        )

    def _abrir_edicao(self, ativo):
        FormularioAtivo(
            master=self, inventario=self.inventario,
            ao_salvar=lambda: (
                self._reconstruir_tudo(),
                self._notificar_cycat("cycat_sucesso", "Ativo atualizado",
                                      f"Alterações em '{ativo.hostname}' salvas."),
            ),
            ativo_existente=ativo,
        )

    def _reconstruir_tudo(self):
        """Reconstrói a aba inteira para os cards de resumo também atualizarem."""
        for w in self.winfo_children():
            w.destroy()
        self._construir()

    def _remover(self, ativo):
        if not messagebox.askyesno(
            "Confirmar exclusão",
            f"Excluir o ativo '{ativo.hostname}' (ID {ativo.id_ativo})?\n\n"
            "Isso remove também as dependências que envolvem ele.",
        ):
            return
        try:
            self.inventario.remover_ativo(ativo.id_ativo)
            self._reconstruir_tudo()
            self._notificar_cycat("cycat_sucesso", "Ativo removido",
                                  "Ativo e suas dependências foram apagados.")
        except ErroInventario as erro:
            messagebox.showerror("Erro", str(erro))
            self._notificar_cycat("cycat_erro", "Erro ao remover", str(erro))


class FormularioAtivo(ctk.CTkToplevel):
    """Pop-up para cadastrar OU editar ativo. Enter salva, Esc cancela."""

    def __init__(self, master, inventario, ao_salvar, ativo_existente=None):
        super().__init__(master)
        self.inventario = inventario
        self.ao_salvar = ao_salvar
        self.ativo_existente = ativo_existente
        self.modo_edicao = ativo_existente is not None

        titulo = "Editar Ativo" if self.modo_edicao else "Cadastrar Ativo"
        self.title(titulo)
        self.geometry("480x660")
        self.minsize(480, 620)
        self.configure(fg_color=COR_FUNDO)
        self.transient(master)
        self.grab_set()

        self.bind("<Return>", lambda e: self._salvar())
        self.bind("<Escape>", lambda e: self.destroy())

        self._construir(titulo)

    def _construir(self, titulo):
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.pack(fill="both", expand=True, padx=25, pady=20)

        ctk.CTkLabel(
            box, text=titulo,
            font=FONTE_SUBTITULO, text_color=COR_PRIMARIA,
        ).pack(anchor="w", pady=(0, 15))

        self._label(box, "Tipo")
        self.tipos = {tipo.rotulo: tipo for tipo in TipoAtivo}
        self.combo_tipo = ctk.CTkComboBox(
            box, values=list(self.tipos.keys()),
            state="readonly", font=FONTE_TEXTO, width=420,
        )
        tipo_inicial = (self.ativo_existente.tipo.rotulo if self.modo_edicao
                        else list(self.tipos.keys())[0])
        self.combo_tipo.set(tipo_inicial)
        self.combo_tipo.pack(pady=(2, 10), fill="x")

        self.entry_hostname = self._entry(box, "Hostname",
            inicial=self.ativo_existente.hostname if self.modo_edicao else "")
        self.entry_responsavel = self._entry(box, "Responsável",
            inicial=self.ativo_existente.responsavel if self.modo_edicao else "")
        self.entry_localizacao = self._entry(box, "Localização",
            inicial=self.ativo_existente.localizacao if self.modo_edicao else "")
        self.entry_descricao = self._entry(box, "Descrição (opcional)",
            inicial=self.ativo_existente.descricao if self.modo_edicao else "")

        self.label_erro = ctk.CTkLabel(
            box, text="", text_color=COR_CRITICA, font=FONTE_PEQUENA,
            wraplength=420, justify="left",
        )
        self.label_erro.pack(anchor="w", pady=(5, 0))

        ctk.CTkLabel(
            box, text="💡  Enter salva  •  Esc cancela",
            font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
        ).pack(anchor="w", pady=(8, 0))

        botoes = ctk.CTkFrame(box, fg_color="transparent")
        botoes.pack(fill="x", pady=(15, 0))

        ctk.CTkButton(
            botoes, text="Cancelar",
            width=120, height=38, font=FONTE_BOTAO,
            fg_color="transparent",
            border_width=1, border_color=COR_TEXTO_SUAVE,
            text_color=COR_TEXTO, hover_color=COR_FUNDO_MEDIO,
            command=self.destroy,
        ).pack(side="right", padx=(5, 0))

        ctk.CTkButton(
            botoes, text="Salvar",
            width=120, height=38, font=FONTE_BOTAO,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            text_color="white", command=self._salvar,
        ).pack(side="right")

        self.entry_hostname.focus()

    def _label(self, master, texto):
        ctk.CTkLabel(master, text=texto,
                     font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE).pack(anchor="w")

    def _entry(self, master, label, inicial=""):
        self._label(master, label)
        entry = ctk.CTkEntry(master, font=FONTE_TEXTO, width=420, height=36)
        if inicial:
            entry.insert(0, inicial)
        entry.pack(pady=(2, 10), fill="x")
        return entry

    def _salvar(self):
        try:
            tipo = self.tipos[self.combo_tipo.get()]
            if self.modo_edicao:
                self.inventario.atualizar_ativo(
                    id_ativo=self.ativo_existente.id_ativo,
                    hostname=self.entry_hostname.get(),
                    responsavel=self.entry_responsavel.get(),
                    localizacao=self.entry_localizacao.get(),
                    descricao=self.entry_descricao.get() or "",
                    tipo=tipo,
                )
            else:
                ativo = criar_equipamento(
                    tipo=tipo,
                    id_ativo=self.inventario.proximo_id(),
                    hostname=self.entry_hostname.get(),
                    responsavel=self.entry_responsavel.get(),
                    localizacao=self.entry_localizacao.get(),
                    descricao=self.entry_descricao.get() or "",
                )
                self.inventario.cadastrar_ativo(ativo)
            self.ao_salvar()
            self.destroy()
        except (ValueError, ErroInventario) as erro:
            self.label_erro.configure(text=str(erro))