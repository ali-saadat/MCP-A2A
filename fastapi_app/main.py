import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import json
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.sessions.in_memory_session_service import InMemorySessionService

from agents import root_agent

from fastapi_mcp import FastApiMCP

load_dotenv()
APP_NAME = "ADK Streaming example"
session_service = InMemorySessionService()


def start_agent_session(session_id: str):
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=session_id,
        session_id=session_id,
    )
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )
    run_config = RunConfig(response_modalities=["TEXT"])
    live_request_queue = LiveRequestQueue()
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue

async def agent_to_client_messaging(websocket, live_events):
    while True:
        async for event in live_events:
            if event.turn_complete:
                await websocket.send_text(json.dumps({"turn_complete": True}))
            if event.interrupted:
                await websocket.send_text(json.dumps({"interrupted": True}))
            part = event.content and event.content.parts and event.content.parts[0]
            if not part or not event.partial:
                continue
            text = event.content and event.content.parts and event.content.parts[0].text
            if not text:
                continue
            await websocket.send_text(json.dumps({"message": text}))
            await asyncio.sleep(0)

async def client_to_agent_messaging(websocket, live_request_queue):
    while True:
        text = await websocket.receive_text()
        from google.genai.types import Part, Content
        content = Content(role="user", parts=[Part.from_text(text=text)])
        live_request_queue.send_content(content=content)
        await asyncio.sleep(0)

app = FastAPI()
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    await websocket.accept()
    session_id = str(session_id)
    live_events, live_request_queue = start_agent_session(session_id)
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )
    await asyncio.gather(agent_to_client_task, client_to_agent_task)

# MCP integration
mcp = FastApiMCP(
    app,
    name="My API MCP",
    base_url="http://localhost:8000"
)
mcp.mount()
