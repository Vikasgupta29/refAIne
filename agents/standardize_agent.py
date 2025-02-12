from langgraph.graph import StateGraph, START
from langchain_aws import ChatBedrock
from langchain_core.messages import SystemMessage, HumanMessage
from typing_extensions import TypedDict

llm = ChatBedrock(
    credentials_profile_name="default", model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"
)

# Define the Graph State
class SQLState(TypedDict):
    standard_documents: str
    user_input: str
    response: str

def get_standardization_docs(state: SQLState) -> SQLState:
    """Get the SQL code from the user."""
    standardization_docs = "SQL Commands need to be capitalized" # Add/get the standardization docs here
    return {"standard_documents": standardization_docs}

def standardize_sql_code(state: SQLState) -> SQLState:
    """Get the SQL code from the user."""
    system_message = SystemMessage(f"You are an expert at SQL. IF the user input is SQL code, THEN standardise the SQL code with proper format and alignment and return only the standardised code without any explaination. If not, respond with 'Please provide SQL code. \n\nSTANDARDS\n---\n{state['standard_documents']}")
    messages = [system_message, HumanMessage(state["user_input"])]
    return {"response": llm.invoke(messages)}

# Create a LangGraph
workflow = StateGraph(SQLState).add_sequence([get_standardization_docs, standardize_sql_code])
workflow.add_edge(START, 'get_standardization_docs')

# Compile the Graph
standardize_graph = workflow.compile()
