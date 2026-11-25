"""Aba Vulnerabilidades - lista todas, cadastra manual ou via NVD (CVE ou tipo)."""

import customtkinter as ctk
from tkinter import messagebox

from enums import Severidade, StatusTratamento
from inventario import Inventario, ErroInventario
from modelos import Vulnerabilidade
from catalogo import buscar_no_nvd, buscar_por_palavra_chave, TIPOS_COMUNS_BUSCA, ErroCatalogo

from interface.tema import (
    COR_FUNDO, COR_FUNDO_CLARO, COR_FUNDO_MEDIO, COR_FUNDO_ESCURO,
    COR_PRIMARIA, COR_PRIMARIA_HOVER, COR_CRITICA,
    COR_TEXTO, COR_TEXTO_SUAVE,
    COR_BAIXA, COR_MEDIA, COR_ALTA,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_TEXTO,
    FONTE_BOTAO, FONTE_PEQUENA,
)
from interface.widget_cards_resumo import criar_cards_resumo


COR_POR_SEVERIDADE = {
    Severidade.BAIXA: COR_BAIXA,
    Severidade.MEDIA: COR_MEDIA,
    Severidade.ALTA: COR_ALTA,
    Severidade.CRITICA: COR_CRITICA,
}


class AbaVulnerabilidades(ctk.CTkFrame):
    """Aba que lista e gerencia vulnerabilidades em todos os ativos."""

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
            topo, text="🛡️  Vulnerabilidades",
            font=FONTE_TITULO, text_color=COR_PRIMARIA,
        ).pack(side="left")

        ctk.CTkButton(
            topo, text="🌐  NVD: Tipo",
            width=130, height=38, font=FONTE_BOTAO,
            fg_color="transparent",
            border_width=1, border_color=COR_PRIMARIA,
            text_color=COR_PRIMARIA, hover_color=COR_FUNDO_MEDIO,
            command=self._abrir_nvd_categoria,
        ).pack(side="right", padx=(5, 0))

        ctk.CTkButton(
            topo, text="🌐  NVD: CVE",
            width=130, height=38, font=FONTE_BOTAO,
            fg_color="transparent",
            border_width=1, border_color=COR_PRIMARIA,
            text_color=COR_PRIMARIA, hover_color=COR_FUNDO_MEDIO,
            command=self._abrir_nvd_cve,
        ).pack(side="right", padx=(5, 0))

        ctk.CTkButton(
            topo, text="+  Cadastrar",
            width=140, height=38, font=FONTE_BOTAO,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            text_color="white",
            command=self._abrir_cadastro,
        ).pack(side="right", padx=(5, 0))

        # Cards de resumo
        self._construir_cards_resumo()

        # Lista (card com borda)
        card_lista = ctk.CTkFrame(
            self, fg_color=COR_FUNDO_CLARO, corner_radius=12,
            border_width=2, border_color=COR_FUNDO_MEDIO,
        )
        card_lista.pack(fill="both", expand=True)

        self.lista = ctk.CTkScrollableFrame(card_lista, fg_color="transparent")
        self.lista.pack(fill="both", expand=True, padx=10, pady=10)

        if not self.eh_admin:
            ctk.CTkLabel(
                self,
                text="🔒  Como Analista, você pode cadastrar e atualizar o status. "
                     "Remoção é restrita ao Admin.",
                font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
                wraplength=800, justify="left",
            ).pack(anchor="w", pady=(10, 0))

        self._renderizar()

    def _construir_cards_resumo(self):
        pares = self._todas_vulns()
        total = len(pares)
        por_sev = {s: 0 for s in Severidade}
        por_status = {s: 0 for s in StatusTratamento}
        for _, v in pares:
            por_sev[v.severidade] = por_sev.get(v.severidade, 0) + 1
            por_status[v.status] = por_status.get(v.status, 0) + 1

        criticas = por_sev.get(Severidade.CRITICA, 0)
        altas = por_sev.get(Severidade.ALTA, 0)
        em_trat = por_status.get(StatusTratamento.EM_TRATAMENTO, 0)
        corrigidas = por_status.get(StatusTratamento.CORRIGIDA, 0)

        cards = criar_cards_resumo(self, [
            {"icone": "🛡️", "titulo": "TOTAL", "valor": total},
            {"icone": "🔴", "titulo": "CRÍTICAS", "valor": criticas,
             "cor_valor": COR_CRITICA if criticas else COR_PRIMARIA},
            {"icone": "🟠", "titulo": "ALTAS", "valor": altas,
             "cor_valor": COR_ALTA if altas else COR_PRIMARIA},
            {"icone": "⚙️", "titulo": "EM TRATAMENTO", "valor": em_trat},
            {"icone": "✅", "titulo": "CORRIGIDAS", "valor": corrigidas,
             "cor_valor": COR_BAIXA if corrigidas else COR_PRIMARIA},
        ])
        cards.pack(fill="x", pady=(0, 15))

    def _todas_vulns(self):
        return [(a, v) for a in self.inventario.ativos for v in a.vulnerabilidades]

    def _renderizar(self):
        for widget in self.lista.winfo_children():
            widget.destroy()

        pares = self._todas_vulns()

        if not pares:
            ctk.CTkLabel(
                self.lista,
                text="Nenhuma vulnerabilidade cadastrada.\nUse '+ Cadastrar' ou busque no NVD.",
                font=FONTE_TEXTO, text_color=COR_TEXTO_SUAVE,
                justify="center",
            ).pack(pady=50)
            self._notificar_cycat("cycat_vazio", "Sem vulnerabilidades",
                                  "Nenhum ativo tem vulnerabilidade cadastrada ainda.")
            return

        cab = ctk.CTkFrame(self.lista, fg_color="transparent")
        cab.pack(fill="x", padx=10, pady=(5, 5))
        colunas = [("CVE", 140), ("Ativo", 140), ("Categoria", 200),
                   ("Severidade", 120), ("CVSS", 60), ("Status", 130), ("", 160)]
        for texto, largura in colunas:
            ctk.CTkLabel(
                cab, text=texto,
                font=(FONTE_BOTAO[0], 12, "bold"),
                text_color=COR_TEXTO_SUAVE,
                width=largura, anchor="w",
            ).pack(side="left")

        sep = ctk.CTkFrame(self.lista, height=1, fg_color=COR_FUNDO_ESCURO)
        sep.pack(fill="x", padx=10)

        severidades_presentes = [v.severidade for _, v in pares if v.status not in (StatusTratamento.CORRIGIDA, StatusTratamento.ACEITA)]
        if Severidade.CRITICA in severidades_presentes:
            self._notificar_cycat("cycat_vuln_critica", "Atenção: vulnerabilidade crítica!",
                                  "Há uma ou mais vulnerabilidades críticas abertas.")
        elif Severidade.ALTA in severidades_presentes:
            self._notificar_cycat("cycat_vuln_media", "Vulnerabilidades altas abertas",
                                  "Vale priorizar o tratamento.")
        elif Severidade.MEDIA in severidades_presentes:
            self._notificar_cycat("cycat_vuln_media", "Vulnerabilidades médias",
                                  "Monitore e trate quando possível.")
        else:
            self._notificar_cycat("cycat_neutra", "Situação sob controle",
                                  "Nenhuma vulnerabilidade de severidade alta ou crítica em aberto.")

        for ativo, vuln in pares:
            self._linha(ativo, vuln)

    def _linha(self, ativo, vuln):
        linha = ctk.CTkFrame(self.lista, fg_color="transparent")
        linha.pack(fill="x", padx=10, pady=3)

        def label(texto, largura):
            ctk.CTkLabel(
                linha, text=texto,
                font=FONTE_TEXTO, text_color=COR_TEXTO,
                width=largura, anchor="w",
            ).pack(side="left")

        label(vuln.cve, 140)
        label(ativo.hostname, 140)
        label(vuln.categoria[:30], 200)

        cor = COR_POR_SEVERIDADE.get(vuln.severidade, COR_TEXTO)
        ctk.CTkLabel(
            linha, text=vuln.severidade.rotulo,
            font=(FONTE_TEXTO[0], FONTE_TEXTO[1], "bold"),
            text_color=cor, width=120, anchor="w",
        ).pack(side="left")

        label(f"{vuln.cvss:.1f}", 60)
        label(vuln.status.rotulo, 130)

        acoes = ctk.CTkFrame(linha, fg_color="transparent", width=160)
        acoes.pack(side="left")

        ctk.CTkButton(
            acoes, text="Status",
            width=70, height=30, font=FONTE_PEQUENA,
            fg_color="transparent",
            border_width=1, border_color=COR_PRIMARIA,
            text_color=COR_PRIMARIA, hover_color=COR_FUNDO,
            command=lambda: self._atualizar_status(ativo, vuln),
        ).pack(side="left", padx=(0, 5))

        if self.eh_admin:
            ctk.CTkButton(
                acoes, text="Excluir",
                width=80, height=30, font=FONTE_PEQUENA,
                fg_color="transparent",
                border_width=1, border_color=COR_CRITICA,
                text_color=COR_CRITICA, hover_color=COR_FUNDO,
                command=lambda: self._remover(ativo, vuln),
            ).pack(side="left")

    def _checar_ativos(self):
        if not self.inventario.ativos:
            messagebox.showwarning(
                "Sem ativos",
                "Cadastre pelo menos um ativo antes de adicionar vulnerabilidades.",
            )
            return False
        return True

    def _reconstruir_tudo(self):
        for w in self.winfo_children():
            w.destroy()
        self._construir()

    def _abrir_cadastro(self):
        if not self._checar_ativos():
            return
        FormularioVulnerabilidade(
            master=self, inventario=self.inventario,
            ao_salvar=lambda: (
                self._reconstruir_tudo(),
                self._notificar_cycat("cycat_sucesso", "Vulnerabilidade registrada",
                                      "Já conta no cálculo de risco."),
            ),
        )

    def _abrir_nvd_cve(self):
        if not self._checar_ativos():
            return
        FormularioNVDCve(
            master=self, inventario=self.inventario,
            ao_salvar=lambda: (
                self._reconstruir_tudo(),
                self._notificar_cycat("cycat_sucesso", "Importada do NVD",
                                      "Vulnerabilidade cadastrada com dados oficiais."),
            ),
        )

    def _abrir_nvd_categoria(self):
        if not self._checar_ativos():
            return
        FormularioNVDCategoria(
            master=self, inventario=self.inventario,
            ao_salvar=lambda: (
                self._reconstruir_tudo(),
                self._notificar_cycat("cycat_sucesso", "Importada do NVD",
                                      "Vulnerabilidade cadastrada com dados oficiais."),
            ),
        )

    def _atualizar_status(self, ativo, vuln):
        FormularioStatus(
            master=self, inventario=self.inventario,
            ativo=ativo, vulnerabilidade=vuln,
            ao_salvar=lambda: (
                self._reconstruir_tudo(),
                self._notificar_cycat("cycat_sucesso", "Status atualizado",
                                      "Nova situação registrada."),
            ),
        )

    def _remover(self, ativo, vuln):
        if not messagebox.askyesno(
            "Confirmar exclusão",
            f"Excluir a vulnerabilidade '{vuln.cve}' do ativo '{ativo.hostname}'?",
        ):
            return
        try:
            self.inventario.remover_vulnerabilidade(ativo.id_ativo, vuln.cve)
            self._reconstruir_tudo()
            self._notificar_cycat("cycat_sucesso", "Vulnerabilidade removida", "")
        except ErroInventario as erro:
            messagebox.showerror("Erro", str(erro))
            self._notificar_cycat("cycat_erro", "Erro ao remover", str(erro))


class FormularioVulnerabilidade(ctk.CTkToplevel):
    """Pop-up para cadastrar vulnerabilidade manual."""

    def __init__(self, master, inventario, ao_salvar):
        super().__init__(master)
        self.inventario = inventario
        self.ao_salvar = ao_salvar

        self.title("Cadastrar Vulnerabilidade")
        self.geometry("540x720")
        self.minsize(540, 680)
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
            box, text="Cadastrar vulnerabilidade",
            font=FONTE_SUBTITULO, text_color=COR_PRIMARIA,
        ).pack(anchor="w", pady=(0, 15))

        self._label(box, "Ativo")
        self.ativos_map = {f"{a.id_ativo} - {a.hostname}": a for a in self.inventario.ativos}
        self.combo_ativo = ctk.CTkComboBox(
            box, values=list(self.ativos_map.keys()),
            state="readonly", font=FONTE_TEXTO, width=480,
        )
        self.combo_ativo.set(list(self.ativos_map.keys())[0])
        self.combo_ativo.pack(pady=(2, 10), fill="x")

        self.entry_cve = self._entry(box, "CVE (ex: CVE-2021-44228)")
        self.entry_descricao = self._entry(box, "Descrição")
        self.entry_categoria = self._entry(box, "Categoria (ex: Injeção de SQL)")

        self._label(box, "Severidade")
        self.severidades_map = {s.rotulo: s for s in Severidade}
        self.combo_sev = ctk.CTkComboBox(
            box, values=list(self.severidades_map.keys()),
            state="readonly", font=FONTE_TEXTO, width=480,
        )
        self.combo_sev.set(Severidade.MEDIA.rotulo)
        self.combo_sev.pack(pady=(2, 10), fill="x")

        self.entry_cvss = self._entry(box, "CVSS (opcional - em branco usa o padrão da severidade)")

        self.label_erro = ctk.CTkLabel(
            box, text="", text_color=COR_CRITICA, font=FONTE_PEQUENA,
            wraplength=480, justify="left",
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

        self.entry_cve.focus()

    def _label(self, master, texto):
        ctk.CTkLabel(master, text=texto,
                     font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE).pack(anchor="w")

    def _entry(self, master, label):
        self._label(master, label)
        entry = ctk.CTkEntry(master, font=FONTE_TEXTO, width=480, height=36)
        entry.pack(pady=(2, 10), fill="x")
        return entry

    def _salvar(self):
        try:
            ativo = self.ativos_map[self.combo_ativo.get()]
            sev = self.severidades_map[self.combo_sev.get()]
            cvss_texto = self.entry_cvss.get().strip()
            cvss = float(cvss_texto) if cvss_texto else None

            vuln = Vulnerabilidade(
                cve=self.entry_cve.get(),
                descricao=self.entry_descricao.get(),
                categoria=self.entry_categoria.get(),
                severidade=sev, cvss=cvss,
            )
            self.inventario.adicionar_vulnerabilidade(ativo.id_ativo, vuln)
            self.ao_salvar()
            self.destroy()
        except (ValueError, ErroInventario) as erro:
            self.label_erro.configure(text=str(erro))


class FormularioNVDCve(ctk.CTkToplevel):
    """Pop-up para buscar UM CVE específico no NVD."""

    def __init__(self, master, inventario, ao_salvar):
        super().__init__(master)
        self.inventario = inventario
        self.ao_salvar = ao_salvar
        self.vuln_encontrada = None

        self.title("Buscar no NVD por CVE")
        self.geometry("580x580")
        self.minsize(580, 540)
        self.configure(fg_color=COR_FUNDO)
        self.transient(master)
        self.grab_set()

        self.bind("<Escape>", lambda e: self.destroy())

        self._construir()

    def _construir(self):
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.pack(fill="both", expand=True, padx=25, pady=20)

        ctk.CTkLabel(
            box, text="🌐  Buscar CVE específico no NVD",
            font=FONTE_SUBTITULO, text_color=COR_PRIMARIA,
        ).pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(box, text="Ativo que tem a vulnerabilidade",
                     font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE).pack(anchor="w")
        self.ativos_map = {f"{a.id_ativo} - {a.hostname}": a for a in self.inventario.ativos}
        self.combo_ativo = ctk.CTkComboBox(
            box, values=list(self.ativos_map.keys()),
            state="readonly", font=FONTE_TEXTO, width=520,
        )
        self.combo_ativo.set(list(self.ativos_map.keys())[0])
        self.combo_ativo.pack(pady=(2, 15), fill="x")

        ctk.CTkLabel(box, text="Identificador CVE (ex: CVE-2021-44228)",
                     font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE).pack(anchor="w")
        linha_busca = ctk.CTkFrame(box, fg_color="transparent")
        linha_busca.pack(fill="x", pady=(2, 10))
        self.entry_cve = ctk.CTkEntry(linha_busca, font=FONTE_TEXTO, height=36)
        self.entry_cve.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_cve.bind("<Return>", lambda e: self._buscar())

        ctk.CTkButton(
            linha_busca, text="Buscar",
            width=100, height=36, font=FONTE_BOTAO,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            text_color="white", command=self._buscar,
        ).pack(side="right")

        self.preview = ctk.CTkFrame(box, fg_color=COR_FUNDO_CLARO, corner_radius=8,
                                    border_width=1, border_color=COR_FUNDO_MEDIO)
        self.preview.pack(fill="both", expand=True, pady=(10, 0))

        self.label_preview = ctk.CTkLabel(
            self.preview,
            text="Digite um CVE acima e clique em 'Buscar'.\n\n"
                 "Exemplos que sempre funcionam:\n"
                 "CVE-2021-44228 (Log4Shell)\nCVE-2014-0160 (Heartbleed)",
            font=FONTE_TEXTO, text_color=COR_TEXTO_SUAVE, justify="center",
        )
        self.label_preview.pack(expand=True, padx=20, pady=20)

        self.botoes_frame = ctk.CTkFrame(box, fg_color="transparent")
        self.botoes_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(
            self.botoes_frame, text="Fechar",
            width=120, height=38, font=FONTE_BOTAO,
            fg_color="transparent",
            border_width=1, border_color=COR_TEXTO_SUAVE,
            text_color=COR_TEXTO, hover_color=COR_FUNDO_MEDIO,
            command=self.destroy,
        ).pack(side="right", padx=(5, 0))

        self.botao_cadastrar = ctk.CTkButton(
            self.botoes_frame, text="Cadastrar",
            width=140, height=38, font=FONTE_BOTAO,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            text_color="white", command=self._cadastrar, state="disabled",
        )
        self.botao_cadastrar.pack(side="right")

        self.entry_cve.focus()

    def _buscar(self):
        cve_id = self.entry_cve.get().strip()
        if not cve_id:
            return
        self.label_preview.configure(
            text="🔄  Buscando no NVD... (pode levar alguns segundos)",
            text_color=COR_TEXTO_SUAVE,
        )
        self.update()
        try:
            self.vuln_encontrada = buscar_no_nvd(cve_id)
            v = self.vuln_encontrada
            texto = (
                f"CVE: {v.cve}\n\n"
                f"Descrição:\n{v.descricao}\n\n"
                f"Categoria: {v.categoria}\n"
                f"Severidade: {v.severidade.rotulo}\n"
                f"CVSS: {v.cvss:.1f}"
            )
            self.label_preview.configure(text=texto, text_color=COR_TEXTO, justify="left")
            self.botao_cadastrar.configure(state="normal")
        except ErroCatalogo as erro:
            self.vuln_encontrada = None
            self.label_preview.configure(text=f"❌  {erro}", text_color=COR_CRITICA)
            self.botao_cadastrar.configure(state="disabled")

    def _cadastrar(self):
        if not self.vuln_encontrada:
            return
        try:
            ativo = self.ativos_map[self.combo_ativo.get()]
            v = self.vuln_encontrada
            vuln = Vulnerabilidade(
                cve=v.cve, descricao=v.descricao,
                categoria=v.categoria, severidade=v.severidade, cvss=v.cvss,
            )
            self.inventario.adicionar_vulnerabilidade(ativo.id_ativo, vuln)
            self.ao_salvar()
            self.destroy()
        except (ValueError, ErroInventario) as erro:
            messagebox.showerror("Erro ao cadastrar", str(erro))


class FormularioNVDCategoria(ctk.CTkToplevel):
    """Pop-up para buscar vulnerabilidades no NVD por tipo/palavra-chave."""

    def __init__(self, master, inventario, ao_salvar):
        super().__init__(master)
        self.inventario = inventario
        self.ao_salvar = ao_salvar
        self.resultados = []

        self.title("Buscar no NVD por Tipo")
        self.geometry("720x660")
        self.minsize(720, 620)
        self.configure(fg_color=COR_FUNDO)
        self.transient(master)
        self.grab_set()

        self.bind("<Escape>", lambda e: self.destroy())

        self._construir()

    def _construir(self):
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.pack(fill="both", expand=True, padx=25, pady=20)

        ctk.CTkLabel(
            box, text="🌐  Buscar por tipo de vulnerabilidade",
            font=FONTE_SUBTITULO, text_color=COR_PRIMARIA,
        ).pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(box, text="Ativo onde vai cadastrar",
                     font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE).pack(anchor="w")
        self.ativos_map = {f"{a.id_ativo} - {a.hostname}": a for a in self.inventario.ativos}
        self.combo_ativo = ctk.CTkComboBox(
            box, values=list(self.ativos_map.keys()),
            state="readonly", font=FONTE_TEXTO, width=660,
        )
        self.combo_ativo.set(list(self.ativos_map.keys())[0])
        self.combo_ativo.pack(pady=(2, 15), fill="x")

        self.tipos_ptbr_para_en = {rotulo: termo_en for rotulo, termo_en in TIPOS_COMUNS_BUSCA.values()}
        opcoes = list(self.tipos_ptbr_para_en.keys())

        ctk.CTkLabel(
            box, text="Tipo de vulnerabilidade (escolha um ou digite o seu em inglês)",
            font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
        ).pack(anchor="w")
        linha_busca = ctk.CTkFrame(box, fg_color="transparent")
        linha_busca.pack(fill="x", pady=(2, 10))

        self.combo_tipo = ctk.CTkComboBox(
            linha_busca, values=opcoes,
            font=FONTE_TEXTO, height=36,
        )
        self.combo_tipo.set(opcoes[0])
        self.combo_tipo.pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(
            linha_busca, text="Buscar",
            width=100, height=36, font=FONTE_BOTAO,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            text_color="white", command=self._buscar,
        ).pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(
            box, fg_color=COR_FUNDO_CLARO, corner_radius=8,
        )
        self.scroll.pack(fill="both", expand=True, pady=(10, 0))

        self._placeholder_scroll()

        botoes = ctk.CTkFrame(box, fg_color="transparent")
        botoes.pack(fill="x", pady=(10, 0))
        ctk.CTkButton(
            botoes, text="Fechar",
            width=120, height=38, font=FONTE_BOTAO,
            fg_color="transparent",
            border_width=1, border_color=COR_TEXTO_SUAVE,
            text_color=COR_TEXTO, hover_color=COR_FUNDO_MEDIO,
            command=self.destroy,
        ).pack(side="right")

        self.combo_tipo.focus()

    def _placeholder_scroll(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.scroll,
            text="Escolha um tipo acima e clique em 'Buscar'.\n"
                 "Vai aparecer uma lista de CVEs reais desse tipo para você escolher qual cadastrar.",
            font=FONTE_TEXTO, text_color=COR_TEXTO_SUAVE, justify="center",
        ).pack(expand=True, padx=20, pady=40)

    def _buscar(self):
        termo_ui = self.combo_tipo.get().strip()
        termo_busca = self.tipos_ptbr_para_en.get(termo_ui, termo_ui)
        if not termo_busca:
            return

        for w in self.scroll.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.scroll,
            text=f"🔄  Buscando '{termo_ui}' no NVD...\n"
                 "(pode levar 5-10 segundos por causa da tradução)",
            font=FONTE_TEXTO, text_color=COR_TEXTO_SUAVE, justify="center",
        ).pack(expand=True, padx=20, pady=40)
        self.update()

        try:
            self.resultados = buscar_por_palavra_chave(termo_busca, limite=5)
        except ErroCatalogo as erro:
            for w in self.scroll.winfo_children():
                w.destroy()
            ctk.CTkLabel(
                self.scroll, text=f"❌  {erro}",
                font=FONTE_TEXTO, text_color=COR_CRITICA, justify="center",
            ).pack(expand=True, padx=20, pady=40)
            return

        self._renderizar_resultados()

    def _renderizar_resultados(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        for vuln in self.resultados:
            self._card(vuln)

    def _card(self, vuln):
        card = ctk.CTkFrame(self.scroll, fg_color=COR_FUNDO, corner_radius=8,
                            border_width=1, border_color=COR_FUNDO_MEDIO)
        card.pack(fill="x", padx=5, pady=5)

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=10, pady=(8, 2))

        ctk.CTkLabel(
            topo, text=vuln.cve,
            font=(FONTE_BOTAO[0], 13, "bold"), text_color=COR_PRIMARIA,
        ).pack(side="left")

        cor = COR_POR_SEVERIDADE.get(vuln.severidade, COR_TEXTO)
        ctk.CTkLabel(
            topo, text=f"{vuln.severidade.rotulo} (CVSS {vuln.cvss:.1f})",
            font=(FONTE_TEXTO[0], 12, "bold"), text_color=cor,
        ).pack(side="right")

        ctk.CTkLabel(
            card, text=f"Categoria: {vuln.categoria}",
            font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE,
        ).pack(anchor="w", padx=10)

        texto = vuln.descricao
        if len(texto) > 280:
            texto = texto[:280] + "..."
        ctk.CTkLabel(
            card, text=texto,
            font=FONTE_PEQUENA, text_color=COR_TEXTO,
            wraplength=600, justify="left",
        ).pack(anchor="w", padx=10, pady=(4, 6))

        ctk.CTkButton(
            card, text="+ Cadastrar esta",
            width=140, height=30, font=FONTE_PEQUENA,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            text_color="white",
            command=lambda v=vuln: self._cadastrar(v),
        ).pack(anchor="e", padx=10, pady=(0, 8))

    def _cadastrar(self, vuln_conhecida):
        try:
            ativo = self.ativos_map[self.combo_ativo.get()]
            vuln = Vulnerabilidade(
                cve=vuln_conhecida.cve, descricao=vuln_conhecida.descricao,
                categoria=vuln_conhecida.categoria,
                severidade=vuln_conhecida.severidade, cvss=vuln_conhecida.cvss,
            )
            self.inventario.adicionar_vulnerabilidade(ativo.id_ativo, vuln)
            self.ao_salvar()
            messagebox.showinfo("Cadastrada", f"{vuln.cve} cadastrada em {ativo.hostname}.")
        except (ValueError, ErroInventario) as erro:
            messagebox.showerror("Erro ao cadastrar", str(erro))


class FormularioStatus(ctk.CTkToplevel):
    """Pop-up para atualizar status de uma vulnerabilidade."""

    def __init__(self, master, inventario, ativo, vulnerabilidade, ao_salvar):
        super().__init__(master)
        self.inventario = inventario
        self.ativo = ativo
        self.vulnerabilidade = vulnerabilidade
        self.ao_salvar = ao_salvar

        self.title("Atualizar Status")
        self.geometry("420x320")
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
            box, text=f"Status de {self.vulnerabilidade.cve}",
            font=FONTE_SUBTITULO, text_color=COR_PRIMARIA,
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            box, text=f"Ativo: {self.ativo.hostname}\nAtual: {self.vulnerabilidade.status.rotulo}",
            font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE, justify="left",
        ).pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(box, text="Novo status",
                     font=FONTE_PEQUENA, text_color=COR_TEXTO_SUAVE).pack(anchor="w")
        self.status_map = {s.rotulo: s for s in StatusTratamento}
        self.combo = ctk.CTkComboBox(
            box, values=list(self.status_map.keys()),
            state="readonly", font=FONTE_TEXTO, width=360,
        )
        self.combo.set(self.vulnerabilidade.status.rotulo)
        self.combo.pack(pady=(2, 10), fill="x")

        self.label_erro = ctk.CTkLabel(
            box, text="", text_color=COR_CRITICA, font=FONTE_PEQUENA,
            wraplength=360, justify="left",
        )
        self.label_erro.pack(anchor="w", pady=(5, 0))

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

    def _salvar(self):
        try:
            novo = self.status_map[self.combo.get()]
            self.inventario.atualizar_status_vulnerabilidade(
                self.ativo.id_ativo, self.vulnerabilidade.cve, novo,
            )
            self.ao_salvar()
            self.destroy()
        except (ValueError, ErroInventario) as erro:
            self.label_erro.configure(text=str(erro))