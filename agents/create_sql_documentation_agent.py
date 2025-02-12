from langgraph.graph import StateGraph, START
from langchain_aws import ChatBedrock
from langchain_core.messages import SystemMessage, HumanMessage
from typing_extensions import TypedDict

llm = ChatBedrock(
    credentials_profile_name="default", model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"
)

# Define the Graph State
class SQLState(TypedDict):
    user_input: str
    response: str

def document_sql_code(state: SQLState) -> SQLState:
    """Get the SQL code from the user."""
    system_message = SystemMessage("You are an expert at SQL. IF the user input is SQL code, THEN explain what the sql code does at a high level. If not, respond with 'Please provide SQL code.'")
    messages = [system_message, HumanMessage(state["user_input"])]
    return {"response": llm.invoke(messages)}

# Create a LangGraph
workflow = StateGraph(SQLState).add_sequence([document_sql_code])
workflow.add_edge(START, 'document_sql_code')

# Compile the Graph
document_sql_graph = workflow.compile()
