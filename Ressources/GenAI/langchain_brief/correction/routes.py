from fastapi import APIRouter, HTTPException, Depends
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.schema.agent import AgentFinish
import logging
from models import (
    MainRequest,
    QuestionRequest,
    RAGAnswer,
    MainResponse,
    FullTextQuestionRequest,
    CharacterResponse,
)
from dependencies import get_vector_store
from services.rag import create_vector_store_from_full_text
from services.openai_llm import get_answer_with_rag
from services.get_full_book_text import get_text_by_id
from services.llm_agent import decide_route

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/", response_model=MainResponse)
async def main_route(request: MainRequest, vector_store = Depends(get_vector_store)):
    input_text = request.text
    functions = [answer_question, answer_question_full_text, get_characters]
    tools = [convert_to_openai_function(function) for function in functions]

    # Use the LLM LangChain agent to decide which route to take
    agent_result = decide_route(input_text, tools)
    print(agent_result)

    if isinstance(agent_result, AgentFinish):
        print('no tools to call')
        return MainResponse(answer="Please only ask questions about books")

    else:

        if agent_result.tool == "answer_question":
            print("agent chose to answer without full text")
            response = await answer_question(QuestionRequest(question=input_text), vector_store)
            return response

        elif agent_result.tool == "answer_question_full_text":
            print("agent chose to answer with full text")
            book_id = agent_result.tool_input['request'].get('book_id')
            if book_id:
                response = await answer_question_full_text(
                    FullTextQuestionRequest(book_id=book_id, question=input_text)
                )
                return response
            else:
                raise HTTPException(status_code=400, detail="No Book ID given")

        elif agent_result.tool == "get_characters":
            response = await get_characters(QuestionRequest(question=input_text), vector_store)
            if response.character_names:
                text_response = str(response.character_names)
                # text_response = ', '.join(response.character_names)
            else:
                text_response = '[]'
            return MainResponse(answer=text_response)

        else:
            raise HTTPException(status_code=400, detail="Unable to process the request.")


@router.post("/answer_question", response_model=MainResponse)
async def answer_question(request: QuestionRequest, vector_store = Depends(get_vector_store)):
    """
    Function to answer questions about books when no book_id is given.
    """

    response = await get_answer_with_rag(request, vector_store, RAGAnswer)

    if not response.answer_found:
        if response.book_id:
            # optional, here we could check if the id is really in our database

            full_text_question_request = FullTextQuestionRequest(book_id=response.book_id,
                                                                 question=request.question)

            response_full_text = await answer_question_full_text(full_text_question_request)

            return MainResponse(answer=response_full_text.answer)

        else:
            return MainResponse(answer="Could not find any answer to your question")

    else:

        return MainResponse(answer=response.answer)


@router.post("/answer_question_full_text", response_model=MainResponse)
async def answer_question_full_text(request: FullTextQuestionRequest):
    """
    Retrieves and queries the full text of the book to get the answer.
    For that it needs the book_id. If no book_id were given explicitely, do NOT use this function.
    """
    print("retrieving full text with book_id")

    full_text = await get_text_by_id(request.book_id)
    if full_text:
    # create vector store from full text and use RAG + LLM over it
        print("creating vector store from full text")
        vector_store = await create_vector_store_from_full_text(full_text, request.book_id)
        print("getting answer from vector store with RAG & LLM")
        response = await get_answer_with_rag(request, vector_store, RAGAnswer)

        return MainResponse(answer=response.answer)


    else:
        return MainResponse(
        answer=f"No text for book {request.book_id} could be found to answer your question."
        )


@router.post("/get_characters", response_model=CharacterResponse)
async def get_characters(request: QuestionRequest, vector_store = Depends(get_vector_store)):
    """
    Answers questions specifically and only about the character names of a book.
    Example question: 'What are the characters in Hamlet by Shakespeare?'
    """

    response = await get_answer_with_rag(request, vector_store, CharacterResponse)
    print(response)

    return response
