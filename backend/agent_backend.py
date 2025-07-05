
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
import os
import arxiv
from typing import List, Dict, AsyncGenerator
from autogen_agentchat.teams import RoundRobinGroupChat
import asyncio

def arxive_search(query: str,max_result: int = 5) -> List[Dict]:
    """Return a compact list of aXiv papers matching *query*

    Each element contains: ``title``, ``authors``, ``published``, ``summary`` and
    ``pdf_url``. The helper is wrapped as an AutoGen *FunctionTool* below so it
    can be invoked by the agents through the normal tool-use mechanism."""

    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_result,
        sort_by=arxiv.SortCriterion.Relevance
    )

    papers: List[Dict] = []
    for result in client.results(search):
        papers.append({
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "published": result.published.isoformat(),
            "summary": result.summary,
            "pdf_url": result.pdf_url   
        })
    return papers


def create_literature_review_team(
    model_name: str = "deepseek/deepseek-chat",
    api_key: str = None,
    max_turns: int = 2
) -> RoundRobinGroupChat:
    
    """
    Create a literature review team with the specified configuration
    
    Args:
        model_name: The model to use for the agents
        api_key: API key for OpenRouter
        max_turns: Maximum turns for the team conversation
        
    Returns:
        RoundRobinGroupChat team ready to run literature reviews
    """
     
    model_client = OpenAIChatCompletionClient(
        model=model_name,
        api_key=api_key or os.getenv("OPENAIROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": "deepseek",  
        }
    )

    # Create the arXiv search tool
    arxiv_research_agent = AssistantAgent(
        name = "ArxivResearchAgent",
        description = "An agent that retrieves research papers from arXiv.",
        model_client=model_client,
        tools=[arxive_search],
        system_message="Given a user topic, think of the arXiv query.When the tool "
        "returns, choose exactly the number of papers requested and pass"
        "them as concise JSON to the summarizers."
    )

    # Create the summarizer agent
    summarizer_agent = AssistantAgent(
        name = "SummarizerAgent",
        description = "An agent that summarizes text.",
        model_client=model_client,
        system_message=(
            "You are an expert researcher.When you receive the JSON list of" \
            "papers, write a literature-review style report in Markdown:\n" \
            "1. Start with a 2-3 sentence introduction of the topic.\n" \
            "2. Then include one bullet per paper with: title (as Markdown "
            "link), authors, the specific problem tackled, and its key"
            " contributions.\n" \
            "3. Close with a single-sentence takeaway."
        ),
    )

    team = RoundRobinGroupChat(
        participants=[arxiv_research_agent, summarizer_agent],
        max_turns=max_turns
    )

    return team

async def run_team(topic: str = "AutoGen", max_papers: int = 5):
    """
    Standalone function to run the team (for testing)
    """
    team = create_literature_review_team()
    task = f"conduct a literature review on the topic - {topic} and return exactly {max_papers} papers"
    
    print(f"Starting literature review on topic: {topic}")
    print(f"Looking for {max_papers} papers...")
    print("-" * 50)
    
   
    async for msg in team.run_stream(task=task):
        try:
            # Use the same extraction logic
            content = ""
            if hasattr(msg, 'content') and msg.content:
                content = str(msg.content)
            elif hasattr(msg, 'summary') and msg.summary:
                content = str(msg.summary)
            elif hasattr(msg, 'messages') and msg.messages:
                # Extract from nested messages
                last_msg = msg.messages[-1] if isinstance(msg.messages, list) else msg.messages
                content = getattr(last_msg, 'content', str(last_msg))
            else:
                content = str(msg)
            
            source = getattr(msg, 'source', 'Unknown')
            # print(f"[{source}]: {content}")
            
        except Exception as e:
            print(f"Error processing message: {e}")
    
    print("-" * 50)


if __name__ == "__main__":
    asyncio.run(run_team("transformer architectures", 3))
    print("Literature review completed.")