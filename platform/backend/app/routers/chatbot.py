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
        session_id = request.conversation_id or session_manager.create_session()
        final_text = None
        updated_state = None
        
        # Check if user is asking for metrics/CPU/prometheus related queries
        query_lower = request.message.lower()
        if any(keyword in query_lower for keyword in ['cpu', 'memory', 'metrics', 'prometheus', 'prom', 'performance', 'system']):
            logger.info("Detected metrics-related query, should use prometheus tool")
        
        final_text = await call_agent_async(request.message)        
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
        logger.error(f"Error in send_message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

