import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from .prompt_v2 import SYSTEM_PROMPT
from google.genai import types
import logging
from .tools import tools


logger = logging.getLogger(__name__)


load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise EnvironmentError("GOOGLE_API_KEY not found. Please set it in a .env file.")

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# agent = LlmAgent(
#     name="ChatbotAgent",
#     instruction=SYSTEM_PROMPT,
# )

APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

# session_service = InMemorySessionService()
my_llm_agent = LlmAgent(
    name="ModelCallbackAgent",
    tools=tools,

    model="gemini-2.0-flash",
    instruction=SYSTEM_PROMPT,
)
session_service = InMemorySessionService()
runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)

async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner

async def call_agent_async(query):
    logger.info(f"Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
    
    final_response = None
    async for event in events:
        if event.is_final_response():
            final_response  = extract_final_text(event)    
            return final_response
    
    # logger.info("Agent Response: ", final_response)
    # return final_response

def extract_final_text(event):
    # Priority 1: direct text
    if getattr(event, "text", None):
        return event.text.strip()

    # Priority 2: output field
    if getattr(event, "output", None):
        return str(event.output).strip()

    # Priority 3: content parts
    parts = []
    if getattr(event, "content", None) and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "text") and part.text:
                parts.append(part.text)

    if parts:
        return "\n".join(parts).strip()

    return None

