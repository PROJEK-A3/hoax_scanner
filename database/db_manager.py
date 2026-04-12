import sqlite3  # Mengimpor library SQLite untuk mengelola database
from datetime import datetime  # Mengimpor datetime untuk mengambil waktu saat ini

# Menyimpan nama dan lokasi database dalam variabel
# agar tidak perlu menuliskan path database berulang kali
DB_NAME = "database/hoaxscan.db"

class DatabaseManager:
    def __init__(self) -> None:
        """
        Menginisialisasi DatabaseManager dan memastikan tabel database yang diperlukan
        ('riwayat_analisis') telah dibuat jika belum ada.
        """
        self.create_table() # Memastikan tabel dibuat saat objek diinisialisasi

    def connect(self):
        """ 
        Fungsi untuk membuat koneksi ke database SQLite.
        Akan dipanggil setiap kali ingin melakukan operasi database.
        """
        return sqlite3.connect(DB_NAME)  # Menghubungkan ke file database

    # CREATE TABLE
    def create_table(self):
        """
        Fungsi untuk membuat tabel 'riwayat_analisis' jika belum ada.
        Tabel ini digunakan untuk menyimpan hasil analisis artikel.
        """
        conn = self.connect()          # Membuka koneksi ke database
        cursor = conn.cursor()    # Membuat cursor untuk menjalankan perintah SQL

        # Perintah SQL untuk membuat tabel
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS riwayat_analisis (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            input_text TEXT,                      
            skor INTEGER,                         
            kategori TEXT,                       
            tanggal DATETIME                    
        )
        """)

        conn.commit()  # Menyimpan perubahan ke database
        conn.close()   # Menutup koneksi database

    # ➕ CREATE (INSERT DATA)
    def insert_analisis(self, input_text, skor, kategori):
        """
        Fungsi untuk MENYIMPAN hasil analisis ke database.
        Ini merupakan bagian CREATE dalam konsep CRUD.
        """
        conn = self.connect()          # Membuka koneksi database
        cursor = conn.cursor()    # Membuat cursor

        # Perintah SQL untuk memasukkan data baru ke tabel
        cursor.execute("""
        INSERT INTO riwayat_analisis (input_text, skor, kategori, tanggal)
        VALUES (?, ?, ?, ?)
        """, (
            input_text,           # Data teks dari user
            skor,                 # Skor hasil analisis
            kategori,             # Kategori hasil analisis
            datetime.now()        # Waktu saat data disimpan
        ))

        conn.commit()  # Menyimpan perubahan
        conn.close()   # Menutup koneksi


    # READ (AMBIL SEMUA DATA)
    def get_all_analisis(self):
        """
        Fungsi untuk MENGAMBIL semua data dari tabel.
        Ini merupakan bagian READ dalam CRUD.
        """
        conn = self.connect()          # Membuka koneksi database
        cursor = conn.cursor()    # Membuat cursor

        # Perintah SQL untuk mengambil semua data
        cursor.execute("SELECT * FROM riwayat_analisis")
        data = cursor.fetchall()  # Mengambil semua hasil query dalam bentuk list

        conn.close()              # Menutup koneksi
        return data               # Mengembalikan data ke program utama


    # READ (AMBIL BERDASARKAN ID)
    def get_analisis_by_id(self, id):
        """
        Fungsi untuk mengambil satu data berdasarkan ID tertentu.
        Digunakan untuk melihat detail hasil analisis.
        """
        conn = self.connect()          # Membuka koneksi database
        cursor = conn.cursor()    # Membuat cursor

        # Perintah SQL untuk mengambil data berdasarkan ID
        cursor.execute("SELECT * FROM riwayat_analisis WHERE id = ?", (id,))
        data = cursor.fetchone()  # Mengambil satu data saja

        conn.close()              # Menutup koneksi
        return data               # Mengembalikan hasil


    # ✏️ UPDATE (UBAH DATA)
    def update_analisis(self, id, skor, kategori):
        """
        Fungsi untuk MENGUBAH data analisis berdasarkan ID.
        Ini merupakan bagian UPDATE dalam CRUD.
        """
        conn = self.connect()          # Membuka koneksi database
        cursor = conn.cursor()    # Membuat cursor

        cursor.execute("""
        UPDATE riwayat_analisis
        SET skor = ?, kategori = ?
        WHERE id = ?
        """, (
            skor,                 # Skor baru
            kategori,             # Kategori baru
            id                    # ID data yang ingin diubah
        ))

        conn.commit()  # Menyimpan perubahan
        conn.close()   # Menutup koneksi


    # DELETE (HAPUS DATA)
    def delete_analisis(self, id):
        """
        Fungsi untuk MENGHAPUS data berdasarkan ID.
        Ini merupakan bagian DELETE dalam CRUD.
        """
        conn = self.connect()          # Membuka koneksi database
        cursor = conn.cursor()    # Membuat cursor

        # Perintah SQL untuk menghapus data berdasarkan ID
        cursor.execute("DELETE FROM riwayat_analisis WHERE id = ?", (id,))

        conn.commit()  # Menyimpan perubahan
        conn.close()   # Menutup koneksi