#!/usr/bin/env python3
from fastmcp import FastMCP
from app.db import init_db, get_session
from app.models import Policy
from app.rag_pipeline import RAGPipeline
from app.config import VECTOR_COLLECTION
from sqlmodel import select
from rich import print as rprint

init_db()
RAG = RAGPipeline(collection_name=VECTOR_COLLECTION)

mcp = FastMCP(name="CompanyPolicyAssistant")

def current_active_collection():
    session = get_session()
    pol = session.exec(select(Policy).where(Policy.active == True).order_by(Policy.uploaded_at.desc())).first()
    session.close()
    if pol and pol.collection_name:
        return pol.collection_name
    return VECTOR_COLLECTION

@mcp.tool(name="query_policy", description="Query company policy RAG model")
def query_policy(question: str) -> dict:
    """
    This function will be exposed to Claude Desktop via MCP.
    Args:
        question: string question from the user
    Returns:
        structured dict with 'answer' and 'retrieved' fields
    """
    if not question or not question.strip():
        return {"error": "empty question"}
    coll = current_active_collection()
    rprint(f"[green]MCP: query_policy called[/green] -> collection={coll}")
    res = RAG.answer_query(question, collection_name=coll)
    return res

@mcp.tool(name="ping", description="Simple ping for health checks")
def ping() -> dict:
    return {"ok": True}

if __name__ == "__main__":
    # FastMCP.run will block and serve over stdio (Claude Desktop will spawn this script)
    mcp.run()
