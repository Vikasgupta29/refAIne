from langgraph.graph import StateGraph, START
from langchain_aws import ChatBedrock
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from typing_extensions import TypedDict

llm = ChatBedrock(
    credentials_profile_name="default", model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"
)

# Define the Graph Statey
class SQLState(TypedDict):
    user_input: str
    response: str

def fix_sql_code(state: SQLState) -> SQLState:
    """Get the SQL code from the user."""
    system_message = SystemMessage("""You are an expert at SQL. IF the user input is a SQL code, THEN fix the syntax errors and return only the fixed code without any explaination. If not, respond with 'Please provide SQL code.'""")
    human_message = HumanMessage("select * from table column=value")
    ai_message = AIMessage("SELECT * FROM table WHERE column = 'value'")
    human_message = HumanMessage("select ? from table column=value")
    ai_message = AIMessage("SELECT * FROM table WHERE column = 'value'")
    messages = [system_message,human_message,ai_message, HumanMessage(state["user_input"])]
    return {"response": llm.invoke(messages)}

# Create a LangGraph
workflow = StateGraph(SQLState).add_sequence([fix_sql_code])
workflow.add_edge(START, 'fix_sql_code')

# Compile the Graph
syntax_fix_graph = workflow.compile()
