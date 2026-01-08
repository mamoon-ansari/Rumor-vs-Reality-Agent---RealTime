from typing import TypedDict
from langgraph.graph import StateGraph, END
from chains import writer_chain, reflector_chain, revisor_chain, search_tool

# Define a State Dictionary to hold data as it moves through the graph
class AgentState(TypedDict):
    topic: str
    draft: str
    search_queries: list
    search_results: str
    final_article: str

# --- NODES ---

def draft_node(state: AgentState):
    print("--- DRAFTING ---")
    response = writer_chain.invoke({"topic": state["topic"]})
    return {"draft": response.content}

def reflect_node(state: AgentState):
    print("--- REFLECTING & GENERATING QUERIES ---")
    # This returns a generic AIMessage with tool_calls
    response = reflector_chain.invoke({
        "topic": state["topic"], 
        "draft": state["draft"]
    })
    return {"search_queries": response.tool_calls}

def tool_execution_node(state: AgentState):
    print("--- EXECUTING SEARCH ---")
    clean_results = []
    
    # Check if we actually have queries to run
    if not state.get("search_queries"):
        return {"search_results": "No search queries were generated."}

    for tool_call in state["search_queries"]:
        try:
            # Execute the tool
            raw_output = search_tool.invoke(tool_call['args'])
            
            # CASE 1: Output is a List of Dictionaries (Success)
            if isinstance(raw_output, list):
                for item in raw_output:
                    # Defensive coding: check if item is actually a dict
                    if isinstance(item, dict):
                        content = item.get("content", "")
                        url = item.get("url", "Unknown source")
                        # TRUNCATE to 300 chars to save tokens
                        snippet = f"Source ({url}): {content[:300]}..."
                        clean_results.append(snippet)
                    else:
                        # Sometimes the list contains strings
                        clean_results.append(str(item)[:300])

            # CASE 2: Output is a Dictionary (Rare, but possible)
            elif isinstance(raw_output, dict):
                content = raw_output.get("content", str(raw_output))
                clean_results.append(f"Result: {content[:300]}...")

            # CASE 3: Output is a String (Error message or simple answer)
            else:
                clean_results.append(f"Result: {str(raw_output)[:300]}")

        except Exception as e:
            print(f"Error executing search: {e}")
            clean_results.append(f"Search failed: {str(e)}")
            
    # Combine all cleaned results
    final_string = "\n\n".join(clean_results)
    
    # DOUBLE SAFETY: Hard truncate the final string if it's still huge
    if len(final_string) > 2000:
        final_string = final_string[:2000] + "...(truncated)"
        
    return {"search_results": final_string}


def revise_node(state: AgentState):
    print("--- REVISING ---")
    response = revisor_chain.invoke({
        "draft": state["draft"],
        "search_results": state["search_results"]
    })
    return {"final_article": response.content}

# --- GRAPH CONSTRUCTION ---

workflow = StateGraph(AgentState)

workflow.add_node("writer", draft_node)
workflow.add_node("editor", reflect_node)
workflow.add_node("researcher", tool_execution_node)
workflow.add_node("publisher", revise_node)

# Linear flow: Writer -> Editor -> Researcher -> Publisher
workflow.add_edge("writer", "editor")
workflow.add_edge("editor", "researcher")
workflow.add_edge("researcher", "publisher")
workflow.add_edge("publisher", END)

workflow.set_entry_point("writer")
app = workflow.compile()

# --- EXECUTION ---

# Example: Ask about something that happened TODAY or very recently
inputs = {"topic": "What is the today's update on the US Nasdaq in Metal sector?"}
result = app.invoke(inputs)

print("\n" + "="*50)
print("FINAL REAL-TIME REPORT")
print("="*50)
print(result["final_article"])