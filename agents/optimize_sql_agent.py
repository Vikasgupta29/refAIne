from langgraph.graph import StateGraph, START
from langchain_aws import ChatBedrock
from langchain_core.messages import SystemMessage, HumanMessage
from typing_extensions import TypedDict

llm = ChatBedrock(
    credentials_profile_name="default", model_id="anthropic.claude-3-5-sonnet-20241022-v2:0"
)

# Define the Graph State
class SQLState(TypedDict):
    user_input: str
    response: str

def optimize_sql_code(state: SQLState) -> SQLState:
    """Get the SQL code from the user."""
    system_message = SystemMessage("You are an expert at SQL. IF the user input is SQL code, THEN optimize the sql code so that it improves efficiency and return only the optimised code without any explaination. If not, respond with 'Please provide SQL code.'")
    messages = [system_message, HumanMessage(state["user_input"])]
    return {"response": llm.invoke(messages)}

# Create a LangGraph
workflow = StateGraph(SQLState).add_sequence([optimize_sql_code])
workflow.add_edge(START, 'optimize_sql_code')

# Compile the Graph
optimize_sql_graph = workflow.compile()
