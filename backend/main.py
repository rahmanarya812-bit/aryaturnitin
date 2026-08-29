import os
import shutil
import tempfile
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse

from database import init_db, add_document, get_corpus_documents, save_report, get_report, get_all_reports
from parser import extract_text, extract_text_from_bytes
from similarity import analyze_plagiarism
from ai_detector import detect_ai_generated_text
from paraphraser import paraphrase_text
from pdf_report import generate_pdf_report

app = FastAPI(
    title="Turnitin Clone API",
    description="Sistem Pengecekan Plagiarisme Teks & AI Writing Detector Lengkap",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure database initialized on startup
@app.on_event("startup")
def startup_event():
    init_db()

if os.environ.get("VERCEL"):
    UPLOAD_DIR = "/tmp/uploads"
else:
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

from typing import Optional

@app.post("/api/check")
async def check_plagiarism(
    file: Optional[UploadFile] = None,
    raw_text: Optional[str] = Form(None),
    title: str = Form("Dokumen Analisis"),
    author: str = Form("Penulis"),
    exclude_bibliography: bool = Form(True),
    exclude_quotes: bool = Form(True),
    exclude_sources: bool = Form(False),
    exclude_matches: bool = Form(False),
    no_repository: bool = Form(True)
):
    """Perform plagiarism similarity check AND AI writing detection with exclusion filters."""
    extracted_text = ""
    file_name = "raw_input.txt"

    if file and file.filename:
        file_name = file.filename
        file_bytes = await file.read()
        extracted_text = extract_text_from_bytes(file_bytes, file_name)
    elif raw_text and raw_text.strip():
        extracted_text = raw_text
    else:
        raise HTTPException(status_code=400, detail="Silakan unggah dokumen atau masukkan teks untuk diperiksa.")

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Dokumen kosong atau teks tidak dapat diekstraksi.")

    try:
        # Get corpus documents
        corpus_docs = get_corpus_documents()
        
        # Run similarity analysis engine with exclusion filters
        analysis_result = analyze_plagiarism(
            target_text=extracted_text,
            corpus_docs=corpus_docs,
            exclude_bibliography=exclude_bibliography,
            exclude_quotes=exclude_quotes,
            exclude_sources=exclude_sources,
            exclude_matches=exclude_matches
        )

        # Attach filter settings metadata
        analysis_result['filters'] = {
            "exclude_bibliography": exclude_bibliography,
            "exclude_quotes": exclude_quotes,
            "exclude_sources": exclude_sources,
            "exclude_matches": exclude_matches,
            "no_repository": no_repository
        }

        # Run AI Writing Detector Engine
        ai_result = detect_ai_generated_text(text=extracted_text)
        analysis_result['ai_analysis'] = ai_result

        # Save to database report history
        report_id = save_report(
            document_title=title if title else file_name,
            author=author,
            report_data=analysis_result
        )

        # If no_repository is FALSE, auto add document to baseline corpus for future checks
        if not no_repository and extracted_text.strip():
            add_document(
                title=title,
                author=author,
                institution="User Uploaded Document",
                filename=file_name,
                file_path=temp_path if file else "raw_input.txt",
                text_content=extracted_text,
                is_corpus=True
            )

        return {
            "status": "success",
            "report_id": report_id,
            "similarity_score": analysis_result['similarity_score'],
            "ai_score": ai_result['ai_score'],
            "total_words": analysis_result['total_words'],
            "matched_words": analysis_result['matched_words'],
            "sources_count": len(analysis_result['sources'])
        }
    except Exception as e:
        print(f"Error processing check: {e}")
        raise HTTPException(status_code=500, detail=f"Gagal memproses dokumen: {str(e)}")

@app.post("/api/paraphrase")
async def paraphrase_api(text: str = Form(...)):
    """API Endpoint to automatically paraphrase text and lower plagiarism similarity score."""
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Teks wajib diisi untuk diparafrase.")
    
    res = paraphrase_text(text)
    return {"status": "success", "result": res}

@app.post("/api/corpus")
async def add_to_corpus(
    file: UploadFile = File(...),
    title: str = Form(...),
    author: str = Form("Unknown"),
    institution: str = Form("Repositori Lokal")
):
    """Add a new baseline document to the similarity database corpus."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="File wajib diunggah.")

    temp_path = os.path.join(UPLOAD_DIR, f"corpus_{file.filename}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text(temp_path)
    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="File kosong atau tidak dapat diekstraksi.")

    doc_id = add_document(
        title=title,
        author=author,
        institution=institution,
        filename=file.filename,
        file_path=temp_path,
        text_content=extracted_text,
        is_corpus=True
    )

    return {"status": "success", "document_id": doc_id, "message": "Dokumen referensi berhasil ditambahkan ke repositori Turnitin."}

@app.get("/api/corpus")
async def list_corpus():
    """List all baseline documents in the corpus."""
    docs = get_corpus_documents()
    # Exclude text_content for lightweight response
    return [{k: v for k, v in doc.items() if k != 'text_content'} for doc in docs]

@app.get("/api/reports")
async def list_reports():
    """List all plagiarism check reports."""
    return get_all_reports()

@app.get("/api/reports/{report_id}")
async def get_report_detail(report_id: int):
    """Get full report data by ID for interactive viewer."""
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan.")
    return report

@app.get("/api/reports/{report_id}/export")
async def export_pdf_report(report_id: int):
    """Export Turnitin Originality Report as PDF."""
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan.")

    pdf_buffer = generate_pdf_report(report)
    filename = f"Turnitin_Report_{report_id}_{report['document_title'].replace(' ', '_')}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

# Serve Frontend static files (Local & Non-serverless fallback)
try:
    FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
    if os.path.exists(FRONTEND_DIR):
        app.mount("/static", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
except Exception as e:
    print(f"Static files mount skipped: {e}")
