"""Tela de cadastro e consulta de produtos."""

from tkinter import messagebox

import customtkinter as ctk

from src.functions.produtos import Produtos
from src.ui import formato, tema
from src.ui.produto_dialog import ProdutoDialog
from src.ui.widgets.tabela import Tabela

COLUNAS = [
    ("id", "ID", 60, "center"),
    ("codigo", "Código", 130, "w"),
    ("produto", "Produto", 260, "w"),
    ("ncm", "NCM", 130, "w"),
    ("cx", "Cx", 70, "center"),
    ("ipi", "IPI", 95, "e"),
    ("custo", "Custo", 140, "e"),
    ("peso", "Peso", 130, "e"),
    ("cubagem", "Cubagem", 140, "e"),
]


class ProdutosPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._montar()
        self.recarregar()

    def _montar(self) -> None:
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        topo.grid_columnconfigure(0, weight=1)

        titulos = ctk.CTkFrame(topo, fg_color="transparent")
        titulos.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(titulos, text="Produtos", font=tema.FONTE_TITULO,
                     text_color=tema.TEXTO, anchor="w").pack(anchor="w")
        self.subtitulo = ctk.CTkLabel(titulos, text="", font=tema.FONTE_PEQUENA,
                                      text_color=tema.TEXTO_SUAVE, anchor="w")
        self.subtitulo.pack(anchor="w")

        ctk.CTkButton(topo, text="+  Novo produto", command=self._novo, height=tema.ALTURA_BOTAO,
                      width=200, corner_radius=tema.RAIO, font=tema.FONTE_SUBTITULO,
                      fg_color=tema.ACENTO, hover_color=tema.ACENTO_HOVER).grid(row=0, column=1)

        barra = ctk.CTkFrame(self, fg_color=tema.CARD, corner_radius=tema.RAIO,
                             border_width=1, border_color=tema.BORDA)
        barra.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        barra.grid_columnconfigure(0, weight=1)

        self.busca = ctk.CTkEntry(barra, placeholder_text="Buscar por código, nome ou id…",
                                  height=tema.ALTURA_CAMPO, font=tema.FONTE_CORPO,
                                  border_width=0, fg_color="transparent")
        self.busca.grid(row=0, column=0, sticky="ew", padx=(16, 8), pady=6)
        self.busca.bind("<KeyRelease>", lambda _e: self.recarregar())

        ctk.CTkButton(barra, text="Editar", command=self._editar, width=110,
                      height=tema.ALTURA_BOTAO_PEQUENO, corner_radius=8, font=tema.FONTE_CORPO,
                      fg_color=tema.NEUTRO, hover_color=tema.NEUTRO_HOVER,
                      text_color=tema.TEXTO).grid(row=0, column=1, padx=4)
        ctk.CTkButton(barra, text="Excluir", command=self._excluir, width=110,
                      height=tema.ALTURA_BOTAO_PEQUENO, corner_radius=8, font=tema.FONTE_CORPO,
                      fg_color="transparent", hover_color=tema.NEUTRO_HOVER, text_color=tema.PERIGO,
                      border_width=1, border_color=tema.BORDA).grid(row=0, column=2, padx=(4, 12))

        self.tabela = Tabela(self, COLUNAS, on_duplo_clique=self._editar)
        self.tabela.grid(row=2, column=0, sticky="nsew")

    # ---------- dados ----------

    def recarregar(self) -> None:
        produtos = Produtos.buscar(self.busca.get().strip())
        self.tabela.preencher([
            (
                p.id, p.id, p.codigo, p.produto, p.ncm or "—", p.cx or 0,
                formato.percentual(p.ipi), formato.moeda(p.custo_com_desconto_e_ipi),
                formato.peso(p.peso), formato.cubagem(p.cubagem),
            )
            for p in produtos
        ])
        total = len(produtos)
        self.subtitulo.configure(text=f"{total} produto{'s' if total != 1 else ''} cadastrado{'s' if total != 1 else ''}")

    # ---------- ações ----------

    def _novo(self) -> None:
        ProdutoDialog(self.winfo_toplevel(), ao_salvar=self.recarregar)

    def _editar(self) -> None:
        produto_id = self.tabela.id_selecionado()
        if produto_id is None:
            return messagebox.showinfo("Editar produto", "Selecione um produto na tabela.")
        produto = Produtos.read(produto_id)
        if produto:
            ProdutoDialog(self.winfo_toplevel(), ao_salvar=self.recarregar, produto=produto)

    def _excluir(self) -> None:
        produto_id = self.tabela.id_selecionado()
        if produto_id is None:
            return messagebox.showinfo("Excluir produto", "Selecione um produto na tabela.")
        produto = Produtos.read(produto_id)
        if produto and messagebox.askyesno("Excluir produto", f"Excluir “{produto.produto}”?"):
            try:
                Produtos.delete(produto_id)
            except Exception:
                # produto referenciado por algum repasse (foreign key)
                messagebox.showerror(
                    "Excluir produto",
                    "Este produto está em algum repasse e não pode ser excluído.",
                )
            self.recarregar()
