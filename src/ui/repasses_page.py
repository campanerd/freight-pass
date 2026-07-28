"""Tela de repasses: monta o pedido somando produtos e quantidades."""

from tkinter import messagebox

import customtkinter as ctk

from src.functions.produtos import Produtos
from src.functions.repasse import Repasse
from src.ui import formato, tema
from src.ui.widgets.autocomplete import AutocompleteProduto
from src.ui.widgets.tabela import Tabela

COLUNAS = [
    ("produto", "Produto", 220, "w"),
    ("qtd", "Qtd", 70, "center"),
    ("peso_un", "Peso un.", 110, "e"),
    ("peso_sub", "Peso total", 120, "e"),
    ("cub_sub", "Cubagem total", 130, "e"),
    ("valor_sub", "Valor total", 130, "e"),
]


class RepassesPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.repasse_atual = None
        self.produto_escolhido = None
        self.cartoes: dict[int, ctk.CTkFrame] = {}

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._montar_lista()
        self._montar_detalhe()
        self.recarregar()

    # ---------- coluna esquerda: lista de repasses ----------

    def _montar_lista(self) -> None:
        painel = ctk.CTkFrame(self, fg_color=tema.CARD, corner_radius=tema.RAIO,
                              border_width=1, border_color=tema.BORDA, width=300)
        painel.grid(row=0, column=0, sticky="nsw", padx=(0, 18))
        painel.grid_propagate(False)
        painel.grid_rowconfigure(1, weight=1)
        painel.grid_columnconfigure(0, weight=1)

        cabecalho = ctk.CTkFrame(painel, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        cabecalho.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(cabecalho, text="Repasses", font=tema.FONTE_SUBTITULO,
                     text_color=tema.TEXTO, anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkButton(cabecalho, text="+ Novo", command=self._novo_repasse, width=76, height=32,
                      corner_radius=8, font=tema.FONTE_CORPO, fg_color=tema.ACENTO,
                      hover_color=tema.ACENTO_HOVER).grid(row=0, column=1)

        self.lista = ctk.CTkScrollableFrame(painel, fg_color="transparent")
        self.lista.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 12))
        self.lista.grid_columnconfigure(0, weight=1)

    def _criar_cartao(self, repasse) -> ctk.CTkFrame:
        selecionado = self.repasse_atual and repasse.id == self.repasse_atual.id
        cartao = ctk.CTkFrame(self.lista, corner_radius=8,
                              fg_color=tema.ACENTO_SUAVE if selecionado else "transparent")
        cartao.pack(fill="x", padx=4, pady=3)
        cartao.grid_columnconfigure(0, weight=1)

        titulo = ctk.CTkLabel(cartao, text=f"Repasse #{repasse.id}", font=tema.FONTE_CORPO,
                              text_color=tema.ACENTO if selecionado else tema.TEXTO, anchor="w")
        titulo.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 0))

        data = (repasse.data_criacao or "")[:16]
        resumo = ctk.CTkLabel(cartao, text=f"{data}  ·  {formato.moeda(repasse.valor_total)}",
                              font=tema.FONTE_PEQUENA, text_color=tema.TEXTO_SUAVE, anchor="w")
        resumo.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        for widget in (cartao, titulo, resumo):
            widget.bind("<Button-1>", lambda _e, r=repasse: self._selecionar(r.id))
        return cartao

    # ---------- coluna direita: detalhe ----------

    def _montar_detalhe(self) -> None:
        self.detalhe = ctk.CTkFrame(self, fg_color="transparent")
        self.detalhe.grid(row=0, column=1, sticky="nsew")
        self.detalhe.grid_columnconfigure(0, weight=1)
        self.detalhe.grid_rowconfigure(3, weight=1)

        # cabeçalho
        topo = ctk.CTkFrame(self.detalhe, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        topo.grid_columnconfigure(0, weight=1)
        self.titulo = ctk.CTkLabel(topo, text="Nenhum repasse selecionado", font=tema.FONTE_TITULO,
                                   text_color=tema.TEXTO, anchor="w")
        self.titulo.grid(row=0, column=0, sticky="w")
        self.botao_excluir = ctk.CTkButton(
            topo, text="Excluir repasse", command=self._excluir_repasse, width=140, height=38,
            corner_radius=tema.RAIO, font=tema.FONTE_CORPO, fg_color="transparent",
            hover_color=tema.NEUTRO_HOVER, text_color=tema.PERIGO,
            border_width=1, border_color=tema.BORDA)
        self.botao_excluir.grid(row=0, column=1)

        # métricas
        metricas = ctk.CTkFrame(self.detalhe, fg_color="transparent")
        metricas.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        for coluna in range(3):
            metricas.grid_columnconfigure(coluna, weight=1)
        self.metrica_peso = self._criar_metrica(metricas, 0, "PESO TOTAL", tema.ACENTO)
        self.metrica_cubagem = self._criar_metrica(metricas, 1, "CUBAGEM TOTAL", tema.ACENTO)
        self.metrica_valor = self._criar_metrica(metricas, 2, "VALOR TOTAL", tema.SUCESSO)

        # adicionar produto
        adicionar = ctk.CTkFrame(self.detalhe, fg_color=tema.CARD, corner_radius=tema.RAIO,
                                 border_width=1, border_color=tema.BORDA)
        adicionar.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        adicionar.grid_columnconfigure(0, weight=1)

        self.autocomplete = AutocompleteProduto(adicionar, buscar_fn=Produtos.buscar,
                                                on_select=self._produto_selecionado)
        self.autocomplete.grid(row=0, column=0, sticky="ew", padx=(14, 8), pady=14)

        self.quantidade = ctk.CTkEntry(adicionar, placeholder_text="Qtd", width=90, height=38,
                                       font=tema.FONTE_CORPO, corner_radius=tema.RAIO,
                                       border_color=tema.BORDA, fg_color=tema.CARD_ELEVADO,
                                       justify="center")
        self.quantidade.grid(row=0, column=1, pady=14)
        self.quantidade.bind("<Return>", lambda _e: self._adicionar_item())

        ctk.CTkButton(adicionar, text="Adicionar", command=self._adicionar_item, width=120, height=38,
                      corner_radius=tema.RAIO, font=tema.FONTE_CORPO, fg_color=tema.ACENTO,
                      hover_color=tema.ACENTO_HOVER).grid(row=0, column=2, padx=14, pady=14)

        self.dica = ctk.CTkLabel(adicionar, text="", font=tema.FONTE_PEQUENA,
                                 text_color=tema.TEXTO_SUAVE, anchor="w")
        self.dica.grid(row=1, column=0, columnspan=3, sticky="ew", padx=16, pady=(0, 10))

        # itens
        self.tabela = Tabela(self.detalhe, COLUNAS)
        self.tabela.grid(row=3, column=0, sticky="nsew")

        rodape = ctk.CTkFrame(self.detalhe, fg_color="transparent")
        rodape.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        rodape.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(rodape, text="Remover item selecionado", command=self._remover_item,
                      width=200, height=36, corner_radius=tema.RAIO, font=tema.FONTE_CORPO,
                      fg_color=tema.NEUTRO, hover_color=tema.NEUTRO_HOVER,
                      text_color=tema.TEXTO).grid(row=0, column=1)

    def _criar_metrica(self, master, coluna: int, rotulo: str, cor_valor) -> ctk.CTkLabel:
        cartao = ctk.CTkFrame(master, fg_color=tema.CARD, corner_radius=tema.RAIO,
                              border_width=1, border_color=tema.BORDA)
        cartao.grid(row=0, column=coluna, sticky="ew", padx=(0 if coluna == 0 else 7, 0 if coluna == 2 else 7))
        ctk.CTkLabel(cartao, text=rotulo, font=tema.FONTE_PEQUENA, text_color=tema.TEXTO_SUAVE,
                     anchor="w").pack(anchor="w", padx=18, pady=(14, 0))
        valor = ctk.CTkLabel(cartao, text="—", font=tema.FONTE_METRICA, text_color=cor_valor, anchor="w")
        valor.pack(anchor="w", padx=18, pady=(0, 14))
        return valor

    # ---------- dados ----------

    def recarregar(self) -> None:
        repasses = Repasse.listar_todos()
        for widget in self.lista.winfo_children():
            widget.destroy()

        if not repasses:
            ctk.CTkLabel(self.lista, text="Nenhum repasse ainda.\nClique em “+ Novo”.",
                         font=tema.FONTE_PEQUENA, text_color=tema.TEXTO_SUAVE,
                         justify="left").pack(anchor="w", padx=12, pady=12)
            self.repasse_atual = None
        else:
            if self.repasse_atual is None or all(r.id != self.repasse_atual.id for r in repasses):
                self.repasse_atual = repasses[0]
            for repasse in repasses:
                self._criar_cartao(repasse)

        self._atualizar_detalhe()

    def _selecionar(self, repasse_id: int) -> None:
        self.repasse_atual = Repasse.read(repasse_id)
        self.recarregar()

    def _atualizar_detalhe(self) -> None:
        if self.repasse_atual is None:
            self.titulo.configure(text="Nenhum repasse selecionado")
            self.botao_excluir.configure(state="disabled")
            for metrica in (self.metrica_peso, self.metrica_cubagem, self.metrica_valor):
                metrica.configure(text="—")
            self.tabela.preencher([])
            return

        repasse = Repasse.read(self.repasse_atual.id)
        self.repasse_atual = repasse
        self.titulo.configure(text=f"Repasse #{repasse.id}")
        self.botao_excluir.configure(state="normal")
        self.metrica_peso.configure(text=formato.peso(repasse.peso_total))
        self.metrica_cubagem.configure(text=formato.cubagem(repasse.cubagem_total))
        self.metrica_valor.configure(text=formato.moeda(repasse.valor_total))

        itens = Repasse.listar_itens_detalhados(repasse.id)
        self.tabela.preencher([
            (
                item.item_id, item.produto, item.quantidade,
                formato.peso(item.peso_unitario), formato.peso(item.peso_subtotal),
                formato.cubagem(item.cubagem_subtotal), formato.moeda(item.valor_subtotal),
            )
            for item in itens
        ])

    # ---------- ações ----------

    def _novo_repasse(self) -> None:
        self.repasse_atual = Repasse.create()
        self.recarregar()

    def _excluir_repasse(self) -> None:
        if self.repasse_atual and messagebox.askyesno(
            "Excluir repasse", f"Excluir o repasse #{self.repasse_atual.id} e todos os seus itens?"
        ):
            Repasse.delete(self.repasse_atual.id)
            self.repasse_atual = None
            self.recarregar()

    def _produto_selecionado(self, produto) -> None:
        self.produto_escolhido = produto
        self.dica.configure(
            text=f"#{produto.id} · {produto.produto} — {formato.peso(produto.peso)} · "
                 f"{formato.cubagem(produto.cubagem)} · {formato.moeda(produto.custo_com_desconto_e_ipi)} por unidade"
        )
        self.quantidade.focus_set()

    def _adicionar_item(self) -> None:
        if self.repasse_atual is None:
            return messagebox.showinfo("Adicionar item", "Crie ou selecione um repasse primeiro.")
        if self.produto_escolhido is None:
            return messagebox.showinfo("Adicionar item", "Escolha um produto na busca.")

        qtd = formato.ler_inteiro(self.quantidade.get())
        if qtd is None or qtd <= 0:
            return messagebox.showinfo("Adicionar item", "Informe uma quantidade válida (número inteiro maior que zero).")

        Repasse.adicionar_item(self.repasse_atual.id, self.produto_escolhido.id, qtd)
        self.produto_escolhido = None
        self.autocomplete.limpar()
        self.quantidade.delete(0, "end")
        self.dica.configure(text="")
        self.recarregar()
        self.autocomplete.focar()

    def _remover_item(self) -> None:
        item_id = self.tabela.id_selecionado()
        if item_id is None:
            return messagebox.showinfo("Remover item", "Selecione um item na tabela.")
        Repasse.remover_item(item_id)
        self.recarregar()
