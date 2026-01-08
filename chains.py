import os
import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.output_parsers import JsonOutputToolsParser

load_dotenv()
# 1. Setup Tools & LLM
# We use Tavily to get REAL-TIME news
search_tool = TavilySearchResults(max_results=3)
llm = ChatGroq(model_name="llama-3.1-8b-instant")

# 2. The "Naive" Writer (Draft Node)
# This prompt forces the AI to try answering even if it doesn't know, 
# which exposes hallucinations we can fix later.
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a reporter. Write a preliminary draft about the user's topic. "
               "If you don't have current info, make your best educated guess based on past context."),
    ("human", "{topic}"),
]).partial(
    time=lambda: datetime.datetime.now().isoformat(),
)
writer_chain = writer_prompt | llm

# 3. The "Skeptical" Editor (Reflect Node)
# This node DOES NOT write text. It only generates SEARCH QUERIES.
# We bind the search tool to it so it outputs structured tool calls.
reflection_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a strict editor. Read the draft below. Identify any claims that need verification "
               "or missing up-to-date information. Generate search queries to fix these issues."),
    ("human", "Original Topic: {topic}\n\nDraft:\n{draft}"),
])
# We force the LLM to ONLY output tool calls here
reflector_chain = reflection_prompt | llm.bind_tools([search_tool])

# 4. The Revisor (Final Node)
# Takes the original draft + the search results and writes the final article.
revision_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a senior editor. Rewrite the draft using the verified search results below. "
               "Cite your sources. If the draft was wrong, correct it explicitly."),
    ("human", "Original Draft:\n{draft}\n\nSearch Results:\n{search_results}\n\nWrite the final article:"),
]).partial(
    time=lambda: datetime.datetime.now().isoformat(),
)
revisor_chain = revision_prompt | llm