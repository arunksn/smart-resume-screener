RESUME_EXTRACTION_PROMPT = """
You are a resume information extraction system.

Extract only information supported by the resume text. Do not invent facts.

Return valid JSON with exactly these keys:
{
  "candidate_name": "string",
  "skills": ["skill1", "skill2"],
  "experience": [
    {
      "job_title": "string",
      "company": "string",
      "duration": "string",
      "responsibilities": ["string"]
    }
  ],
  "education": [
    {
      "degree": "string",
      "institution": "string",
      "year": "string"
    }
  ]
}

Resume text:
{resume_text}
"""


MATCHING_PROMPT = """
Compare the following resume with the job description.

Rate the candidate's fit from 1 to 10. The score must reflect the evidence in
the resume against the stated requirements. Do not invent experience, skills,
education, or qualifications.

Return valid JSON with exactly these keys:
{
  "match_score": 1,
  "justification": "concise evidence-based explanation",
  "matched_skills": ["skill1"],
  "missing_skills": ["skill1"]
}

Resume:
{resume_text}

Job Description:
{job_description}
"""
