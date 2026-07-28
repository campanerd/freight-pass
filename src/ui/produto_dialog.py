"""Modal de cadastro/edição de produto."""

import customtkinter as ctk

from src.functions.produtos import Produtos
from src.ui import formato, tema

CAMPOS = [
    ("produto", "Produto *", "Ex: Parafuso sextavado 5mm"),
    ("descricao", "Descrição", "Detalhes complementares"),
    ("cx", "Unidades por caixa", "Ex: 24"),
    ("ncm", "NCM", "Ex: 7318.15.00"),
    ("ipi", "IPI (%)", "Ex: 5"),
    ("custo_com_desconto_e_ipi", "Custo c/ desconto e IPI", "Ex: 12,50"),
    ("peso", "Peso (kg)", "Ex: 0,05"),
    ("cubagem", "Cubagem (m³)", "Ex: 0,002"),
]


class ProdutoDialog(ctk.CTkToplevel):
    def __init__(self, master, ao_salvar, produto=None):
        super().__init__(master)
        self.ao_salvar = ao_salvar
        self.produto = produto
        self.entries: dict[str, ctk.CTkEntry] = {}

        self.title("Editar produto" if produto else "Novo produto")
        self.geometry("520x640")
        self.resizable(False, False)
        self.configure(fg_color=tema.FUNDO)
        self.transient(master)
        self.grab_set()

        self._montar()
        if produto:
            self._preencher(produto)
        self.after(120, lambda: self.entries["produto"].focus_set())

    def _montar(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        cabecalho = ctk.CTkLabel(
            self, text="Editar produto" if self.produto else "Novo produto",
            font=tema.FONTE_TITULO, text_color=tema.TEXTO, anchor="w",
        )
        cabecalho.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 4))

        corpo = ctk.CTkScrollableFrame(self, fg_color="transparent")
        corpo.grid(row=1, column=0, sticky="nsew", padx=18, pady=8)
        corpo.grid_columnconfigure(0, weight=1)

        for linha, (chave, rotulo, exemplo) in enumerate(CAMPOS):
            ctk.CTkLabel(corpo, text=rotulo, font=tema.FONTE_PEQUENA,
                         text_color=tema.TEXTO_SUAVE, anchor="w").grid(
                row=linha * 2, column=0, sticky="ew", padx=10, pady=(10, 2))
            entry = ctk.CTkEntry(corpo, placeholder_text=exemplo, height=38,
                                 font=tema.FONTE_CORPO, corner_radius=tema.RAIO,
                                 border_color=tema.BORDA, fg_color=tema.CARD)
            entry.grid(row=linha * 2 + 1, column=0, sticky="ew", padx=10)
            entry.bind("<Return>", lambda _e: self._salvar())
            self.entries[chave] = entry

        self.erro = ctk.CTkLabel(self, text="", font=tema.FONTE_PEQUENA,
                                 text_color=tema.PERIGO, anchor="w")
        self.erro.grid(row=2, column=0, sticky="ew", padx=28, pady=(4, 0))

        rodape = ctk.CTkFrame(self, fg_color="transparent")
        rodape.grid(row=3, column=0, sticky="ew", padx=28, pady=(8, 22))
        rodape.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(rodape, text="Cancelar", command=self.destroy, width=110, height=40,
                      corner_radius=tema.RAIO, font=tema.FONTE_CORPO, fg_color=tema.NEUTRO,
                      hover_color=tema.NEUTRO_HOVER, text_color=tema.TEXTO).grid(row=0, column=1, padx=(0, 10))
        ctk.CTkButton(rodape, text="Salvar", command=self._salvar, width=130, height=40,
                      corner_radius=tema.RAIO, font=tema.FONTE_SUBTITULO, fg_color=tema.ACENTO,
                      hover_color=tema.ACENTO_HOVER).grid(row=0, column=2)

    def _preencher(self, produto) -> None:
        valores = {
            "produto": produto.produto,
            "descricao": produto.descricao or "",
            "cx": produto.cx,
            "ncm": produto.ncm or "",
            "ipi": produto.ipi,
            "custo_com_desconto_e_ipi": produto.custo_com_desconto_e_ipi,
            "peso": produto.peso,
            "cubagem": produto.cubagem,
        }
        for chave, valor in valores.items():
            if valor is None:
                continue
            texto = str(valor).replace(".", ",") if isinstance(valor, float) else str(valor)
            self.entries[chave].insert(0, texto)

    def _salvar(self) -> None:
        nome = self.entries["produto"].get().strip()
        if not nome:
            return self._mostrar_erro("Informe o nome do produto.")

        numericos = {}
        for chave, rotulo in [("cx", "Unidades por caixa"), ("ipi", "IPI"),
                              ("custo_com_desconto_e_ipi", "Custo"), ("peso", "Peso"),
                              ("cubagem", "Cubagem")]:
            texto = self.entries[chave].get().strip()
            if not texto:
                numericos[chave] = 0 if chave == "cx" else 0.0
                continue
            valor = formato.ler_inteiro(texto) if chave == "cx" else formato.ler_decimal(texto)
            if valor is None:
                return self._mostrar_erro(f"{rotulo}: valor inválido ({texto}).")
            numericos[chave] = valor

        descricao = self.entries["descricao"].get().strip()
        ncm = self.entries["ncm"].get().strip()

        if self.produto:
            # Produtos.update ignora campos None ("mantém o valor atual"), então aqui
            # mandamos string vazia — senão limpar um campo no formulário não salvaria.
            Produtos.update(self.produto.id, produto=nome, descricao=descricao, ncm=ncm, **numericos)
        else:
            Produtos.create(produto=nome, descricao=descricao or None, ncm=ncm or None, **numericos)

        self.ao_salvar()
        self.destroy()

    def _mostrar_erro(self, mensagem: str) -> None:
        self.erro.configure(text=mensagem)
