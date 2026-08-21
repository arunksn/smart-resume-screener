from json import dumps, loads
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db, init_db
from .extractor import extract_text_from_input
from .llm import LLMService
from .models import Resume
from .schemas import MatchResult, ParsedResume, StoredResume


app = FastAPI(
    title="Smart Resume Screener",
    description="Parse resumes, extract structured candidate data, and match candidates to a job description.",
    version="1.0.0",
)


@app.on_event("startup")
def startup():
    init_db()


class JobDescriptionRequest(BaseModel):
    job_description: str = Field(min_length=20)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/resumes/parse", response_model=ParsedResume)
async def parse_resume(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="A resume file is required.")

    content = await file.read()
    try:
        text = extract_text_from_input(file.filename, content)
        parsed = LLMService().parse_resume(text)
        return ParsedResume.model_validate(parsed)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/resumes", response_model=StoredResume)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="A resume file is required.")

    content = await file.read()
    try:
        text = extract_text_from_input(file.filename, content)
        parsed = ParsedResume.model_validate(LLMService().parse_resume(text))
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    record = Resume(
        filename=file.filename,
        candidate_name=parsed.candidate_name,
        skills=dumps(parsed.skills),
        experience=dumps(parsed.experience),
        education=dumps(parsed.education),
        raw_text=text,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return StoredResume(
        id=record.id,
        filename=record.filename,
        candidate_name=record.candidate_name,
        skills=loads(record.skills),
        experience=loads(record.experience),
        education=loads(record.education),
    )


@app.get("/resumes", response_model=list[StoredResume])
def list_resumes(db: Session = Depends(get_db)):
    records = db.query(Resume).order_by(Resume.created_at.desc()).all()
    return [
        StoredResume(
            id=r.id,
            filename=r.filename,
            candidate_name=r.candidate_name,
            skills=loads(r.skills),
            experience=loads(r.experience),
            education=loads(r.education),
        )
        for r in records
    ]


@app.post("/resumes/{resume_id}/match", response_model=MatchResult)
def match_resume(
    resume_id: int,
    request: JobDescriptionRequest,
    db: Session = Depends(get_db),
):
    record = db.get(Resume, resume_id)
    if not record:
        raise HTTPException(status_code=404, detail="Resume not found.")

    try:
        result = LLMService().match_resume(record.raw_text, request.job_description)
        score = int(result["match_score"])
        if score < 1 or score > 10:
            raise ValueError("LLM produced a score outside the allowed 1–10 range.")

        return MatchResult(
            candidate_name=record.candidate_name,
            match_score=score,
            justification=result["justification"],
            matched_skills=result.get("matched_skills", []),
            missing_skills=result.get("missing_skills", []),
            shortlisted=score >= settings.match_threshold,
        )
    except (KeyError, TypeError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/screen", response_model=list[MatchResult])
async def screen_candidates(
    job_description: str = File(...),
    resumes: list[UploadFile] = File(...),
):
    if not job_description or len(job_description.strip()) < 20:
        raise HTTPException(status_code=400, detail="Job description is required.")

    service = LLMService()
    results = []

    for file in resumes:
        if not file.filename:
            continue
        content = await file.read()
        try:
            text = extract_text_from_input(file.filename, content)
            parsed = ParsedResume.model_validate(service.parse_resume(text))
            match = service.match_resume(text, job_description)
            score = int(match["match_score"])
            results.append(
                MatchResult(
                    candidate_name=parsed.candidate_name,
                    match_score=score,
                    justification=match["justification"],
                    matched_skills=match.get("matched_skills", []),
                    missing_skills=match.get("missing_skills", []),
                    shortlisted=score >= settings.match_threshold,
                )
            )
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process {file.filename}: {exc}",
            )

    return sorted(results, key=lambda x: x.match_score, reverse=True)
