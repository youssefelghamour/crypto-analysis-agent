"""FastAPI API for the cryptocurrency analysis agent"""
from uuid import uuid4
from fastapi import FastAPI
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from graphs.main_graph import build_main_graph
from fastapi.encoders import jsonable_encoder


app = FastAPI(
    title="Crypto Analysis Agent API",
    description="Generate cryptocurrency reports and discuss market conditions",
    version="1.0.0",
)

# Build the graph once when the API starts
agent, db_connection = build_main_graph()


class AgentRequest(BaseModel):
    """Request body for interacting with the agent"""
    message: str = Field(min_length=1)
    thread_id: str | None = None


@app.get("/health")
def health_check():
    """Check if the API is running"""
    return {"status": "ok"}


@app.post("/agent")
def interact_with_agent(request: AgentRequest):
    """Invokes the main agentic workflow with the user message"""

    thread_id = request.thread_id or str(uuid4())

    result = agent.invoke(
        {
            "request": request.message,
            "messages": [HumanMessage(content=request.message)],
        },
        config={"configurable": {"thread_id": thread_id}},
    )

    if result.get("intent") == "report":
        response = jsonable_encoder(result.get("final_report"))
    else:
        response = result.get("discussion_response")

    return {
        "thread_id": thread_id,
        "intent": result.get("intent"),
        "response": response,
    }
