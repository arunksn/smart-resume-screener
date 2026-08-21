# Smart Resume Screener

A backend API that intelligently parses PDF/TXT resumes, extracts structured candidate information, stores parsed resumes, and uses an LLM to compare candidates with a job description.

## Assignment Requirements Covered

The implementation follows the supplied company assignment:

- **Input:** PDF/Text resumes + job description
- **Structured extraction:** skills, experience, education
- **LLM matching:** 1–10 fit score with evidence-based justification
- **Shortlisting:** candidates are marked shortlisted using a configurable score threshold
- **Backend API:** Python + FastAPI
- **Database storage:** SQLite via SQLAlchemy
- **Optional frontend:** intentionally not included because it is optional in the assignment
- **Deliverables:** GitHub-ready repository, architecture documentation, and LLM prompts

The assignment explicitly evaluates code quality/structure, data extraction, LLM prompt quality, and output clarity.

## Architecture

```text
PDF/TXT Resume
      |
      v
FastAPI Upload API
      |
      v
Text Extraction (PyMuPDF / UTF-8)
      |
      v
LLM Structured Extraction
      |
      +----> skills
      +----> experience
      +----> education
      |
      v
SQLite Database
      |
      v
LLM Semantic Matching
      |
      +----> 1–10 match score
      +----> justification
      +----> matched skills
      +----> missing skills
      |
      v
Shortlisted Candidate JSON
```

## Project Structure

```text
smart_resume_screener/
├── app/
│   ├── config.py
│   ├── database.py
│   ├── extractor.py
│   ├── llm.py
│   ├── main.py
│   ├── models.py
│   ├── prompts.py
│   └── schemas.py
├── tests/
│   └── test_extractor.py
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your LLM API key to `.env`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
DATABASE_URL=sqlite:///./resume_screener.db
MATCH_THRESHOLD=7
```

Run:

```bash
uvicorn app.main:app --reload
```

API documentation is available through FastAPI's generated documentation at `/docs`.

## API Flow

### 1. Parse a resume

`POST /resumes/parse`

Upload a PDF or TXT resume.

The API extracts text and asks the LLM to return:

- candidate name
- skills
- experience
- education

### 2. Store a resume

`POST /resumes`

The resume is parsed and its structured information plus extracted text are stored in SQLite.

### 3. List stored resumes

`GET /resumes`

Returns all parsed candidates.

### 4. Match a candidate

`POST /resumes/{resume_id}/match`

Body:

```json
{
  "job_description": "Python backend developer with FastAPI and SQL experience..."
}
```

The response includes:

```json
{
  "candidate_name": "Candidate",
  "match_score": 8,
  "justification": "The candidate demonstrates ...",
  "matched_skills": ["Python", "FastAPI"],
  "missing_skills": ["Docker"],
  "shortlisted": true
}
```

### 5. Screen multiple candidates

`POST /screen`

Accepts a job description and multiple resume files and returns candidates ranked by match score.

## LLM Prompts

The extraction and matching prompts are stored separately in `app/prompts.py`.

### Resume extraction prompt

The prompt instructs the model to:

1. extract only evidence present in the resume,
2. avoid inventing facts,
3. return a fixed JSON schema,
4. separate skills, experience, and education.

### Matching prompt

The prompt instructs the model to:

1. compare resume evidence against the job description,
2. produce a 1–10 fit score,
3. justify the score using evidence,
4. identify matched skills,
5. identify missing skills,
6. avoid inventing candidate qualifications.

Temperature is set to `0` for deterministic structured output.

## Shortlisting

The API uses `MATCH_THRESHOLD=7` by default.

- Score 7–10 → shortlisted
- Score 1–6 → not shortlisted

The threshold is configurable through `.env` so the screening rule remains explicit and testable.

## Testing

Run:

```bash
pytest
```



