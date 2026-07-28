from src.core.infra.database import Produto, get_connection


class Produtos:
    @staticmethod
    def create(codigo: str, produto: str, descricao: str | None, cx: int, ncm: str,
               ipi: float, custo_com_desconto_e_ipi: float, peso: float, cubagem: float) -> Produto:
        conn = get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO produtos (codigo, produto, descricao, cx, ncm, ipi, custo_com_desconto_e_ipi, peso, cubagem)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (codigo, produto, descricao, cx, ncm, ipi, custo_com_desconto_e_ipi, peso, cubagem),
            )
            conn.commit()
            return Produto(cursor.lastrowid, codigo, produto, descricao, cx, ncm, ipi,
                           custo_com_desconto_e_ipi, peso, cubagem)
        finally:
            conn.close()

    @staticmethod
    def read(produto_id: int) -> Produto | None:
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
            return Produtos._row_to_produto(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def buscar(termo: str = "") -> list[Produto]:
        # busca pelo nome, pelo código do cliente ou pelo id; termo vazio retorna todos
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT * FROM produtos
                WHERE produto LIKE ? OR codigo LIKE ? OR CAST(id AS TEXT) LIKE ?
                ORDER BY produto
                """,
                (f"%{termo}%", f"%{termo}%", f"{termo}%"),
            ).fetchall()
            return [Produtos._row_to_produto(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def update(produto_id: int, codigo: str | None = None, produto: str | None = None,
               descricao: str | None = None, cx: int | None = None, ncm: str | None = None,
               ipi: float | None = None, custo_com_desconto_e_ipi: float | None = None,
               peso: float | None = None, cubagem: float | None = None) -> None:
        # só altera os campos enviados (None mantém o valor atual)
        campos = {
            "codigo": codigo,
            "produto": produto,
            "descricao": descricao,
            "cx": cx,
            "ncm": ncm,
            "ipi": ipi,
            "custo_com_desconto_e_ipi": custo_com_desconto_e_ipi,
            "peso": peso,
            "cubagem": cubagem,
        }
        campos = {coluna: valor for coluna, valor in campos.items() if valor is not None}
        if not campos:
            return

        set_clause = ", ".join(f"{coluna} = ?" for coluna in campos)
        conn = get_connection()
        try:
            conn.execute(f"UPDATE produtos SET {set_clause} WHERE id = ?", (*campos.values(), produto_id))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def delete(produto_id: int) -> None:
        conn = get_connection()
        try:
            conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _row_to_produto(row) -> Produto:
        return Produto(
            id=row["id"],
            codigo=row["codigo"],
            produto=row["produto"],
            descricao=row["descricao"],
            cx=row["cx"],
            ncm=row["ncm"],
            ipi=row["ipi"],
            custo_com_desconto_e_ipi=row["custo_com_desconto_e_ipi"],
            peso=row["peso"],
            cubagem=row["cubagem"],
        )
