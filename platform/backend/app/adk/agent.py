import os
import logging
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .prompt import SYSTEM_PROMPT
from .tools import tool_context  # contains Loki tool definitions

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise EnvironmentError("GOOGLE_API_KEY not found in .env")

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# ---------------------------
# GLOBAL CONFIG
# ---------------------------
APP_NAME = "sre_incident_bot"
USER_ID = "user_1"
SESSION_ID = "session_001"

# ---------------------------
# CREATE AGENT (ONE TIME)
# ---------------------------
my_llm_agent = LlmAgent(
    name="SREIncidentBot",
    model="gemini-2.0-flash",
    instruction=SYSTEM_PROMPT,
    tools=tool_context
)

# ---------------------------
# CREATE SESSION SERVICE + RUNNER (ONE TIME)
# ---------------------------
session_service = InMemorySessionService()

# Create the session ONCE
async def init_session():
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

runner = Runner(
    agent=my_llm_agent,
    app_name=APP_NAME,
    session_service=session_service
)

# ---------------------------
# MAIN CALLER
# ---------------------------
async def call_agent_async(query: str) -> str:
    logger.info(f"[Query] {query}")

    content = types.Content(
        role="user",
        parts=[types.Part(text=query)]
    )

    # Stream ADK events
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    ):
        if event.is_final_response():
            return extract_final_text(event)

    return "No response generated."

# ---------------------------
# FINAL RESPONSE CLEANER
# ---------------------------
def extract_final_text(event):
    """
    Unified ADK result extractor.
    Ensures no JSON, no tool metadata, only plain English text.
    """

    # 1. event.text (most common for LlmAgent)
    if getattr(event, "text", None):
        return event.text.strip()

    # 2. event.model_output (tool summary)
    if getattr(event, "model_output", None):
        try:
            return event.model_output.text.strip()
        except:
            pass

    # 3. event.output (pipeline returns)
    if getattr(event, "output", None):
        return str(event.output).strip()

    # 4. content parts (fallback)
    if getattr(event, "content", None) and event.content.parts:
        parts = [p.text for p in event.content.parts if hasattr(p, "text")]
        if parts:
            return " ".join(parts).strip()

    return "No usable response."
