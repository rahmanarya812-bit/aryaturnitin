import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/turnitin.db"
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "turnitin.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table for baseline corpus and uploaded documents
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT DEFAULT 'Unknown',
            institution TEXT DEFAULT 'Local Repository',
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            text_content TEXT NOT NULL,
            word_count INTEGER DEFAULT 0,
            uploaded_at TEXT NOT NULL,
            is_corpus INTEGER DEFAULT 1
        )
    """)

    # Table for similarity check reports
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_title TEXT NOT NULL,
            author TEXT DEFAULT 'Anonim',
            similarity_score REAL NOT NULL,
            ai_score REAL DEFAULT 0.0,
            total_words INTEGER DEFAULT 0,
            matched_words INTEGER DEFAULT 0,
            report_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    try:
        cursor.execute("ALTER TABLE reports ADD COLUMN ai_score REAL DEFAULT 0.0")
    except Exception:
        pass

    conn.commit()

    # Seed sample baseline corpus if database is empty
    cursor.execute("SELECT COUNT(*) FROM documents WHERE is_corpus = 1")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_corpus(conn)

    conn.close()

def seed_corpus(conn):
    cursor = conn.cursor()
    sample_docs = [
        {
            "title": "Jurnal Kecerdasan Buatan dan Deep Learning dalam Pendidikan",
            "author": "Budi Santoso",
            "institution": "Universitas Teknologi Indonesia",
            "filename": "jurnal_ai_pendidikan.txt",
            "file_path": "sample/jurnal_ai_pendidikan.txt",
            "text_content": """
Kecerdasan Buatan (Artificial Intelligence) dan Deep Learning telah mengubah lanskap pendidikan modern secara signifikan.
Penggunaan model pembelajaran mesin memungkinkan sistem pendidikan menyesuaikan materi pembelajaran sesuai dengan kecepatan dan kebutuhan individu siswa.
Selain itu, otomatisasi penilaian dan analisis data hasil belajar membantu pengajar dalam mengidentifikasi kelemahan siswa secara cepat dan presisi.
Pengolahan bahasa alami (Natural Language Processing) juga diterapkan untuk mendeteksi plagiarisme dan menganalisis teks secara otomatis pada tugas mahasiswa.
Tantangan utama dalam penerapan AI di bidang pendidikan mencakup privasi data siswa, etika kecerdasan buatan, dan kesiapan infrastruktur teknologi.
            """.strip(),
            "word_count": 82,
            "uploaded_at": datetime.now().isoformat(),
            "is_corpus": 1
        },
        {
            "title": "Analisis Performa Algoritma Pencarian Teks dan String Matching",
            "author": "Dewi Lestari",
            "institution": "Institut Teknologi Nusantara",
            "filename": "analisis_string_matching.txt",
            "file_path": "sample/analisis_string_matching.txt",
            "text_content": """
Pencarian teks dan pemocokan string (string matching) merupakan fondasi penting dalam pemrosesan data teks skala besar.
Algoritma seperti Knuth-Morris-Pratt (KMP), Boyer-Moore, dan N-gram hashing sering digunakan untuk menemukan pola kalimat yang identik atau mirip.
Dalam konteks penyorotan plagiarisme, pencocokan N-gram dan perhitungan Cosine Similarity dengan TF-IDF memberikan hasil yang sangat akurat.
Algoritma MinHash dan Locality-Sensitive Hashing (LSH) mempercepat proses perbandingan dokumen dalam basis data yang berisi jutaan sampel karya ilmiah.
            """.strip(),
            "word_count": 68,
            "uploaded_at": datetime.now().isoformat(),
            "is_corpus": 1
        },
        {
            "title": "Pengembangan Sistem Informasi Manajemen Dokumen Ilmiah Berbasis Web",
            "author": "Ahmad Rizky",
            "institution": "Jurnal Informatika Indonesia",
            "filename": "sim_dokumen_ilmiah.txt",
            "file_path": "sample/sim_dokumen_ilmiah.txt",
            "text_content": """
Sistem Informasi Manajemen Dokumen Ilmiah dirancang untuk mengelola arsip karya tulis, tesis, dan disertasi secara terintegrasi.
Arsitektur berbasis web dengan REST API dan kerangka kerja FastAPI menyediakan akses cepat, responsif, serta aman bagi para peneliti.
Sistem ini dilengkapi fitur analisis kemiripan otomatis untuk menjamin keaslian karya yang diunggah sebelum dipublikasikan.
Integrasi basis data SQLite atau PostgreSQL memastikan skalabilitas simpanan arsip dokumen hingga jutaan entri.
            """.strip(),
            "word_count": 62,
            "uploaded_at": datetime.now().isoformat(),
            "is_corpus": 1
        }
    ]

    for doc in sample_docs:
        cursor.execute("""
            INSERT INTO documents (title, author, institution, filename, file_path, text_content, word_count, uploaded_at, is_corpus)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (doc['title'], doc['author'], doc['institution'], doc['filename'], doc['file_path'], doc['text_content'], doc['word_count'], doc['uploaded_at'], doc['is_corpus']))
    
    conn.commit()

def add_document(title: str, author: str, institution: str, filename: str, file_path: str, text_content: str, is_corpus: bool = True) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    word_count = len(text_content.split())
    uploaded_at = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO documents (title, author, institution, filename, file_path, text_content, word_count, uploaded_at, is_corpus)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, author, institution, filename, file_path, text_content, word_count, uploaded_at, 1 if is_corpus else 0))
    
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return doc_id

def get_corpus_documents() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, author, institution, text_content, filename FROM documents WHERE is_corpus = 1")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_report(document_title: str, author: str, report_data: Dict[str, Any]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    ai_score = report_data.get('ai_analysis', {}).get('ai_score', 0.0)
    
    cursor.execute("""
        INSERT INTO reports (document_title, author, similarity_score, ai_score, total_words, matched_words, report_data, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        document_title,
        author,
        report_data['similarity_score'],
        ai_score,
        report_data['total_words'],
        report_data['matched_words'],
        json.dumps(report_data, ensure_ascii=False),
        created_at
    ))
    
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return report_id

def get_report(report_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    data = dict(row)
    data['report_data'] = json.loads(data['report_data'])
    return data

def get_all_reports() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, document_title, author, similarity_score, ai_score, total_words, created_at FROM reports ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
