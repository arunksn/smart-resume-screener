import json
from openai import OpenAI
from .config import settings
from .prompts import RESUME_EXTRACTION_PROMPT, MATCHING_PROMPT


class LLMService:
    def __init__(self):
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def _json_completion(self, prompt: str) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "Return only valid JSON. Do not add markdown.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("LLM returned an empty response.")
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError("LLM returned invalid JSON.") from exc

    def parse_resume(self, resume_text: str) -> dict:
        return self._json_completion(
            RESUME_EXTRACTION_PROMPT.format(resume_text=resume_text)
        )

    def match_resume(self, resume_text: str, job_description: str) -> dict:
        return self._json_completion(
            MATCHING_PROMPT.format(
                resume_text=resume_text,
                job_description=job_description,
            )
        )
