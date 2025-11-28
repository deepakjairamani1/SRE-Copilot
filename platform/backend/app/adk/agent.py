from google.adk import Agent
from adk.prompt import SYSTEM_PROMPT

agent = Agent(
    model="gemini-2.0-flash",
    system_instruction=SYSTEM_PROMPT,
)

# Create runner once and reuse for all requests
runner = agent.create_runner()