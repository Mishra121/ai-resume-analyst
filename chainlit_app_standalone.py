"""
Standalone Chainlit app that communicates with the FastAPI backend via HTTP.
This approach avoids dependency conflicts between Chainlit and the main application.
"""
import chainlit as cl
import httpx
import os


# API endpoint configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
RAG_ENDPOINT = f"{API_BASE_URL}/api/v1/search/rag-agent"


@cl.on_chat_start
async def on_chat_start():
    """
    This function is called when a new chat session starts.
    """
    await cl.Message(
        content="👋 Welcome to the AI Resume Analyst! I can help you with:\n\n"
        "- 📋 Resume searches and candidate matching\n"
        "- 📊 Resume summaries\n"
        "- 📅 Availability checks\n"
        "- 🎯 Talent gap analysis\n\n"
        "Ask me anything about resumes and candidates!"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """
    Main message handler - calls the FastAPI RAG agent endpoint.
    """
    # Show a loading message
    msg = cl.Message(content="")
    await msg.send()

    try:
        # Update message to show processing
        msg.content = "🤔 Processing your query..."
        await msg.update()

        # Call the RAG agent endpoint
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                RAG_ENDPOINT,
                json={"query": message.content}
            )
            response.raise_for_status()
            result = response.json()

        # Extract the answer
        answer = result.get("answer", "Sorry, I couldn't generate an answer.")

        # Update the message with the final answer
        msg.content = answer
        await msg.update()

    except httpx.HTTPError as e:
        msg.content = f"❌ API Error: {str(e)}\n\nPlease make sure the API service is running."
        await msg.update()
        print(f"HTTP error in Chainlit app: {e}")
    except Exception as e:
        msg.content = f"❌ An error occurred: {str(e)}\n\nPlease try again or rephrase your question."
        await msg.update()
        print(f"Error in Chainlit app: {e}")
