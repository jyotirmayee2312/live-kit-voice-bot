from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
)
from livekit.plugins import silero, aws, groq
from livekit import rtc
from dotenv import load_dotenv
import os
import json
import asyncio

load_dotenv(dotenv_path=".env")

os.environ["LIVEKIT_API_KEY"]=os.getenv("LIVEKIT_API_KEY")
os.environ["LIVEKIT_API_SECRET"]=os.getenv("LIVEKIT_API_SECRET")

print("✅ Backend starting with:")
print("LIVEKIT_URL:", os.getenv("LIVEKIT_URL"))
print("LIVEKIT_API_KEY:", os.getenv("LIVEKIT_API_KEY"))
print("LIVEKIT_API_SECRET:", os.getenv("LIVEKIT_API_SECRET"))

@function_tool
async def lookup_weather(context: RunContext, location: str):
    """Look up weather information."""
    return {"weather": "sunny", "temperature": 70}

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = Agent(
        instructions="""
            You are a friendly voice assistant built by LiveKit.
            Start every conversation by greeting the user.
            Only use the `lookup_weather` tool if the user specifically asks for weather info.
            Keep your responses conversational and concise.
        """,
        tools=[lookup_weather],
    )

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=aws.STT(language="en-US"),
        llm=groq.LLM(model="llama-3.1-8b-instant"),
        tts=aws.TTS(voice="Joanna"),
    )

    await session.start(agent=agent, room=ctx.room)
    print(f"✅ Agent session started in room: {ctx.room.name}")
    
    # Keep the session running
    while True:
        await asyncio.sleep(10)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            load_threshold=1.0        # 🚀 Don’t mark as unavailable too early
        )
    )
