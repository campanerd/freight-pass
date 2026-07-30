"""Carrega variáveis de ambiente (.env) — dados que não devem ir pro git."""

import sys
from pathlib import Path

from dotenv import load_dotenv


def carregar_env() -> None:
    # Quando empacotado (PyInstaller), os arquivos ficam extraídos em sys._MEIPASS,
    # não na pasta de onde o .exe foi executado — por isso o .env precisa ser
    # embutido no build (ver FreightPass.spec) e localizado por aqui.
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parents[3]  # infra -> core -> src -> raiz do projeto
    load_dotenv(base / ".env")
