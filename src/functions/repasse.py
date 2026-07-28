from src.core.infra.database import Repasse as RepasseModel, RepasseItem, get_connection


class Repasse:
    @staticmethod
    def create() -> RepasseModel:
        conn = get_connection()
        try:
            cursor = conn.execute("INSERT INTO repasses DEFAULT VALUES")
            conn.commit()
            novo_id = cursor.lastrowid
        finally:
            conn.close()
        return Repasse.read(novo_id)

    @staticmethod
    def read(repasse_id: int) -> RepasseModel | None:
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM repasses WHERE id = ?", (repasse_id,)).fetchone()
            return Repasse._row_to_repasse(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def adicionar_item(repasse_id: int, produto_id: int, quantidade: int) -> RepasseItem:
        conn = get_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO repasse_itens (repasse_id, produto_id, quantidade) VALUES (?, ?, ?)",
                (repasse_id, produto_id, quantidade),
            )
            conn.commit()
            item_id = cursor.lastrowid
        finally:
            conn.close()
        Repasse._recalcular_totais(repasse_id)
        return RepasseItem(item_id, repasse_id, produto_id, quantidade)

    @staticmethod
    def remover_item(item_id: int) -> None:
        conn = get_connection()
        try:
            row = conn.execute("SELECT repasse_id FROM repasse_itens WHERE id = ?", (item_id,)).fetchone()
            if row is None:
                return
            repasse_id = row["repasse_id"]
            conn.execute("DELETE FROM repasse_itens WHERE id = ?", (item_id,))
            conn.commit()
        finally:
            conn.close()
        Repasse._recalcular_totais(repasse_id)

    @staticmethod
    def listar_itens(repasse_id: int) -> list[RepasseItem]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM repasse_itens WHERE repasse_id = ?", (repasse_id,)
            ).fetchall()
            return [
                RepasseItem(row["id"], row["repasse_id"], row["produto_id"], row["quantidade"])
                for row in rows
            ]
        finally:
            conn.close()

    @staticmethod
    def delete(repasse_id: int) -> None:
        # ON DELETE CASCADE em repasse_itens.repasse_id já apaga os itens junto
        conn = get_connection()
        try:
            conn.execute("DELETE FROM repasses WHERE id = ?", (repasse_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _recalcular_totais(repasse_id: int) -> None:
        conn = get_connection()
        try:
            totais = conn.execute(
                """
                SELECT COALESCE(SUM(ri.quantidade * p.peso), 0) AS peso_total,
                       COALESCE(SUM(ri.quantidade * p.cubagem), 0) AS cubagem_total,
                       COALESCE(SUM(ri.quantidade * p.custo_com_desconto_e_ipi), 0) AS valor_total
                FROM repasse_itens ri
                JOIN produtos p ON p.id = ri.produto_id
                WHERE ri.repasse_id = ?
                """,
                (repasse_id,),
            ).fetchone()
            conn.execute(
                "UPDATE repasses SET peso_total = ?, cubagem_total = ?, valor_total = ? WHERE id = ?",
                (totais["peso_total"], totais["cubagem_total"], totais["valor_total"], repasse_id),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _row_to_repasse(row) -> RepasseModel:
        return RepasseModel(
            id=row["id"],
            data_criacao=row["data_criacao"],
            peso_total=row["peso_total"],
            cubagem_total=row["cubagem_total"],
            valor_total=row["valor_total"],
        )
