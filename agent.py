import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

# Example query
# "What is weather in Cologne, Germany"
# "What is FastMCP?"
# "summarize this youtube video in 50 words, here is a video link: https://www.youtube.com/watch?v=xFvlUVkMPJY"
# "2+2"
query = input("Query:")

# Define llm
model = ChatOpenAI(model="gpt-4o-mini")

# Define MCP client
async def run_agent():
    
    async with MultiServerMCPClient(
        {
            "tavily": {
                "command": "python",
                "args": ["servers/tavily.py"],
                "transport": "stdio",
            },
            "youtube_transcript": {
                "command": "python",
                "args": ["servers/yt_transcript.py"],
                "transport": "stdio",
            }, 
            "math": {
                "command": "python",
                "args": ["servers/math.py"],
                "transport": "stdio",
            },       
            "weather": {
            "url": "http://localhost:8000/sse", # start your weather server on port 8000
            "transport": "sse",
            }
        }
    ) as client:
        # Load available tools
        tools = client.get_tools()
        agent = create_react_agent(model, tools)

        # Add system message
        system_message = SystemMessage(content=(
                "You have access to multiple tools that can help answer queries. "
                "Use them dynamically and efficiently based on the user's request. "
        ))

        # Process the query
        agent_response = await agent.ainvoke({"messages": [system_message, HumanMessage(content=query)]})

        # # Print each message for debugging
        # for m in agent_response["messages"]:
        #     m.pretty_print()

        return agent_response["messages"][-1].content
    
# Run the agent
if __name__ == "__main__":
    response = asyncio.run(run_agent())
    print("\nFinal Response:", response)