import logging  # Mengimpor library bawaan Python untuk logging


# Custom Formatter
# Digunakan untuk mengubah level log (INFO, WARNING, dll)
# menjadi huruf kecil seperti [info], [warning]
class LowercaseLevelFormatter(logging.Formatter):
    def format(self, record):
        record.levelname = record.levelname.lower()  # Ubah level jadi lowercase
        return super().format(record)  # Lanjutkan proses format seperti biasa


# Setup Logger
# Fungsi ini digunakan untuk mengatur konfigurasi logging
def setup_logger():
    
    # Membuat handler untuk menyimpan log ke file "app.log"
    handler = logging.FileHandler("app.log")

    # Menentukan format tampilan log
    # %(asctime)s  → waktu
    # %(msecs)03d → milisecond (3 digit)
    # %(levelname)s → level log (info, warning)
    # %(message)s → isi pesan log
    formatter = LowercaseLevelFormatter(
        "%(asctime)s.%(msecs)03d [%(levelname)s] > %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"  # format tanggal & waktu
    )

    # Menghubungkan formatter ke handler
    handler.setFormatter(formatter)

    # Mengambil root logger (logger utama)
    logger = logging.getLogger()

    # Menentukan level minimal logging
    # INFO = semua log INFO, WARNING, ERROR akan muncul
    logger.setLevel(logging.INFO)

    # Cegah duplicate log (biar tidak muncul dua kali)
    if not logger.handlers:
        logger.addHandler(handler)


# Fungsi untuk mengambil logger
# Supaya bisa dipakai di file lain
def get_logger():
    return logging