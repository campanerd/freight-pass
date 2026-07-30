"""Formatação e leitura de números no padrão brasileiro."""


def moeda(valor: float | None) -> str:
    if valor is None:
        return "—"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def decimal(valor: float | None, casas: int = 3) -> str:
    if valor is None:
        return "—"
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def peso(valor: float | None) -> str:
    return f"{decimal(valor, 3)} kg" if valor is not None else "—"


def cubagem(valor: float | None) -> str:
    return f"{decimal(valor, 4)} m³" if valor is not None else "—"


def percentual(valor: float | None) -> str:
    return f"{decimal(valor, 2)}%" if valor is not None else "—"


def numero_sem_zeros(valor: float | None, casas_max: int = 2) -> str:
    """Ex: 275.0 -> '275', 275.5 -> '275,5' — usado no texto pra transportadora."""
    if valor is None:
        return "—"
    texto = f"{valor:.{casas_max}f}".rstrip("0").rstrip(".")
    return (texto or "0").replace(".", ",")


def ler_decimal(texto: str) -> float | None:
    """Converte texto digitado ('12,50' ou '12.50') em float. None se inválido/vazio."""
    texto = (texto or "").strip().replace(".", "").replace(",", ".") if "," in (texto or "") else (texto or "").strip()
    if not texto:
        return None
    try:
        return float(texto)
    except ValueError:
        return None


def ler_inteiro(texto: str) -> int | None:
    texto = (texto or "").strip()
    if not texto:
        return None
    try:
        return int(texto)
    except ValueError:
        return None
