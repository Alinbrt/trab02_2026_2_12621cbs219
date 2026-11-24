"""Aba Analise de Risco - roda o modelo linear, mostra barras de comparacao e gerencia dependencias."""

import customtkinter as ctk
from tkinter import messagebox

from analise_risco import ModeloAnaliseRisco
from inventario import Inventario, ErroInventario

from interface.tema import (
    COR_FUNDO, COR_FUNDO_CLARO, COR_FUNDO_MEDIO,
    COR_PRIMARIA, COR_PRIMARIA_HOVER, COR_CRITICA,
    COR_TEXTO, COR_TEXTO_SUAVE,
    COR_BAIXA, COR_MEDIA, COR_ALTA,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_TEXTO,
    FONTE_BOTAO, FONTE_PEQUENA,
)


def cor_do_risco(valor):
    """Cor pastel baseada na intensidade do risco."""
    if valor < 2:
        return COR_BAIXA
    if valor < 5:
        return COR_MEDIA
    if valor < 10:
        return COR_ALTA
    return COR_CRITICA


class AbaAnalise(ctk.CTkFrame):
    """Analise de risco + gestao de dependencias."""

    def __init__(self, master, inventario: Inventario, perfil: str, ao_mudar_cycat=None):
        super().__init__(master, fg_color=COR_FUNDO)
        self.inventario = inventario
        self.perfil = perfil
        self.eh_admin = (perfil == "admin")
        self.ao_mudar_cycat = ao_mudar_cycat or (lambda nome: None)
        self._construir()

    def _construir(self):
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            topo, text="📊  Analise de Risco",
            font=FONTE_TITULO, text_color=COR_PRIMARIA,
        ).pack(side="left")

        ctk.CTkButton(
            topo, text="▶  Rodar Analise",
            width=160, height=36,
            font=FONTE_BOTAO,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            text_color="white",
            command=self._rodar_analise,
        ).pack(side="right")

        self.area_resultado = ctk.CTkScrollableFrame(
            self, fg_color=COR_FUNDO_CLARO, corner_radius=10, height=320,
        )
        self.area_resultado.pack(fill="x", pady=(0, 15))
        self._placeholder_resultado()

        self._construir_dependencias()

    def _placeholder_resultado(self):
        ctk.CTkLabel(
            self.area_resultado,
            text="Clique em '▶ Rodar Analise' pra calcular o risco de cada ativo.",
            font=FONTE_TEXTO, text_color=COR_TEXTO_SUAVE,
        ).pack(pady=40)

    def _rodar_analise(self):
        for widget in self.area_resultado.winfo_children():
            widget.destroy()

        if not self.inventario.ativos:
            ctk.CTkLabel(
                self.area_resultado,
                text="Nenhum ativo cadastrado. Nao ha o que analisar.",
                font=FONTE_TEXTO, text_color=COR_TEXTO_SUAVE,
            ).pack(pady=40)
            self.ao_mudar_cycat("cycat_vazio")
            return

        self.ao_mudar_cycat("cycat_processando")
        self.update()

        modelo = ModeloAnaliseRisco(self.inventario.ativos, self.inventario.dependencias)
        resultados, diagnostico = modelo.calcular()

        # Diagnostico
        cor_diag = COR_BAIXA if diagnostico.invertivel else COR_CRITICA
        ctk.CTkLabel(
            self.area_resultado,
            text=f"{'✅' if diagnostico.invertivel else '⚠️'}  {diagnostico.mensagem}",
            font=FONTE_SUBTITULO, text_color=cor_diag,
            wraplength=800, justify="left",
        ).pack(anchor="w", padx=15, pady=(10, 5))

        info = (
            f"Diagonal dominante: {'sim' if diagnostico.diagonal_dominante else 'nao'}  •  "
            f"Determinante: {diagnostico.determinante:.3f}  •  "
            f"Numero de condicao: {diagnostico.numero_condicao:.2e}"
        )
        ctk.CTkLabel(
            self.area_resultado, text=info,
            font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # Cabecalho da tabela
        cab = ctk.CTkFrame(self.area_resultado, fg_color="transparent")
        cab.pack(fill="x", padx=15, pady=(5, 3))
        colunas_cab = [
            ("ID", 50),
            ("Hostname", 160),
            ("Tipo", 130),
            ("Risco Proprio (b)", 130),
            ("Risco Efetivo (x)", 130),
            ("Comparacao", 220),
        ]
        for texto, largura in colunas_cab:
            ctk.CTkLabel(
                cab, text=texto,
                font=(FONTE_BOTAO[0], 12, "bold"),
                text_color=COR_TEXTO_SUAVE,
                width=largura, anchor="w",
            ).pack(side="left")

        sep = ctk.CTkFrame(self.area_resultado, height=1, fg_color=COR_FUNDO_MEDIO)
        sep.pack(fill="x", padx=15)

        # Calcula o risco maximo pra escala relativa das barras
        riscos_usaveis = [
            (r.risco_efetivo if r.risco_efetivo is not None else r.risco_proprio)
            for r in resultados
        ]
        risco_maximo = max(riscos_usaveis) if riscos_usaveis else 0

        # Ordena por risco efetivo (maior primeiro)
        ordenado = sorted(
            resultados,
            key=lambda r: (r.risco_efetivo if r.risco_efetivo is not None else r.risco_proprio),
            reverse=True,
        )

        for r in ordenado:
            self._linha_resultado(r, risco_maximo)

        # Cycat por risco maximo
        if risco_maximo >= 10:
            self.ao_mudar_cycat("cycat_vuln_critica")
        elif risco_maximo >= 2:
            self.ao_mudar_cycat("cycat_vuln_media")
        else:
            self.ao_mudar_cycat("cycat_sucesso")

    def _linha_resultado(self, r, risco_maximo):
        linha = ctk.CTkFrame(self.area_resultado, fg_color="transparent")
        linha.pack(fill="x", padx=15, pady=2)

        def label(texto, largura, cor=COR_TEXTO, negrito=False):
            fonte = (FONTE_TEXTO[0], FONTE_TEXTO[1], "bold") if negrito else FONTE_TEXTO
            ctk.CTkLabel(
                linha, text=texto, font=fonte, text_color=cor,
                width=largura, anchor="w",
            ).pack(side="left")

        label(str(r.equipamento.id_ativo), 50)
        label(r.equipamento.hostname, 160)
        label(r.equipamento.tipo.rotulo, 130)
        label(f"{r.risco_proprio:.3f}", 130,
              cor=cor_do_risco(r.risco_proprio), negrito=True)

        if r.risco_efetivo is not None:
            label(f"{r.risco_efetivo:.3f}", 130,
                  cor=cor_do_risco(r.risco_efetivo), negrito=True)
        else:
            label("—", 130, cor=COR_TEXTO_SUAVE)

        # Barra de comparacao + porcentagem
        risco_usavel = r.risco_efetivo if r.risco_efetivo is not None else r.risco_proprio
        fracao = (risco_usavel / risco_maximo) if risco_maximo > 0 else 0.0
        pct = fracao * 100
        cor_bar = cor_do_risco(risco_usavel)

        barra_wrap = ctk.CTkFrame(linha, fg_color="transparent", width=220)
        barra_wrap.pack(side="left")

        bar = ctk.CTkProgressBar(
            barra_wrap, width=150, height=12,
            progress_color=cor_bar,
            fg_color=COR_FUNDO_MEDIO,
        )
        bar.set(fracao)
        bar.pack(side="left", padx=(0, 8), pady=4)

        ctk.CTkLabel(
            barra_wrap, text=f"{pct:.0f}%",
            font=(FONTE_PEQUENA[0], 11, "bold"),
            text_color=cor_bar,
            width=50, anchor="w",
        ).pack(side="left")

    def _construir_dependencias(self):
        titulo_dep = ctk.CTkFrame(self, fg_color="transparent")
        titulo_dep.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            titulo_dep, text="🔗  Dependencias entre ativos",
            font=FONTE_SUBTITULO, text_color=COR_PRIMARIA,
        ).pack(side="left")

        if self.eh_admin:
            ctk.CTkButton(
                titulo_dep, text="+  Cadastrar",
                width=130, height=32, font=FONTE_BOTAO,
                fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
                text_color="white",
                command=self._abrir_cadastro_dep,
            ).pack(side="right")

        self.lista_dep = ctk.CTkScrollableFrame(
            self, fg_color=COR_FUNDO_CLARO, corner_radius=10,
        )
        self.lista_dep.pack(fill="both", expand=True)

        if not self.eh_admin:
            ctk.CTkLabel(
                self, text="🔒  Como Analista, voce pode visualizar e rodar a analise. Modificar dependencias e restrito ao Admin.",
                font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
                wraplength=800, justify="left",
            ).pack(anchor="w", pady=(10, 0))

        self._renderizar_dependencias()

    def _renderizar_dependencias(self):
        for widget in self.lista_dep.winfo_children():
            widget.destroy()

        deps = self.inventario.dependencias
        if not deps:
            ctk.CTkLabel(
                self.lista_dep,
                text="Nenhuma dependencia cadastrada.",
                font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
            ).pack(pady=15)
            return

        host = {a.id_ativo: a.hostname for a in self.inventario.ativos}

        for dep in deps:
            linha = ctk.CTkFrame(self.lista_dep, fg_color="transparent")
            linha.pack(fill="x", padx=15, pady=3)

            texto = (
                f"{host.get(dep.id_destino, '?')} (#{dep.id_destino})  "
                f"herda  {dep.fracao:.0%}  do risco de  "
                f"{host.get(dep.id_origem, '?')} (#{dep.id_origem})"
            )
            ctk.CTkLabel(
                linha, text=texto,
                font=FONTE_TEXTO, text_color=COR_TEXTO,
                anchor="w",
            ).pack(side="left", fill="x", expand=True)

            if self.eh_admin:
                ctk.CTkButton(
                    linha, text="Remover",
                    width=90, height=28, font=FONTE_PEQUENA,
                    fg_color="transparent",
                    border_width=1, border_color=COR_CRITICA,
                    text_color=COR_CRITICA,
                    hover_color=COR_FUNDO,
                    command=lambda d=dep: self._remover_dep(d),
                ).pack(side="right")

    def _abrir_cadastro_dep(self):
        if len(self.inventario.ativos) < 2:
            messagebox.showwarning(
                "Poucos ativos",
                "Cadastre pelo menos 2 ativos antes de criar uma dependencia.",
            )
            return
        FormularioDependencia(
            master=self, inventario=self.inventario,
            ao_salvar=lambda: (self._renderizar_dependencias(),
                               self.ao_mudar_cycat("cycat_sucesso")),
        )

    def _remover_dep(self, dep):
        if not messagebox.askyesno(
            "Confirmar", f"Remover a dependencia #{dep.id_destino} ← #{dep.id_origem}?",
        ):
            return
        try:
            self.inventario.remover_dependencia(dep.id_origem, dep.id_destino)
            self._renderizar_dependencias()
            self.ao_mudar_cycat("cycat_sucesso")
        except ErroInventario as erro:
            messagebox.showerror("Erro", str(erro))


class FormularioDependencia(ctk.CTkToplevel):
    """Pop-up pra cadastrar dependencia."""

    def __init__(self, master, inventario, ao_salvar):
        super().__init__(master)
        self.inventario = inventario
        self.ao_salvar = ao_salvar

        self.title("Cadastrar Dependencia")
        self.geometry("480x440")
        self.configure(fg_color=COR_FUNDO)
        self.transient(master)
        self.grab_set()

        self.bind("<Return>", lambda e: self._salvar())
        self.bind("<Escape>", lambda e: self.destroy())

        self._construir()

    def _construir(self):
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.pack(fill="both", expand=True, padx=25, pady=20)

        ctk.CTkLabel(
            box, text="Nova dependencia",
            font=FONTE_SUBTITULO, text_color=COR_PRIMARIA,
        ).pack(anchor="w", pady=(0, 15))

        self.ativos_map = {f"{a.id_ativo} - {a.hostname}": a for a in self.inventario.ativos}
        opcoes = list(self.ativos_map.keys())

        ctk.CTkLabel(box, text="Ativo de origem (quem causa risco)",
                     font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE).pack(anchor="w")
        self.combo_origem = ctk.CTkComboBox(
            box, values=opcoes, state="readonly", font=FONTE_TEXTO, width=420,
        )
        self.combo_origem.set(opcoes[0])
        self.combo_origem.pack(pady=(2, 10), fill="x")

        ctk.CTkLabel(box, text="Ativo de destino (quem herda o risco)",
                     font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE).pack(anchor="w")
        self.combo_destino = ctk.CTkComboBox(
            box, values=opcoes, state="readonly", font=FONTE_TEXTO, width=420,
        )
        self.combo_destino.set(opcoes[1] if len(opcoes) > 1 else opcoes[0])
        self.combo_destino.pack(pady=(2, 10), fill="x")

        ctk.CTkLabel(box, text="Fracao herdada (entre 0 e 1, exemplo: 0.5 = 50%)",
                     font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE).pack(anchor="w")
        self.entry_fracao = ctk.CTkEntry(box, font=FONTE_TEXTO, width=420, height=36)
        self.entry_fracao.pack(pady=(2, 10), fill="x")

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

        self.entry_fracao.focus()

    def _salvar(self):
        try:
            origem = self.ativos_map[self.combo_origem.get()]
            destino = self.ativos_map[self.combo_destino.get()]
            fracao = float(self.entry_fracao.get())
            self.inventario.cadastrar_dependencia(origem.id_ativo, destino.id_ativo, fracao)
            self.ao_salvar()
            self.destroy()
        except (ValueError, ErroInventario) as erro:
            self.label_erro.configure(text=str(erro))