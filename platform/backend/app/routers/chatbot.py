from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from google.adk import Content
from services.redis_session_manager import session_manager

from adk.agent import runner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])


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
        session_id = request.conversation_id or session_manager.create_session()
        session_state = session_manager.get_session(session_id)

        user_message = Content.text(request.message)

        final_text = None
        updated_state = None

        async for event in runner.run_async(
            user_id="USER",
            session_id=session_id,
            new_message=user_message,
            state_delta=session_state
        ):
            # Capture final logical response
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_text = event.content.parts[0].text

            # Capture updated session state
            if event.state is not None:
                updated_state = event.state

        # Save state back to Redis
        if updated_state is not None:
            session_manager.update_session(session_id, updated_state)

        return ChatMessageResponse(
            conversation_id=session_id,
            response=final_text or "Unable to respond right now."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

