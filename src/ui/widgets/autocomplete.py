"""Campo de busca com sugestões: digita o nome (ou o id) e escolhe o produto."""

import customtkinter as ctk

from src.ui import tema

MAX_SUGESTOES = 8
ALTURA_LINHA = 44
ESPACO_LINHA = 3
LARGURA_MINIMA = 360


class AutocompleteProduto(ctk.CTkFrame):
    """Entry que sugere produtos conforme o usuário digita.

    buscar_fn(termo) -> lista de produtos; on_select(produto) é chamado ao escolher um.
    """

    def __init__(self, master, buscar_fn, on_select, placeholder="Busque pelo nome ou id do produto…", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.buscar_fn = buscar_fn
        self.on_select = on_select
        self.sugestoes: list = []
        self.indice_ativo = -1
        self.selecionado = None
        self._linhas: list[ctk.CTkFrame] = []

        self.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(
            self, placeholder_text=placeholder, height=38, font=tema.FONTE_CORPO,
            corner_radius=tema.RAIO, border_color=tema.BORDA, fg_color=tema.CARD,
        )
        self.entry.grid(row=0, column=0, sticky="ew")

        self.entry.bind("<KeyRelease>", self._ao_digitar)
        self.entry.bind("<Down>", self._proxima)
        self.entry.bind("<Up>", self._anterior)
        self.entry.bind("<Return>", self._confirmar)
        self.entry.bind("<Escape>", lambda _e: self._esconder())
        self.entry.bind("<FocusOut>", lambda _e: self.after(160, self._esconder))

        self.dropdown = None

    # ---------- API pública ----------

    def limpar(self) -> None:
        self.selecionado = None
        self.entry.delete(0, "end")
        self._esconder()

    def focar(self) -> None:
        self.entry.focus_set()

    # ---------- eventos ----------

    def _ao_digitar(self, evento) -> None:
        if evento.keysym in ("Up", "Down", "Return", "Escape"):
            return
        self.selecionado = None  # digitou de novo: a escolha anterior não vale mais
        termo = self.entry.get().strip()
        self.sugestoes = self.buscar_fn(termo)[:MAX_SUGESTOES] if termo else []
        self.indice_ativo = -1
        self._mostrar() if self.sugestoes else self._esconder()

    def _proxima(self, _evento) -> str:
        if self.sugestoes:
            self.indice_ativo = (self.indice_ativo + 1) % len(self.sugestoes)
            self._destacar()
        return "break"

    def _anterior(self, _evento) -> str:
        if self.sugestoes:
            self.indice_ativo = (self.indice_ativo - 1) % len(self.sugestoes)
            self._destacar()
        return "break"

    def _confirmar(self, _evento) -> str:
        if self.sugestoes:
            indice = self.indice_ativo if self.indice_ativo >= 0 else 0
            self._escolher(self.sugestoes[indice])
        return "break"

    def _escolher(self, produto) -> None:
        self.selecionado = produto
        self.entry.delete(0, "end")
        self.entry.insert(0, produto.produto)
        self._esconder()
        self.on_select(produto)

    # ---------- dropdown ----------

    def _mostrar(self) -> None:
        self._esconder()
        topo = self.winfo_toplevel()
        self.entry.update_idletasks()

        # o customtkinter 6 exige width/height no construtor (não aceita no place())
        largura = max(self.entry.winfo_width(), LARGURA_MINIMA)
        altura = len(self.sugestoes) * (ALTURA_LINHA + ESPACO_LINHA * 2) + 10

        self.dropdown = ctk.CTkFrame(
            topo, width=largura, height=altura, fg_color=tema.CARD,
            corner_radius=tema.RAIO, border_width=1, border_color=tema.BORDA,
        )
        self.dropdown.pack_propagate(False)

        self._linhas = []
        for indice, produto in enumerate(self.sugestoes):
            self._linhas.append(self._criar_linha(produto, indice))

        x = self.entry.winfo_rootx() - topo.winfo_rootx()
        y = self.entry.winfo_rooty() - topo.winfo_rooty() + self.entry.winfo_height() + 4
        self.dropdown.place(x=x, y=y)
        self.dropdown.lift()

    def _criar_linha(self, produto, indice: int) -> ctk.CTkFrame:
        from src.ui import formato

        linha = ctk.CTkFrame(self.dropdown, height=ALTURA_LINHA, fg_color="transparent", corner_radius=6)
        linha.pack(fill="x", padx=5, pady=ESPACO_LINHA)
        linha.pack_propagate(False)
        linha.grid_columnconfigure(0, weight=1)
        linha.grid_rowconfigure(0, weight=1)

        nome = ctk.CTkLabel(linha, text=f"#{produto.id}   {produto.produto}", font=tema.FONTE_CORPO,
                            text_color=tema.TEXTO, anchor="w")
        nome.grid(row=0, column=0, sticky="ew", padx=(12, 6))

        detalhe = ctk.CTkLabel(
            linha,
            text=f"{formato.peso(produto.peso)}  ·  {formato.moeda(produto.custo_com_desconto_e_ipi)}",
            font=tema.FONTE_PEQUENA, text_color=tema.TEXTO_SUAVE, anchor="e",
        )
        detalhe.grid(row=0, column=1, sticky="e", padx=(6, 12))

        for widget in (linha, nome, detalhe):
            widget.bind("<Button-1>", lambda _e, p=produto: self._escolher(p))
            widget.bind("<Enter>", lambda _e, i=indice: self._destacar(i))
        return linha

    def _destacar(self, indice: int | None = None) -> None:
        if indice is not None:
            self.indice_ativo = indice
        for posicao, linha in enumerate(self._linhas):
            linha.configure(fg_color=tema.ACENTO_SUAVE if posicao == self.indice_ativo else "transparent")

    def _esconder(self) -> None:
        if self.dropdown is not None:
            self.dropdown.destroy()
            self.dropdown = None
            self._linhas = []
