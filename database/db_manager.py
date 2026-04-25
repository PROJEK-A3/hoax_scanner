import sqlite3
from datetime import datetime
from logger import setup_logger, get_logger

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
        self.create_table() # Memastikan tabel dibuat saat objek diinisialisasi

# CONNECT
def connect_db():
    return sqlite3.connect(DB_NAME)


# CREATE TABLE
def create_table():
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

    
    logger.info("CREATE TABLE riwayat_analisis")


# INSERT
def insert_analisis(input_text: str, skor: int, kategori: str):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO riwayat_analisis (input_text, skor, kategori, tanggal)
    VALUES (?, ?, ?, ?)
    """, (input_text, skor, kategori, datetime.now()))

    conn.commit()
    conn.close()

    logger.info(f"INSERT | text='{input_text}' | skor={skor} | kategori={kategori}")


# GET ALL
def get_all_analisis():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM riwayat_analisis")
    data = cursor.fetchall()

    conn.close()

    logger.info("GET ALL DATA")

    return data


# GET BY ID
def get_analisis_by_id(id: int):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM riwayat_analisis WHERE id = ?", (id,))
    data = cursor.fetchone()

    conn.close()

    logger.info(f"GET BY ID | id={id}")

    return data


# UPDATE
def update_analisis(id: int, skor: int, kategori: str):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE riwayat_analisis
    SET skor = ?, kategori = ?
    WHERE id = ?
    """, (skor, kategori, id))

    conn.commit()
    conn.close()

    logger.info(f"UPDATE | id={id} | skor={skor} | kategori={kategori}")


# DELETE
def delete_analisis(id: int):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM riwayat_analisis WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    logger.warning(f"DELETE | id={id}")


# DELETE ALL
def delete_all_analisis():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM riwayat_analisis")

    conn.commit()
    conn.close()

    logger.warning("DELETE ALL DATA")
