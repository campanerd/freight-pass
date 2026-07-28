"""Tabela baseada em ttk.Treeview, estilizada para combinar com o customtkinter."""

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from src.ui import tema


def aplicar_estilo() -> None:
    """(Re)aplica o estilo da tabela conforme o tema ativo. Chamar ao trocar de tema."""
    style = ttk.Style()
    style.theme_use("clam")

    fundo = tema.cor(tema.CARD)
    texto = tema.cor(tema.TEXTO)
    cabecalho = tema.cor(tema.CARD_ELEVADO)
    selecao = tema.cor(tema.ACENTO_SUAVE)
    borda = tema.cor(tema.BORDA)

    style.configure(
        "FP.Treeview",
        background=fundo,
        fieldbackground=fundo,
        foreground=texto,
        rowheight=34,
        borderwidth=0,
        font=tema.FONTE_CORPO,
    )
    style.configure(
        "FP.Treeview.Heading",
        background=cabecalho,
        foreground=tema.cor(tema.TEXTO_SUAVE),
        relief="flat",
        borderwidth=0,
        padding=(10, 8),
        font=tema.FONTE_PEQUENA,
    )
    style.map(
        "FP.Treeview",
        background=[("selected", selecao)],
        foreground=[("selected", tema.cor(tema.ACENTO))],
    )
    style.map("FP.Treeview.Heading", background=[("active", borda)])
    style.layout("FP.Treeview", [("FP.Treeview.treearea", {"sticky": "nswe"})])


class Tabela(ctk.CTkFrame):
    """Tabela com rolagem. `colunas` é uma lista de (chave, titulo, largura, ancora)."""

    def __init__(self, master, colunas, on_duplo_clique=None, **kwargs):
        super().__init__(master, fg_color=tema.CARD, corner_radius=tema.RAIO,
                         border_width=1, border_color=tema.BORDA, **kwargs)
        self.colunas = colunas
        aplicar_estilo()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        chaves = [c[0] for c in colunas]
        self.tree = ttk.Treeview(self, columns=chaves, show="headings", style="FP.Treeview",
                                 selectmode="browse")
        for chave, titulo, largura, ancora in colunas:
            self.tree.heading(chave, text=titulo.upper(), anchor=ancora)
            self.tree.column(chave, width=largura, anchor=ancora, stretch=True)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        scroll = ctk.CTkScrollbar(self, command=self.tree.yview)
        scroll.grid(row=0, column=1, sticky="ns", padx=(0, 6), pady=6)
        self.tree.configure(yscrollcommand=scroll.set)

        if on_duplo_clique:
            self.tree.bind("<Double-1>", lambda _e: on_duplo_clique())

    def preencher(self, linhas: list[tuple]) -> None:
        """Substitui todo o conteúdo. Cada linha é uma tupla: (id_registro, valor1, valor2, ...)."""
        self.tree.delete(*self.tree.get_children())
        for linha in linhas:
            self.tree.insert("", tk.END, iid=str(linha[0]), values=linha[1:])

    def id_selecionado(self) -> int | None:
        selecao = self.tree.selection()
        return int(selecao[0]) if selecao else None
