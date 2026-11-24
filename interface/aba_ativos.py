"""Aba Ativos - lista, cadastra, edita e remove ativos. Respeita permissoes."""

import customtkinter as ctk
from tkinter import messagebox

from enums import TipoAtivo
from inventario import Inventario, ErroInventario
from modelos import criar_equipamento

from interface.tema import (
    COR_FUNDO, COR_FUNDO_CLARO, COR_FUNDO_MEDIO,
    COR_PRIMARIA, COR_PRIMARIA_HOVER, COR_CRITICA,
    COR_TEXTO, COR_TEXTO_SUAVE,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_TEXTO,
    FONTE_BOTAO, FONTE_PEQUENA,
)


class AbaAtivos(ctk.CTkFrame):
    """Aba que lista ativos. Admin pode cadastrar/editar/excluir; Analista so le."""

    def __init__(self, master, inventario: Inventario, perfil: str, ao_mudar_cycat=None):
        super().__init__(master, fg_color=COR_FUNDO)
        self.inventario = inventario
        self.perfil = perfil
        self.eh_admin = (perfil == "admin")
        self.ao_mudar_cycat = ao_mudar_cycat or (lambda nome: None)
        self._construir()

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
                width=180, height=36,
                font=FONTE_BOTAO,
                fg_color=COR_PRIMARIA,
                hover_color=COR_PRIMARIA_HOVER,
                text_color="white",
                command=self._abrir_cadastro,
            ).pack(side="right")

        self.label_contador = ctk.CTkLabel(
            self, text="", font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
        )
        self.label_contador.pack(anchor="w", pady=(0, 10))

        self.lista = ctk.CTkScrollableFrame(
            self, fg_color=COR_FUNDO_CLARO, corner_radius=10,
        )
        self.lista.pack(fill="both", expand=True)

        # Rodape de permissao pra Analista
        if not self.eh_admin:
            ctk.CTkLabel(
                self, text="🔒  Como Analista, voce pode visualizar os ativos. Pra cadastrar, editar ou remover, use o perfil Admin.",
                font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
                wraplength=800, justify="left",
            ).pack(anchor="w", pady=(10, 0))

        self._renderizar()

    def _renderizar(self):
        for widget in self.lista.winfo_children():
            widget.destroy()

        ativos = self.inventario.ativos
        self.label_contador.configure(text=f"{len(ativos)} ativo(s) cadastrado(s)")

        if not ativos:
            ctk.CTkLabel(
                self.lista,
                text="Nenhum ativo cadastrado ainda.",
                font=FONTE_TEXTO, text_color=COR_TEXTO_SUAVE,
                justify="center",
            ).pack(pady=50)
            self.ao_mudar_cycat("cycat_vazio")
            return

        self.ao_mudar_cycat("cycat_neutra")

        cab = ctk.CTkFrame(self.lista, fg_color="transparent")
        cab.pack(fill="x", padx=15, pady=(10, 5))
        colunas = [("ID", 50), ("Hostname", 180), ("Tipo", 140), ("Responsavel", 150), ("", 160)]
        for texto, largura in colunas:
            ctk.CTkLabel(
                cab, text=texto,
                font=(FONTE_BOTAO[0], 12, "bold"),
                text_color=COR_TEXTO_SUAVE,
                width=largura, anchor="w",
            ).pack(side="left")

        sep = ctk.CTkFrame(self.lista, height=1, fg_color=COR_FUNDO_MEDIO)
        sep.pack(fill="x", padx=15)

        for ativo in ativos:
            self._linha_ativo(ativo)

    def _linha_ativo(self, ativo):
        linha = ctk.CTkFrame(self.lista, fg_color="transparent")
        linha.pack(fill="x", padx=15, pady=3)

        for texto, largura in [
            (str(ativo.id_ativo), 50),
            (ativo.hostname, 180),
            (ativo.tipo.rotulo, 140),
            (ativo.responsavel, 150),
        ]:
            ctk.CTkLabel(
                linha, text=texto,
                font=FONTE_TEXTO, text_color=COR_TEXTO,
                width=largura, anchor="w",
            ).pack(side="left")

        acoes = ctk.CTkFrame(linha, fg_color="transparent", width=160)
        acoes.pack(side="left")

        if self.eh_admin:
            ctk.CTkButton(
                acoes, text="Editar",
                width=70, height=28,
                font=FONTE_PEQUENA,
                fg_color="transparent",
                border_width=1, border_color=COR_PRIMARIA,
                text_color=COR_PRIMARIA,
                hover_color=COR_FUNDO,
                command=lambda a=ativo: self._abrir_edicao(a),
            ).pack(side="left", padx=(0, 5))

            ctk.CTkButton(
                acoes, text="Excluir",
                width=80, height=28,
                font=FONTE_PEQUENA,
                fg_color="transparent",
                border_width=1, border_color=COR_CRITICA,
                text_color=COR_CRITICA,
                hover_color=COR_FUNDO,
                command=lambda a=ativo: self._remover(a),
            ).pack(side="left")

    def _abrir_cadastro(self):
        FormularioAtivo(
            master=self, inventario=self.inventario,
            ao_salvar=lambda: (self._renderizar(), self.ao_mudar_cycat("cycat_sucesso")),
        )

    def _abrir_edicao(self, ativo):
        FormularioAtivo(
            master=self, inventario=self.inventario,
            ao_salvar=lambda: (self._renderizar(), self.ao_mudar_cycat("cycat_sucesso")),
            ativo_existente=ativo,
        )

    def _remover(self, ativo):
        if not messagebox.askyesno(
            "Confirmar exclusao",
            f"Excluir o ativo '{ativo.hostname}' (ID {ativo.id_ativo})?\n\n"
            "Isso remove tambem as dependencias que envolvem ele.",
        ):
            return
        try:
            self.inventario.remover_ativo(ativo.id_ativo)
            self._renderizar()
            self.ao_mudar_cycat("cycat_sucesso")
        except ErroInventario as erro:
            messagebox.showerror("Erro", str(erro))
            self.ao_mudar_cycat("cycat_erro")


class FormularioAtivo(ctk.CTkToplevel):
    """Pop-up pra cadastrar OU editar ativo. Enter salva, Esc cancela."""

    def __init__(self, master, inventario, ao_salvar, ativo_existente=None):
        super().__init__(master)
        self.inventario = inventario
        self.ao_salvar = ao_salvar
        self.ativo_existente = ativo_existente
        self.modo_edicao = ativo_existente is not None

        titulo = "Editar Ativo" if self.modo_edicao else "Cadastrar Ativo"
        self.title(titulo)
        self.geometry("460x640")
        self.minsize(460, 600)
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
            state="readonly", font=FONTE_TEXTO, width=400,
        )
        tipo_inicial = (self.ativo_existente.tipo.rotulo if self.modo_edicao
                        else list(self.tipos.keys())[0])
        self.combo_tipo.set(tipo_inicial)
        self.combo_tipo.pack(pady=(2, 10), fill="x")

        self.entry_hostname = self._entry(box, "Hostname",
            inicial=self.ativo_existente.hostname if self.modo_edicao else "")
        self.entry_responsavel = self._entry(box, "Responsavel",
            inicial=self.ativo_existente.responsavel if self.modo_edicao else "")
        self.entry_localizacao = self._entry(box, "Localizacao",
            inicial=self.ativo_existente.localizacao if self.modo_edicao else "")
        self.entry_descricao = self._entry(box, "Descricao (opcional)",
            inicial=self.ativo_existente.descricao if self.modo_edicao else "")

        self.label_erro = ctk.CTkLabel(
            box, text="", text_color=COR_CRITICA, font=FONTE_PEQUENA,
            wraplength=400, justify="left",
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
            width=120, height=36, font=FONTE_BOTAO,
            fg_color="transparent",
            border_width=1, border_color=COR_TEXTO_SUAVE,
            text_color=COR_TEXTO,
            hover_color=COR_FUNDO_MEDIO,
            command=self.destroy,
        ).pack(side="right", padx=(5, 0))

        ctk.CTkButton(
            botoes, text="Salvar",
            width=120, height=36, font=FONTE_BOTAO,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            text_color="white",
            command=self._salvar,
        ).pack(side="right")

        self.entry_hostname.focus()

    def _label(self, master, texto):
        ctk.CTkLabel(
            master, text=texto,
            font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
        ).pack(anchor="w")

    def _entry(self, master, label, inicial=""):
        self._label(master, label)
        entry = ctk.CTkEntry(master, font=FONTE_TEXTO, width=400, height=36)
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