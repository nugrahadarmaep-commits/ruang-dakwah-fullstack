"""
Inisialisasi Ekstensi Aplikasi Flask.
Modul ini memisahkan instance SQLAlchemy agar terhindar dari siklus impor (circular imports).
"""

from flask_sqlalchemy import SQLAlchemy

# Instance ORM Database SQLAlchemy
db = SQLAlchemy()