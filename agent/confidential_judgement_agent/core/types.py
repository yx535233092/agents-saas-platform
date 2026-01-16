"""类型定义模块"""

from typing import TypedDict, Optional, List, Dict, Any
from typing_extensions import NotRequired


class AnalysisResult(TypedDict):
    """分析结果基础类型"""
    result: str
    confidence: int
    evidence: str


class SecretAnalysisResult(AnalysisResult):
    """秘密目录分析结果"""
    match_score: NotRequired[int]
    key_matches: NotRequired[List[str]]
    risk_level: NotRequired[str]


class PublicAnalysisResult(TypedDict):
    """公开性分析结果"""
    is_public: bool
    confidence: int
    evidence: str


class RetrievalChunk(TypedDict):
    """检索结果中的 chunk"""
    chunk_id: str
    similarity: float
    content_with_weight: NotRequired[str]
    highlight: NotRequired[str]
    content_ltks: NotRequired[str]
    docnm_kwd: NotRequired[str]


class RetrievalResult(TypedDict):
    """检索结果"""
    success: bool
    code: int
    message: str
    total: int
    chunks_count: int
    scene: str
    chunks: List[RetrievalChunk]
    doc_aggs: NotRequired[List[Dict[str, Any]]]
    chunk_summary: NotRequired[str]
    error: NotRequired[str]


class DecisionResult(TypedDict):
    """决策评审结果"""
    is_sensitive: bool
    confidence: int
    evidence: str

