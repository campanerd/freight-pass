"""Janela principal do FreightPass."""

import customtkinter as ctk

from src.ui import tema
from src.ui.produtos_page import ProdutosPage
from src.ui.repasses_page import RepassesPage
from src.ui.widgets import tabela as widget_tabela

PAGINAS = [
    ("repasses", "Repasses", RepassesPage),
    ("produtos", "Produtos", ProdutosPage),
]


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")

        self.title("FreightPass")
        self.geometry("1460x880")
        self.minsize(1180, 720)
        self.configure(fg_color=tema.FUNDO)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.paginas: dict[str, ctk.CTkFrame] = {}
        self.botoes: dict[str, ctk.CTkButton] = {}
        self.pagina_ativa = None

        self._montar_sidebar()
        self._montar_conteudo()
        self.mostrar("repasses")

    def _montar_sidebar(self) -> None:
        barra = ctk.CTkFrame(self, fg_color=tema.SIDEBAR, corner_radius=0, width=280)
        barra.grid(row=0, column=0, sticky="nsw")
        barra.grid_propagate(False)
        barra.grid_rowconfigure(2, weight=1)
        barra.grid_columnconfigure(0, weight=1)

        marca = ctk.CTkFrame(barra, fg_color="transparent")
        marca.grid(row=0, column=0, sticky="ew", padx=22, pady=(28, 6))
        ctk.CTkLabel(marca, text="FreightPass", font=tema.FONTE_LOGO,
                     text_color=tema.TEXTO, anchor="w").pack(anchor="w")
        ctk.CTkLabel(marca, text="Repasse para transportadora", font=tema.FONTE_PEQUENA,
                     text_color=tema.TEXTO_SUAVE, anchor="w").pack(anchor="w")

        navegacao = ctk.CTkFrame(barra, fg_color="transparent")
        navegacao.grid(row=1, column=0, sticky="ew", padx=14, pady=(24, 0))
        navegacao.grid_columnconfigure(0, weight=1)

        for linha, (chave, rotulo, _classe) in enumerate(PAGINAS):
            botao = ctk.CTkButton(
                navegacao, text=rotulo, command=lambda c=chave: self.mostrar(c),
                height=52, corner_radius=tema.RAIO, font=tema.FONTE_SUBTITULO, anchor="w",
                fg_color="transparent", hover_color=tema.NEUTRO_HOVER, text_color=tema.TEXTO_SUAVE,
            )
            botao.grid(row=linha, column=0, sticky="ew", pady=3)
            self.botoes[chave] = botao

        self.switch_tema = ctk.CTkSwitch(barra, text="Tema escuro", command=self._alternar_tema,
                                         font=tema.FONTE_PEQUENA, text_color=tema.TEXTO_SUAVE,
                                         progress_color=tema.ACENTO)
        self.switch_tema.select()
        self.switch_tema.grid(row=3, column=0, sticky="w", padx=24, pady=24)

    def _montar_conteudo(self) -> None:
        self.conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self.conteudo.grid(row=0, column=1, sticky="nsew", padx=28, pady=26)
        self.conteudo.grid_columnconfigure(0, weight=1)
        self.conteudo.grid_rowconfigure(0, weight=1)

    def mostrar(self, chave: str) -> None:
        if chave not in self.paginas:
            classe = next(c for k, _r, c in PAGINAS if k == chave)
            pagina = classe(self.conteudo)
            self.paginas[chave] = pagina

        for outra in self.paginas.values():
            outra.grid_forget()
        self.paginas[chave].grid(row=0, column=0, sticky="nsew")

        for outra_chave, botao in self.botoes.items():
            ativo = outra_chave == chave
            botao.configure(
                fg_color=tema.ACENTO_SUAVE if ativo else "transparent",
                text_color=tema.ACENTO if ativo else tema.TEXTO_SUAVE,
            )

        self.pagina_ativa = chave
        if hasattr(self.paginas[chave], "recarregar"):
            self.paginas[chave].recarregar()

    def _alternar_tema(self) -> None:
        ctk.set_appearance_mode("dark" if self.switch_tema.get() else "light")
        widget_tabela.aplicar_estilo()  # a tabela é ttk: não acompanha o tema sozinha
