import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path


def _pasta_dados() -> Path:
    # %LOCALAPPDATA% no Windows — estável independente de onde o app rode a partir
    # (importante pro executável empacotado, que extrai os arquivos numa pasta temporária
    # diferente a cada execução; se o banco morasse lá, os dados sumiriam a cada abertura)
    base = os.getenv("LOCALAPPDATA") or str(Path.home())
    pasta = Path(base) / "FreightPass"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


DB_PATH = _pasta_dados() / "freight_pass.db"


@dataclass
class Produto:
    id: int | None
    codigo: str
    produto: str
    descricao: str | None
    cx: int
    ncm: str
    ipi: float
    custo_com_desconto_e_ipi: float
    peso: float
    cubagem: float


@dataclass
class Repasse:
    id: int | None
    data_criacao: str | None
    peso_total: float
    cubagem_total: float
    valor_total: float


@dataclass
class RepasseItem:
    id: int | None
    repasse_id: int
    produto_id: int
    quantidade: int


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    # `with conn:` só cuida do commit/rollback da transação, não fecha a conexão
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT NOT NULL UNIQUE,
                produto TEXT NOT NULL,
                descricao TEXT,
                cx INTEGER,
                ncm TEXT,
                ipi REAL,
                custo_com_desconto_e_ipi REAL,
                peso REAL,
                cubagem REAL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS repasses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
                peso_total REAL NOT NULL DEFAULT 0,
                cubagem_total REAL NOT NULL DEFAULT 0,
                valor_total REAL NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS repasse_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repasse_id INTEGER NOT NULL REFERENCES repasses(id) ON DELETE CASCADE,
                produto_id INTEGER NOT NULL REFERENCES produtos(id),
                quantidade INTEGER NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()
