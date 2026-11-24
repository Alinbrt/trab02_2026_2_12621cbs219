"""Aba Relatorios - gera relatorio completo do inventario + analise em TXT."""

from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk

from analise_risco import ModeloAnaliseRisco
from inventario import Inventario

from interface.tema import (
    COR_FUNDO, COR_FUNDO_CLARO, COR_FUNDO_MEDIO,
    COR_PRIMARIA, COR_PRIMARIA_HOVER,
    COR_TEXTO, COR_TEXTO_SUAVE,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_TEXTO,
    FONTE_BOTAO, FONTE_PEQUENA,
)


class AbaRelatorios(ctk.CTkFrame):
    """Gera relatorio em texto do estado atual do inventario."""

    def __init__(self, master, inventario: Inventario, perfil: str, ao_mudar_cycat=None):
        super().__init__(master, fg_color=COR_FUNDO)
        self.inventario = inventario
        self.perfil = perfil
        self.ao_mudar_cycat = ao_mudar_cycat or (lambda nome: None)
        self.ultimo_relatorio = ""
        self._construir()

    def _construir(self):
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            topo, text="📄  Relatorios",
            font=FONTE_TITULO, text_color=COR_PRIMARIA,
        ).pack(side="left")

        ctk.CTkButton(
            topo, text="📥  Salvar como TXT",
            width=160, height=36,
            font=FONTE_BOTAO,
            fg_color="transparent",
            border_width=1, border_color=COR_PRIMARIA,
            text_color=COR_PRIMARIA,
            hover_color=COR_FUNDO_MEDIO,
            command=self._salvar_txt,
        ).pack(side="right", padx=(5, 0))

        ctk.CTkButton(
            topo, text="▶  Gerar Relatorio",
            width=160, height=36,
            font=FONTE_BOTAO,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            text_color="white",
            command=self._gerar,
        ).pack(side="right")

        ctk.CTkLabel(
            self,
            text="Clique em 'Gerar Relatorio' pra ver o estado completo do inventario com analise de risco.",
            font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
            wraplength=900, justify="left",
        ).pack(anchor="w", pady=(0, 10))

        self.area = ctk.CTkTextbox(
            self, fg_color=COR_FUNDO_CLARO, text_color=COR_TEXTO,
            font=("Consolas", 12), wrap="word",
        )
        self.area.pack(fill="both", expand=True)
        self.area.insert("1.0", "Nenhum relatorio gerado ainda.")
        self.area.configure(state="disabled")

    def _gerar(self):
        self.ao_mudar_cycat("cycat_processando")
        self.update()

        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        linhas = []
        linhas.append("=" * 70)
        linhas.append(f"RELATORIO DO INVENTARIO CYCAT")
        linhas.append(f"Gerado em: {agora}")
        linhas.append("=" * 70)
        linhas.append("")

        ativos = self.inventario.ativos
        linhas.append(f"1. ATIVOS CADASTRADOS ({len(ativos)})")
        linhas.append("-" * 70)
        if not ativos:
            linhas.append("Nenhum ativo cadastrado.")
        else:
            for a in ativos:
                linhas.append(f"[#{a.id_ativo}] {a.hostname}")
                linhas.append(f"    Tipo:         {a.tipo.rotulo}")
                linhas.append(f"    Responsavel:  {a.responsavel}")
                linhas.append(f"    Localizacao:  {a.localizacao}")
                if a.descricao:
                    linhas.append(f"    Descricao:    {a.descricao}")
                vulns = a.vulnerabilidades
                linhas.append(f"    Vulnerabilidades: {len(vulns)}")
                for v in vulns:
                    linhas.append(f"      - [{v.cve}] {v.severidade.rotulo} "
                                  f"(CVSS {v.cvss:.1f}) - {v.status.rotulo}")
                    linhas.append(f"        Categoria: {v.categoria}")
                linhas.append("")

        deps = self.inventario.dependencias
        linhas.append(f"2. DEPENDENCIAS ({len(deps)})")
        linhas.append("-" * 70)
        if not deps:
            linhas.append("Nenhuma dependencia cadastrada.")
        else:
            host = {a.id_ativo: a.hostname for a in ativos}
            for d in deps:
                linhas.append(
                    f"  {host.get(d.id_destino, '?')} (#{d.id_destino}) "
                    f"← {d.fracao:.0%} de {host.get(d.id_origem, '?')} (#{d.id_origem})"
                )
        linhas.append("")

        # Analise
        linhas.append("3. ANALISE DE RISCO")
        linhas.append("-" * 70)
        if not ativos:
            linhas.append("Sem ativos pra analisar.")
        else:
            modelo = ModeloAnaliseRisco(ativos, deps)
            resultados, diagnostico = modelo.calcular()
            linhas.append(f"Status: {diagnostico.mensagem}")
            linhas.append(f"Diagonal dominante: {'sim' if diagnostico.diagonal_dominante else 'nao'}")
            linhas.append(f"Determinante: {diagnostico.determinante:.3f}")
            linhas.append(f"Numero de condicao: {diagnostico.numero_condicao:.2e}")
            linhas.append("")
            linhas.append(f"{'Hostname':<25} {'Tipo':<22} {'Risco Proprio':>15} {'Risco Efetivo':>15}")
            for r in sorted(resultados,
                            key=lambda r: (r.risco_efetivo if r.risco_efetivo is not None
                                           else r.risco_proprio),
                            reverse=True):
                efetivo = f"{r.risco_efetivo:.3f}" if r.risco_efetivo is not None else "—"
                linhas.append(
                    f"{r.equipamento.hostname[:24]:<25} {r.equipamento.tipo.rotulo[:21]:<22} "
                    f"{r.risco_proprio:>15.3f} {efetivo:>15}"
                )
        linhas.append("")
        linhas.append("=" * 70)
        linhas.append("Fim do relatorio.")

        self.ultimo_relatorio = "\n".join(linhas)

        self.area.configure(state="normal")
        self.area.delete("1.0", "end")
        self.area.insert("1.0", self.ultimo_relatorio)
        self.area.configure(state="disabled")
        self.ao_mudar_cycat("cycat_sucesso")

    def _salvar_txt(self):
        if not self.ultimo_relatorio:
            messagebox.showinfo("Aviso", "Gere um relatorio primeiro.")
            return
        caminho = filedialog.asksaveasfilename(
            title="Salvar relatorio",
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt")],
            initialfile=f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        )
        if not caminho:
            return
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(self.ultimo_relatorio)
            messagebox.showinfo("Salvo", f"Relatorio salvo em:\n{caminho}")
        except OSError as erro:
            messagebox.showerror("Erro", f"Nao foi possivel salvar: {erro}")