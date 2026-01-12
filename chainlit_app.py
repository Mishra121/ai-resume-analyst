import chainlit as cl
from app.agents.hr_agent import hr_agent
from app.agents.state import AgentState


@cl.on_chat_start
async def on_chat_start():
    """
    This function is called when a new chat session starts.
    Initialize any session-specific data here.
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
    Main message handler - processes user queries through the RAG agent.
    """
    # Show a loading message
    msg = cl.Message(content="")
    await msg.send()

    try:
        # Initialize agent state
        state: AgentState = {
            "query": message.content,
            "intent": "",
            "retrieved_chunks": [],
            "resumes": [],
            "calendar_info": None,
            "talent_gap": None,
            "answer": None,
            "structured_output": None,
        }

        # Update message to show processing
        msg.content = "🤔 Processing your query..."
        await msg.update()

        # Invoke the HR agent
        result = hr_agent.invoke(state)

        # Extract the answer
        answer = result.get("answer", "Sorry, I couldn't generate an answer.")

        # Update the message with the final answer
        msg.content = answer
        await msg.update()

        # Optionally show additional metadata
        if result.get("intent"):
            await cl.Message(
                content=f"_Detected intent: {result['intent']}_",
                author="System"
            ).send()

    except Exception as e:
        msg.content = f"❌ An error occurred: {str(e)}\n\nPlease try again or rephrase your question."
        await msg.update()
        print(f"Error in Chainlit app: {e}")
