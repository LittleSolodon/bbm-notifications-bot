import sqlite3

def create_tables(db_name: str = "db/app.db") -> None:
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER NOT NULL UNIQUE,
                access INTEGER NOT NULL DEFAULT 0 CHECK (access IN (0, 1)),
                is_admin INTEGER NOT NULL DEFAULT 0 CHECK (is_admin IN (0, 1))
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS global_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                polling INTEGER NOT NULL DEFAULT 0 CHECK (polling IN (0, 1))
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS favourites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                UNIQUE(owner_id, item_id),
                FOREIGN KEY (owner_id) REFERENCES users(id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                FOREIGN KEY (item_id) REFERENCES items(id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                price INTEGER,
                image_link TEXT NOT NULL,
                link_code TEXT NOT NULL,
                stat_type INTEGER DEFAULT 0,
                stat_num INTEGER DEFAULT 0,
                is_animated INTEGER NOT NULL DEFAULT 0 CHECK (is_animated IN (0, 1)),
                buy_orders INTEGER DEFAULT 0,
                sell_orders INTEGER DEFAULT 0
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL UNIQUE,
                notifications_enabled INTEGER NOT NULL DEFAULT 0 CHECK (notifications_enabled IN (0, 1)),
                price_min INTEGER NOT NULL DEFAULT 0,
                price_max INTEGER NOT NULL DEFAULT 0,
                body_head INTEGER NOT NULL DEFAULT 0 CHECK (notifications_enabled IN (0, 1)),
                body_face INTEGER NOT NULL DEFAULT 0 CHECK (notifications_enabled IN (0, 1)),
                body_shirt INTEGER NOT NULL DEFAULT 0 CHECK (notifications_enabled IN (0, 1)),
                body_boots INTEGER NOT NULL DEFAULT 0 CHECK (notifications_enabled IN (0, 1)),
                body_lhand INTEGER NOT NULL DEFAULT 0 CHECK (notifications_enabled IN (0, 1)),
                body_rhand INTEGER NOT NULL DEFAULT 0 CHECK (notifications_enabled IN (0, 1)),
                att_min INTEGER NOT NULL DEFAULT 0,
                att_max INTEGER NOT NULL DEFAULT 0,
                def_min INTEGER NOT NULL DEFAULT 0,
                def_max INTEGER NOT NULL DEFAULT 0,
                is_animated INTEGER NOT NULL DEFAULT 0 CHECK (notifications_enabled IN (0, 1)),
                multi INTEGER NOT NULL DEFAULT 0 CHECK (notifications_enabled IN (0, 1)),
                fav_only INTEGER NOT NULL DEFAULT 0 CHECK (notifications_enabled IN (0, 1)),
                buy_order_percent INTEGER NOT NULL DEFAULT 0,
                
                FOREIGN KEY (owner_id) REFERENCES users(tg_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        """)

        cur.execute("""
            CREATE TRIGGER IF NOT EXISTS create_profile_after_user_insert
            AFTER INSERT ON users
            FOR EACH ROW
            BEGIN
                INSERT INTO settings (owner_id)
                VALUES (NEW.tg_id);
            END;
                    """)

        conn.commit()


def select():
    with sqlite3.connect("db/app.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM settings")
        rows = cur.fetchall()
        return rows

if __name__ == "__main__":
    create_tables()
    # print(select())
    print("asaa")