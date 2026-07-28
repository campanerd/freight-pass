"""Paleta e tipografia da aplicação.

As cores são tuplas (modo claro, modo escuro) — o customtkinter troca sozinho
conforme o tema ativo.
"""

FUNDO = ("#F2F4F7", "#15171C")
SIDEBAR = ("#FFFFFF", "#1A1D24")
CARD = ("#FFFFFF", "#1F232B")
CARD_ELEVADO = ("#F7F8FA", "#262B35")
BORDA = ("#E3E6EB", "#2E3440")

TEXTO = ("#1A1D24", "#E8EAED")
TEXTO_SUAVE = ("#6B7280", "#9AA4B2")

ACENTO = ("#2563EB", "#3B82F6")
ACENTO_HOVER = ("#1D4ED8", "#2563EB")
ACENTO_SUAVE = ("#EFF4FF", "#1E2A44")

SUCESSO = ("#15803D", "#22C55E")
PERIGO = ("#DC2626", "#EF4444")
PERIGO_HOVER = ("#B91C1C", "#DC2626")

NEUTRO = ("#EDEFF3", "#2A2F3A")
NEUTRO_HOVER = ("#E1E4EA", "#343A47")

# Tipografia — tuplas simples (não CTkFont) para poder usar antes da janela existir.
# Para deixar tudo maior/menor de uma vez, ajuste estes números junto com as
# alturas abaixo (senão o texto maior fica cortado dentro dos campos).
FONTE_TITULO = ("Segoe UI Semibold", 28)
FONTE_SUBTITULO = ("Segoe UI Semibold", 19)
FONTE_CORPO = ("Segoe UI", 16)
FONTE_PEQUENA = ("Segoe UI", 14)
FONTE_METRICA = ("Segoe UI Semibold", 32)
FONTE_LOGO = ("Segoe UI Semibold", 25)

# Dimensões que acompanham a tipografia
ALTURA_CAMPO = 46
ALTURA_BOTAO = 46
ALTURA_BOTAO_PEQUENO = 40
ALTURA_LINHA_TABELA = 42

RAIO = 10


def cor(tupla: tuple[str, str]) -> str:
    """Resolve uma tupla (claro, escuro) para a cor do tema ativo.

    Necessário para widgets ttk (a tabela), que não entendem tuplas como o customtkinter.
    """
    import customtkinter as ctk

    return tupla[0] if ctk.get_appearance_mode() == "Light" else tupla[1]
