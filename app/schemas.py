from typing import List, Optional
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


# ---------- Upload ----------

class UploadResponse(BaseModel):
    content_id: str
    filename: str
    sha256: str
    perceptual_hash: Optional[str] = None
    message: str = "Upload received"


# ---------- AI output (Kanchan fills this in) ----------

class AIResult(BaseModel):
    synthetic_probability: float = Field(..., ge=0.0, le=1.0)
    classification: str
    generation_family: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[str] = []
    attribution_scores: Dict[str, float] = {}
    forensics: Dict[str, float] = {}


# ---------- Provenance output (Vidhi fills this in) ----------

class ProvenanceResult(BaseModel):
    provenance_found: bool
    original_content_id: Optional[str] = None
    creator: Optional[str] = None
    timestamp: Optional[str] = None
    edit_type: Optional[str] = None
    blockchain_verified: bool = False
    parent_chain: List[str] = []


class ProvenanceRegisterRequest(BaseModel):
    content_id: str
    creator: str
    signature: Optional[str] = None


class ProvenanceVerifyRequest(BaseModel):
    content_id: str


# ---------- Fused final result ----------

class FinalResult(BaseModel):
    analysis_id: str
    status: str
    synthetic_probability: float
    generation_family: Optional[str] = None
    provenance_found: bool
    blockchain_verified: bool
    confidence: float
    evidence: List[str] = []
    matched_content_id: Optional[str] = None
    attribution_scores: Dict[str, float] = {}
    forensics: Dict[str, float] = {}


class AnalyzeRequest(BaseModel):
    content_id: str