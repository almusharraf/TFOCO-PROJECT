"""
TFOCO Financial Document Reader - FastAPI Main Application
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

from app.extractors.document_processor import DocumentProcessor
from app.models.schemas import ExtractionResponse, HealthResponse

# Initialize FastAPI app
app = FastAPI(
    title="TFOCO Financial Document Reader",
    description="AI-powered Named Entity Recognition for financial documents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize document processor
processor = DocumentProcessor()

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """Root endpoint"""
    return {
        "message": "TFOCO Financial Document Reader API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=int(time.time())
    )


@app.post("/api/v1/extract", response_model=ExtractionResponse, tags=["Extraction"])
async def extract_entities(
    file: UploadFile = File(..., description="Document file (PDF, DOCX, or TXT)")
) -> ExtractionResponse:
    """
    Extract financial entities from uploaded document
    
    Args:
        file: Uploaded document file
        
    Returns:
        ExtractionResponse with extracted entities and metadata
        
    Raises:
        HTTPException: If file is invalid or processing fails
    """
    start_time = time.time()
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    try:
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // 1024 // 1024}MB"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Empty file")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    
    # Save to temporary file for processing
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_ext,
            mode='wb'
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Process document
        entities = processor.process_document(temp_path, file.filename)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        return ExtractionResponse(
            filename=file.filename,
            file_size=file_size,
            entities=entities,
            processing_time_ms=processing_time,
            entity_count=len(entities)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )
    
    finally:
        # Cleanup temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

