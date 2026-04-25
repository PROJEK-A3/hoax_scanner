import sqlite3
from datetime import datetime
from database.logger import setup_logger, get_logger

# Setup logger
setup_logger()
logger = get_logger()

# Database path
DB_NAME = "database/hoaxscan.db"


class DatabaseManager:
    def __init__(self) -> None:
        """
        Menginisialisasi DatabaseManager dan memastikan tabel database yang diperlukan
        ('riwayat_analisis') telah dibuat jika belum ada.
        """
        logger.info("DB MANAGER INIT")
        create_table()  


# CONNECT
def connect_db():
    try:
        logger.info("CONNECT DB START")
        conn = sqlite3.connect(DB_NAME)
        logger.info("CONNECT DB SUCCESS")
        return conn
    except Exception as e:
        logger.error(f"CONNECT DB ERROR | {repr(e)}")
        raise


# CREATE TABLE
def create_table():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS riwayat_analisis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_text TEXT,
            skor INTEGER,
            kategori TEXT,
            tanggal DATETIME
        )
        """)

        conn.commit()
        conn.close()

        logger.info("CREATE TABLE SUCCESS | riwayat_analisis")

    except Exception as e:
        logger.error(f"CREATE TABLE ERROR | {repr(e)}")


# INSERT
def insert_analisis(input_text: str, skor: int, kategori: str):
    try:
        logger.info(f"INSERT START | text='{input_text}'")

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO riwayat_analisis (input_text, skor, kategori, tanggal)
        VALUES (?, ?, ?, ?)
        """, (input_text, skor, kategori, datetime.now()))

        conn.commit()
        conn.close()

        logger.info(f"INSERT SUCCESS | skor={skor} | kategori={kategori}")

    except Exception as e:
        logger.error(f"INSERT ERROR | {repr(e)}")


# GET ALL
def get_all_analisis():
    try:
        logger.info("GET ALL START")

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM riwayat_analisis")
        data = cursor.fetchall()

        conn.close()

        logger.info(f"GET ALL SUCCESS | total={len(data)}")

        return data

    except Exception as e:
        logger.error(f"GET ALL ERROR | {repr(e)}")
        return []


# GET BY ID
def get_analisis_by_id(id: int):
    try:
        logger.info(f"GET BY ID START | id={id}")

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM riwayat_analisis WHERE id = ?", (id,))
        data = cursor.fetchone()

        conn.close()

        logger.info(f"GET BY ID SUCCESS | found={data is not None}")

        return data

    except Exception as e:
        logger.error(f"GET BY ID ERROR | {repr(e)}")
        return None


# UPDATE
def update_analisis(id: int, skor: int, kategori: str):
    try:
        logger.info(f"UPDATE START | id={id}")

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE riwayat_analisis
        SET skor = ?, kategori = ?
        WHERE id = ?
        """, (skor, kategori, id))

        conn.commit()
        conn.close()

        logger.info(f"UPDATE SUCCESS | skor={skor} | kategori={kategori}")

    except Exception as e:
        logger.error(f"UPDATE ERROR | {repr(e)}")


# DELETE
def delete_analisis(id: int):
    try:
        logger.warning(f"DELETE START | id={id}")

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM riwayat_analisis WHERE id = ?", (id,))

        conn.commit()
        conn.close()

        logger.warning(f"DELETE SUCCESS | id={id}")

    except Exception as e:
        logger.error(f"DELETE ERROR | {repr(e)}")


# DELETE ALL
def delete_all_analisis():
    try:
        logger.warning("DELETE ALL START")

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM riwayat_analisis")

        conn.commit()
        conn.close()

        logger.warning("DELETE ALL SUCCESS")

    except Exception as e:
        logger.error(f"DELETE ALL ERROR | {repr(e)}")