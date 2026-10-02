from pydantic import BaseModel, Field


class ClaimReview(BaseModel):
    claims: list[str] = Field(description="Important claims found in the text")
    unsupported_claims: list[str] = Field(description="Claims that need evidence or a source")
    absolute_phrases: list[str] = Field(description="Absolute or overly certain phrases")
