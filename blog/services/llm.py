from django.conf import settings
from openai import OpenAI, RateLimitError, APIError, APIConnectionError


class LLMServiceError(Exception):
    """Base exception for LLM service errors."""


class LLMQuotaError(LLMServiceError):
    """Raised when OpenAI API quota/credits are exhausted."""


class LLMUnavailableError(LLMServiceError):
    """Raised when OpenAI service is temporarily unavailable."""


class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY
        )

    def generate(self, prompt):
        try:
            response = self.client.responses.create(
                model="gpt-5-mini",
                input=prompt,
            )

            return response.output_text

        except RateLimitError as exc:
            raise LLMQuotaError(
                "AI service quota has been exhausted."
            ) from exc

        except (APIConnectionError, APIError) as exc:
            raise LLMUnavailableError(
                "AI service is currently unavailable."
            ) from exc