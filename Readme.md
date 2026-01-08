# 🕵️‍♂️ Rumor vs. Reality: Real-Time News Analyst Agent

**An autonomous AI agent that fact-checks its own hallucinations in real-time, using live search and a Reflexion workflow.**

![Project Status](https://img.shields.io/badge/Status-Active-green)
![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue)
![Tech Stack](https://img.shields.io/badge/Stack-LangGraph%20|%20Groq%20|%20Tavily-orange)

---

## 💡 The Concept

Standard LLMs (like GPT-4, Llama 3) are frozen in time. If you ask them about an event that happened *this morning*, they will often:
1.  **Hallucinate:** Make up a plausible but false story based on old patterns.
2.  **Refuse:** "I cannot browse the internet."

**"Rumor vs. Reality" solves this using a 4-step cognitive loop:**

1.  **Draft (The Naive Reporter):** The AI writes a preliminary story based *only* on its internal training. This exposes what the AI "thinks" is true.
2.  **Reflect (The Skeptic):** A separate "Editor" node reviews the draft, identifies missing or suspicious claims, and generates specific search queries.
3.  **Research (The Investigator):** The agent executes those queries using the **Tavily Search API** to fetch live data from the web.
4.  **Revise (The Senior Editor):** The agent rewrites the story, citing the new evidence and correcting the original errors.


## 🧠 Workflow Nodes

- **Writer Node:** Generates the "Rumor" (Draft) using a prompt with Time Injection for current date awareness.
- **Reflector Node:** Produces tool calls (search queries) to verify claims, acting as a filter.
- **Researcher Node:** Executes search queries, truncating results to avoid token overflow.
- **Revisor Node:** Synthesizes the draft and search results into a final, fact-checked report.

---

## 🛠️ Key Features & Optimizations

- **Real-Time Data:** Uses Tavily API for news indexed minutes ago.
- **Time Awareness:** Injects current datetime into prompts to avoid outdated responses.
- **Token Optimization (Groq-Ready):**
  - **State Pruning:** Slices conversation history to keep context window small.
  - **Smart Truncation:** Limits search result text (approx. 300-400 chars per result) to stay under Groq Free Tier’s 6,000 TPM limit.
- **Error Handling:** Robust checks for API failures or empty search results.

---

## 🚀 Getting Started

1. **Prerequisites**
   - Python 3.10 or higher.
   - Groq API Key (for Llama 3 inference).
   - Tavily API Key (for AI-optimized search).

---

## 📦 Project Structure

- **app.py:** Main workflow orchestration using LangGraph’s StateGraph. Defines nodes and edges for the agent’s cognitive loop.
- **chains.py:** Contains all chain definitions, prompts, and tool bindings for Writer, Reflector, and Revisor nodes. Integrates Groq and Tavily APIs.
- **Readme.md:** Project documentation.



---

## 🏗️ Architecture

- Built on **LangGraph** with a linear StateGraph workflow:
  - Writer → Editor → Researcher → Publisher (Revisor)
- Each node is modular and handles a specific cognitive step.
- Example input: `{"topic": "What is the today's update on the US Nasdaq in Metal sector?"}`

---

## 📝 Example Execution

- The agent writes a draft, reflects to generate queries, researches live data, and revises the report, outputting a real-time, fact-checked article.

---

## 🗺️ Workflow Diagram

```mermaid
graph LR
    A[User Topic] --> B(Writer Node)
    B --> C(Reflector Node)
    C --> D(Researcher Node)
    D --> E(Revisor Node)
    E --> F[Final Verified Article]
```

<img src="RealTimeNewsAnalystAgent\RealTimeNewsAnalystAgent.png" alt="A beautiful landscape" width="400" height="200">
