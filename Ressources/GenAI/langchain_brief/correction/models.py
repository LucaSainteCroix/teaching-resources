from pydantic import BaseModel, Field
from typing import List, Optional

# Schema for the main route input
class MainRequest(BaseModel):
    text: str

# Schema for the question-answering route input
class QuestionRequest(BaseModel):
    question: str

# Schema for the answer response
class MainResponse(BaseModel):
    answer: str

class RAGAnswer(BaseModel):
    """The LLM answer for questions about books."""

    answer: str = Field(description="The text answer")
    answer_found: bool = Field(description="If the answer was found or not.")
    book_id: Optional[int] = Field(
        default=None, description="The ebook id of the top document from the context."
    )

# Schema for the full-text question route input
class FullTextQuestionRequest(BaseModel):
    book_id: int
    question: str


# Schema for the character extraction response
class CharacterResponse(BaseModel):
    character_names: List[str] = Field(description="List of book character names")
    answer_found: bool = Field(description="If the answer was found or not.")
    book_id: Optional[int] = Field(
        default=None, description="The ebook id of the top document from the context."
    )
