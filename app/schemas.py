from typing import Any
from pydantic import BaseModel, Field


class ParsedResume(BaseModel):
    candidate_name: str = "Unknown"
    skills: list[str] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)


class MatchResult(BaseModel):
    candidate_name: str
    match_score: int = Field(ge=1, le=10)
    justification: str
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    shortlisted: bool


class StoredResume(BaseModel):
    id: int
    filename: str
    candidate_name: str
    skills: list[str]
    experience: list[dict]
    education: list[dict]
