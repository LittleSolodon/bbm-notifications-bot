import sqlite3
from typing import Optional, Dict, Any


def get_user(tg_id: int, db_name: str = "db/app.db") -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        "SELECT id, tg_id, access, is_admin FROM users WHERE tg_id = ?",
        (tg_id,)
    )
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    return dict(row)



def add_user(tg_id: int, db_name: str = "db/app.db") -> bool:
    try:
        with sqlite3.connect(db_name) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO users (tg_id)
                VALUES (?)
                """,
                (tg_id,)
            )
        return True
    except sqlite3.IntegrityError:
        return False
    
def get_item(item_id: int, db_name: str = "db/app.db") -> Optional[Dict[str, Any]]:
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM items WHERE item_code = ?",
            (item_id,)
        )
        row = cur.fetchone()

    return dict(row) if row else None
    
def get_users(db_name: str = "db/app.db") -> Optional[Dict[str, Any]]:
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM users"
        )
        rows = cur.fetchall()

        return [dict(row) for row in rows] if rows else []

def add_item(
    item_code: str,
    name: str,
    image_link: str,
    link_code: str,
    price: int | None = None,
    stat_type: int = 0,
    stat_num: int = 0,
    is_animated: bool = False,
    db_path: str = "db/app.db"
) -> int:
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO items (
                item_code,
                name,
                price,
                image_link,
                link_code,
                stat_type,
                stat_num,
                is_animated
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_code,
            name,
            price,
            image_link,
            link_code,
            stat_type,
            stat_num,
            int(is_animated)
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_item_by_id(item_id: int, db_path: str = "db/app.db") -> dict[str, Any] | None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_item_by_code(item_code: str, db_path: str = "db/app.db") -> dict[str, Any] | None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE item_code = ?", (item_code,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_items_by_name(name: str, db_path: str = "db/app.db") -> list[dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE name = ?", (name,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def search_items_by_name(query: str, db_path: str = "db/app.db") -> list[dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM items WHERE name LIKE ?",
            (f"%{query}%",)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_all_items(db_path: str = "db/app.db") -> list[dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def update_item(
    item_code: str,
    db_path: str = "db/app.db",
    **fields: Any
) -> bool:
    allowed_fields = {
        "name",
        "price",
        "image_link",
        "link_code",
        "stat_type",
        "stat_num",
        "is_animated",
        "buy_orders",
        "sell_orders"
    }

    update_data = {key: value for key, value in fields.items() if key in allowed_fields}

    if not update_data:
        raise ValueError("Нет допустимых полей для обновления")

    if "is_animated" in update_data:
        update_data["is_animated"] = int(bool(update_data["is_animated"]))

    set_clause = ", ".join(f"{key} = ?" for key in update_data)
    values = list(update_data.values())
    values.append(item_code)

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE items SET {set_clause} WHERE item_code = ?",
            values
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_item(item_code: str, db_path: str = "db/app.db") -> bool:
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE item_code = ?", (item_code,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
    
def update_user(
    tg_id: int,
    field_name: str,
    new_value: Any,
    db_name: str = "db/app.db"
) -> bool:
    allowed_fields = {"tg_id", "access", "is_admin"}

    if field_name not in allowed_fields:
        raise ValueError(f"Недопустимое поле users: {field_name}")

    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE users SET {field_name} = ? WHERE tg_id = ?",
            (new_value, tg_id)
        )
        conn.commit()
        return cur.rowcount > 0
    
    
def get_settings(owner_id: int, db_name: str = "db/app.db") -> Optional[Dict[str, Any]]:
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM settings WHERE owner_id = ?",
            (owner_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None
    
def update_settings(
    owner_id: int,
    field_name: str,
    new_value: Any,
    db_name: str = "db/app.db"
) -> bool:
    allowed_fields = {"notifications_enabled"}

    if field_name not in allowed_fields:
        raise ValueError(f"Недопустимое поле users: {field_name}")

    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE settings SET {field_name} = ? WHERE owner_id = ?",
            (new_value, owner_id)
        )
        conn.commit()
        return cur.rowcount > 0
    
def get_global_settings(db_name: str = "db/app.db") -> Optional[Dict[str, Any]]:
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM global_settings"
        )
        row = cur.fetchone()
        return dict(row) if row else None
    
def update_global_settings(
    field_name: str,
    new_value: Any,
    db_name: str = "db/app.db"
) -> bool:
    allowed_fields = {"polling"}

    if field_name not in allowed_fields:
        raise ValueError(f"Недопустимое поле: {field_name}")

    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE global_settings SET {field_name} = ?",
            (new_value,)
        )
        conn.commit()
        return cur.rowcount > 0


def add_favourite(
    owner_id: int,
    item_id: int,
    db_name: str = "db/app.db"
) -> int:
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO favourites (owner_id, item_id)
            VALUES (?, ?)
            """,
            (owner_id, item_id)
        )
        conn.commit()
        return cur.lastrowid


def get_favourites_by_item_id(
    item_id: int,
    db_name: str = "db/app.db"
) -> list[dict[str, Any]]:
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM favourites WHERE item_id = ?",
            (item_id,)
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]


def get_favourite(
    owner_id: int,
    item_id: int,
    db_name: str = "db/app.db"
) -> dict[str, Any] | None:
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM favourites
            WHERE owner_id = ? AND item_id = ?
            """,
            (owner_id, item_id)
        )
        row = cur.fetchone()
        return dict(row) if row else None


def get_user_favourites(
    owner_id: int,
    db_name: str = "db/app.db"
) -> list[dict[str, Any]]:
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM favourites
            WHERE owner_id = ?
            ORDER BY id DESC
            """,
            (owner_id,)
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]


def get_user_favourite_item_ids(
    owner_id: int,
    db_name: str = "db/app.db"
) -> list[int]:
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT item_id FROM favourites
            WHERE owner_id = ?
            ORDER BY id DESC
            """,
            (owner_id,)
        )
        rows = cur.fetchall()
        return [row[0] for row in rows]


def delete_favourite(
    owner_id: int,
    item_id: int,
    db_name: str = "db/app.db"
) -> bool:
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            DELETE FROM favourites
            WHERE owner_id = ? AND item_id = ?
            """,
            (owner_id, item_id)
        )
        conn.commit()
        return cur.rowcount > 0


def delete_favourite_by_id(
    favourite_id: int,
    db_name: str = "db/app.db"
) -> bool:
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM favourites WHERE id = ?",
            (favourite_id,)
        )
        conn.commit()
        return cur.rowcount > 0
    

def get_all_unique_favourite_item_ids(db_name: str = "db/app.db") -> list[int]:
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT item_id
            FROM favourites
            ORDER BY item_id
        """)
        rows = cur.fetchall()
        return [row[0] for row in rows]

def get_all_unique_favourite_owner_ids(item_id, db_name: str = "db/app.db") -> list[int]:
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT owner_id
            FROM favourites WHERE item_id = ?
            ORDER BY owner_id
        """, (item_id,))
        rows = cur.fetchall()
        return [row[0] for row in rows]


def print_table(table_name = "users"):
    """
    Выводит содержимое таблицы SQLite в консоль
    
    Args:
        db_path (str): путь к файлу базы данных
        table_name (str): имя таблицы
    """
    conn = sqlite3.connect("db/app.db")
    cursor = conn.cursor()
    
    try:
        # Получаем данные из таблицы
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Получаем названия колонок
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Выводим заголовки
        print(f"Таблица: {table_name}")
        print("-" * 50)
        print(" | ".join(columns))
        print("-" * 50)
        
        # Выводим данные
        for row in rows:
            print(" | ".join(str(value) for value in row))
        
        print(f"\nВсего записей: {len(rows)}")
        
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    print_table("items")