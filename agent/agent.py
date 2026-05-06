import json
import os
from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# ---------------------------
# LLM
# ---------------------------
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

# ---------------------------
# System Prompt
# ---------------------------
system_prompt = """
You are an AI Email Assistant. You help users manage their inbox.

TOOLS AVAILABLE:
- fetch_emails: Fetches all emails. Call this whenever you need email data.
- summarize_emails: Summarizes emails. Pass the full JSON string from fetch_emails.
- classify_email: Classifies ONE email. You MUST pass a JSON string like: '{"id": "1", "subject": "...", "body": "..."}'
- send_reply: Sends a reply. Requires email_id (string) and reply_body (string).

STRICT RULES:
1. When classifying, ALWAYS pass email_data as a JSON string, never as an object.
2. When user says "send reply" without specifying which email:
   - Ask: "Which email would you like to reply to? (1-6)"
   - Wait for their answer before doing anything.
3. When user picks an email but gives no reply content:
   - Show a draft reply you composed based on the email content.
   - Ask: "Should I send this reply? (yes/no) Or type your own reply."
   - Wait for confirmation before calling send_reply.
4. Only call send_reply AFTER the user has confirmed or provided the reply text.
5. Keep context across the conversation. Remember which email the user was discussing.
6. Be concise and friendly. Don't repeat the full email list unless asked.
"""

# ---------------------------
# MCP server path
# ---------------------------
MCP_SERVER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "mcp_server", "app.py"
)

# ---------------------------
# Persistent agent state
# ---------------------------
_agent = None
_client = None
_conversation_history = []


async def _init_agent():
    global _agent, _client
    if _agent is None:
        _client = MultiServerMCPClient(
            {
                "email_assistant": {
                    "command": "python",
                    "args": [MCP_SERVER_PATH],
                    "transport": "stdio",
                }
            }
        )
        tools = await _client.get_tools()
        _agent = create_react_agent(llm, tools, prompt=system_prompt)
    return _agent


async def run_query(query: str) -> str:
    """Run a query with full conversation history so the agent remembers context."""
    global _conversation_history

    agent = await _init_agent()

    # Append user message to history
    _conversation_history.append({"role": "user", "content": query})

    # Build messages list: history as tuples
    messages = [(m["role"], m["content"]) for m in _conversation_history]

    response = await agent.ainvoke({"messages": messages})

    # Check for send_reply tool calls in the new messages generated this turn
    new_messages = response.get("messages", [])[len(messages):]
    for msg in new_messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc.get("name") == "send_reply":
                    reply_body = tc.get("args", {}).get("reply_body", "")
                    print(f"\n[Model Sent Reply]:\n{reply_body}\n")

    all_messages = response.get("messages", [])
    if all_messages:
        final = all_messages[-1].content
        # Save assistant reply to history
        _conversation_history.append({"role": "assistant", "content": final})
        return final

    return "No response generated."


def reset_conversation():
    global _conversation_history
    _conversation_history = []