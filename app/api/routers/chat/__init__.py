from fastapi import APIRouter, HTTPException, status
from app.utils.query_helpers import OpenAILLM
from api.schemas.chat import ChatCreateSchema, ChatCreateResponseSchema

from app.utils.setup_logger import setup_logger
logger = setup_logger("Query Controller")
router = APIRouter()

@router.post("/chats/", response_model=ChatCreateResponseSchema)
async def post_chat(chat: ChatCreateSchema):
    """
    Create a new chat.
    Args:
        chat: ChatCreateSchema object
        user: Current user
    Returns:
        ChatCreateResponseSchema
    """
    try:
        queryObj = OpenAILLM()
        query = queryObj.build_query_from_question(chat.content)
        result = []
        interpreted_result = queryObj.interpret_result(llm_messages=query, result=result)
        return ChatCreateResponseSchema(response = interpreted_result)
    except Exception as e:
        logger.error(f"Chat creation error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create chat")