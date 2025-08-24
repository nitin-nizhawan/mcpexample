from langchain.agents import initialize_agent
from langchain.tools import Tool
from langchain_ollama import OllamaLLM, ChatOllama
from langchain.schema import BaseMessage,SystemMessage, HumanMessage,AIMessage
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
import json
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from typing import TypedDict,List
from langgraph.prebuilt import ToolNode
from langchain.chat_models import init_chat_model
from langchain_core.messages.tool import ToolMessage
import re
system="You are helpful CLI assistant. Use tools when needed, and respond clearly and concisely. Always think step-by-step before answering."
class AgentState(TypedDict):
    messages:List[BaseMessage]
    tools:List[Tool]
    system_prompt:str

def input_node(state: AgentState) -> AgentState:
    query = input("You: ")
    #print(state)
    state["messages"].append(HumanMessage(content=query))
    return state


def should_continue2(state: AgentState):
    #print("2should continue2")
    #print(state)
    messages= state["messages"]
    last_message = messages[-1]
    if last_message is ToolMessage:
        #print("2returning input")
        return "input"
    #print("2returning llm")
    return "llm"
def should_continue(state: AgentState):
    #print("should continue")
    #print(state)
    messages= state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        #print("returning tools")
        return "tools"
    #print("returning input")
    return "input"
def createToolNode(tools):
  toolNode = ToolNode(tools);
  async def tool_node(state: AgentState) -> AgentState:
     response = await toolNode.ainvoke(state)
     state["messages"].append(response["messages"][0])
     return state
  return tool_node
def strip_thinking(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
def build_graph(tools):
#    llm =  OllamaLLM(model="qwen3:4b", system=SystemMessage(content=system))
    llm = init_chat_model("ollama:qwen3:4b")
    llm = llm.bind_tools(tools)
    async def llm_node(state: AgentState) -> AgentState:
        #print("llm node invokdd")
        #print(state)
        print("Thinking...")
        response = await llm.ainvoke(state["messages"])
        print(strip_thinking(response.content))
        state["messages"].append(response)
        #print("After llminvoke")
        #print(state)
        return state
    graph = StateGraph(AgentState)
#    tool_node = ToolNode(tools)

    graph.add_node("input", RunnableLambda(input_node))
    graph.add_node("llm", RunnableLambda(llm_node))
    graph.add_node("tools",createToolNode(tools))
    graph.set_entry_point("input")
    graph.add_edge("input", "llm")
    graph.add_conditional_edges("llm",should_continue)
    graph.add_conditional_edges("tools",should_continue2)
    return graph.compile()



server_params = StdioServerParameters(
    command="python3",
    # Make sure to update to the full absolute path to your math_server.py file
    args=["filesystem_mcp_server.py"],
)
    
# 🧰 Wrap tools from all MCP clients

async def main():
  async with stdio_client(server_params) as (read, write):
      async with ClientSession(read, write) as session:
           await session.initialize()
           tools = await load_mcp_tools(session)
           state = AgentState(messages=[SystemMessage(content=system)], system_prompt=system)
           graph = build_graph(tools)
           #print(state)
           await graph.ainvoke(state)

if __name__ == "__main__":
    asyncio.run(main())


