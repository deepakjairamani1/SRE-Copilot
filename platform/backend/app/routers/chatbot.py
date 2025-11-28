from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from google.genai import types
from ..services.redis_session_manager import session_manager

from ..adk.agent import call_agent_async
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])


APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"
class ChatMessageRequest(BaseModel):
    """Request model for chatbot messages"""
    message: str
    conversation_id: Optional[str] = None
    reset_conversation: bool = False


class ChatMessageResponse(BaseModel):
    """Response model for chatbot messages"""
    response: str
    tokens_used: int
    model: str
    conversation_id: Optional[str] = None
    status: str
    error: Optional[str] = None


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """
    Handle user message using ADK runner.
    """
    try:
        logger.info(f"Request: message='{request.message}', conversation_id={request.conversation_id}")
        session_id = request.conversation_id or session_manager.create_session()
        session_state = session_manager.get_session(session_id)
        logger.info((session_state, session_id, "frrgtyhujyh"))
        # user_message = types.Content(request.message)
        # content = types.Content(role='user', parts=[types.Part(text=request.message)])
        # logger.info((user_message, "frrgtyhujyh"))
        final_text = None
        updated_state = None
        logger.info(("session_state", session_state))
        logger.info("gruhrhbeifdop")
        final_text = response = asyncio.run(call_agent_async(request.message))

        # Save state back to Redis
        if updated_state is not None:
            session_manager.update_session(session_id, updated_state)
        return ChatMessageResponse(
            conversation_id=session_id,
            response=final_text or "Unable to respond right now.",
            tokens_used=0,  # TODO: Track actual token usage
            model="gemini-2.0-flash",
            status="success"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

