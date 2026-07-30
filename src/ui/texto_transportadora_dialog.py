"""Modal pra gerar o texto de repasse pra transportadora (destino/CNPJ/CEP digitados na hora, não salvos)."""

import customtkinter as ctk

from src.functions.repasse import Repasse
from src.ui import tema

CAMPOS = [
    ("destino", "Destino", "Nome da empresa destinatária"),
    ("cnpj", "CNPJ do destino", "Ex: 00.000.000/0001-00"),
    ("cep", "CEP do destino", "Ex: 00000-000"),
]


class TextoTransportadoraDialog(ctk.CTkToplevel):
    def __init__(self, master, repasse_id: int):
        super().__init__(master)
        self.repasse_id = repasse_id
        self.entries: dict[str, ctk.CTkEntry] = {}

        self.title("Gerar texto para transportadora")
        self.geometry("480x520")
        self.resizable(False, False)
        self.configure(fg_color=tema.FUNDO)
        self.transient(master)
        self.grab_set()

        self._montar()
        self.after(120, lambda: self.entries["destino"].focus_set())

    def _montar(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Gerar texto para transportadora", font=tema.FONTE_TITULO,
                     text_color=tema.TEXTO, anchor="w").grid(
            row=0, column=0, sticky="ew", padx=28, pady=(24, 4))
        ctk.CTkLabel(self, text="Peso, cubagem, volumes e valor vêm direto do repasse.",
                     font=tema.FONTE_PEQUENA, text_color=tema.TEXTO_SUAVE, anchor="w").grid(
            row=1, column=0, sticky="ew", padx=28, pady=(0, 16))

        corpo = ctk.CTkFrame(self, fg_color="transparent")
        corpo.grid(row=2, column=0, sticky="ew", padx=28)
        corpo.grid_columnconfigure(0, weight=1)

        for linha, (chave, rotulo, exemplo) in enumerate(CAMPOS):
            ctk.CTkLabel(corpo, text=rotulo, font=tema.FONTE_PEQUENA,
                         text_color=tema.TEXTO_SUAVE, anchor="w").grid(
                row=linha * 2, column=0, sticky="ew", pady=(10, 2))
            entry = ctk.CTkEntry(corpo, placeholder_text=exemplo, height=tema.ALTURA_CAMPO,
                                 font=tema.FONTE_CORPO, corner_radius=tema.RAIO,
                                 border_color=tema.BORDA, fg_color=tema.CARD)
            entry.grid(row=linha * 2 + 1, column=0, sticky="ew")
            entry.bind("<Return>", lambda _e: self._gerar())
            self.entries[chave] = entry

        self.status = ctk.CTkLabel(self, text="", font=tema.FONTE_PEQUENA,
                                   text_color=tema.SUCESSO, anchor="w")
        self.status.grid(row=3, column=0, sticky="ew", padx=28, pady=(14, 0))

        rodape = ctk.CTkFrame(self, fg_color="transparent")
        rodape.grid(row=4, column=0, sticky="ew", padx=28, pady=(8, 24))
        rodape.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(rodape, text="Fechar", command=self.destroy, width=130,
                      height=tema.ALTURA_BOTAO, corner_radius=tema.RAIO, font=tema.FONTE_CORPO,
                      fg_color=tema.NEUTRO, hover_color=tema.NEUTRO_HOVER,
                      text_color=tema.TEXTO).grid(row=0, column=1, padx=(0, 10))
        ctk.CTkButton(rodape, text="Gerar e copiar", command=self._gerar, width=170,
                      height=tema.ALTURA_BOTAO, corner_radius=tema.RAIO, font=tema.FONTE_SUBTITULO,
                      fg_color=tema.ACENTO, hover_color=tema.ACENTO_HOVER).grid(row=0, column=2)

    def _gerar(self) -> None:
        destino = self.entries["destino"].get().strip()
        cnpj = self.entries["cnpj"].get().strip()
        cep = self.entries["cep"].get().strip()
        if not destino or not cnpj or not cep:
            self.status.configure(text="Preencha destino, CNPJ e CEP.", text_color=tema.PERIGO)
            return

        texto = Repasse.montar_texto_transportadora(self.repasse_id, destino, cnpj, cep)
        self.clipboard_clear()
        self.clipboard_append(texto)
        self.status.configure(text="Copiado para a área de transferência!", text_color=tema.SUCESSO)
