"""
Sarawak Tourism Agent Swarm
Implements a 3-agent architecture for answering tourism queries.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import google.generativeai as genai
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.rag_pipeline import RAGPipeline, initialize_pipeline

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class TripPlannerAgent:
    """
    Trip Planner Agent (Router)
    Uses Gemini 2.5 Flash to analyze user queries and extract key topics.
    """
    
    SYSTEM_PROMPT = """You are a Trip Planner Agent for Sarawak, Malaysia tourism.
Your job is to analyze the user's query about Sarawak and extract the key location, 
attraction, or topic they are asking about.

Rules:
1. Return ONLY the key topic or location (e.g., "Bako National Park", "Rainforest World Music Festival", "Mulu Caves")
2. If multiple topics are mentioned, return the primary one
3. If the query is too general, return "Sarawak general tourism"
4. Keep your response to 1-2 sentences maximum

Examples:
- "What wildlife can I see at Bako?" → "Bako National Park wildlife"
- "Tell me about the music festival" → "Rainforest World Music Festival"
- "How do I get to Mulu Caves?" → "Mulu Caves transportation access"
"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        """Initialize the Trip Planner Agent."""
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=self.SYSTEM_PROMPT
        )
    
    def extract_topic(self, user_query: str) -> str:
        """
        Extract the key topic from a user query.
        
        Args:
            user_query: The user's question about Sarawak
            
        Returns:
            Extracted topic string
        """
        try:
            response = self.model.generate_content(user_query)
            return response.text.strip()
        except Exception as e:
            print(f"Trip Planner Error: {e}")
            # Fallback: return the original query
            return user_query


class SarawakInfoAgent:
    """
    Sarawak Info Agent (Researcher)
    Uses RAG pipeline to retrieve relevant information from documents.
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the Sarawak Info Agent with RAG pipeline."""
        self.pipeline = initialize_pipeline(data_dir=data_dir)
    
    def research(self, topic: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Research a topic using the RAG pipeline.
        
        Args:
            topic: The topic to research
            num_results: Number of results to retrieve
            
        Returns:
            Dictionary with 'context' and 'sources' keys
        """
        try:
            results = self.pipeline.search_documents(topic, k=num_results)
            
            if not results:
                return {
                    'context': "No relevant information found in the knowledge base.",
                    'sources': []
                }
            
            # Format context
            context_parts = []
            sources = []
            
            for i, result in enumerate(results, 1):
                source = result['metadata'].get('source_file', 'Unknown')
                page = result['metadata'].get('page', 'N/A')
                
                context_parts.append(
                    f"[Source {i}: {source}, Page {page}]\n{result['content']}"
                )
                
                if source not in sources:
                    sources.append(source)
            
            return {
                'context': "\n\n---\n\n".join(context_parts),
                'sources': sources
            }
        
        except Exception as e:
            print(f"Sarawak Info Agent Error: {e}")
            return {
                'context': f"Error retrieving information: {str(e)}",
                'sources': []
            }


class TourGuideAgent:
    """
    Tour Guide Agent (Synthesizer)
    Uses Gemini 2.5 Flash to synthesize information into friendly responses.
    """
    
    SYSTEM_PROMPT = """You are a friendly and knowledgeable Sarawak tour guide.
Your role is to help tourists learn about Sarawak's attractions, culture, and travel tips.

Guidelines:
1. Be warm, enthusiastic, and welcoming
2. Use the provided information to answer questions accurately
3. If the information doesn't fully answer the question, acknowledge what you know and suggest where to find more details
4. Keep responses concise but informative (2-4 paragraphs)
5. Include practical tips when relevant (best times to visit, what to bring, etc.)
6. If you cannot find the details in the provided information, say so honestly

Always maintain a helpful, local expert tone.
"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        """Initialize the Tour Guide Agent."""
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=self.SYSTEM_PROMPT
        )
    
    def synthesize(self, user_query: str, context: str, sources: list) -> str:
        """
        Synthesize a response based on retrieved context.
        
        Args:
            user_query: The original user question
            context: Retrieved context from RAG
            sources: List of source documents
            
        Returns:
            Synthesized response string
        """
        prompt = f"""User Question: {user_query}

Retrieved Information:
{context}

Please provide a helpful response to the user's question based on the retrieved information.
If the information is insufficient, acknowledge what you know and suggest they contact local tourism offices for more details."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Tour Guide Agent Error: {e}")
            return f"I apologize, but I encountered an error while preparing your response. Please try again or contact Sarawak Tourism Board directly for assistance."


class TourismSwarm:
    """
    Main orchestrator for the 3-agent tourism swarm.
    Coordinates the Trip Planner, Sarawak Info, and Tour Guide agents.
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the Tourism Swarm with all agents."""
        self.trip_planner = TripPlannerAgent()
        self.info_agent = SarawakInfoAgent(data_dir=data_dir)
        self.tour_guide = TourGuideAgent()
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a user query through the agent swarm.
        
        Args:
            user_query: The user's question about Sarawak
            
        Returns:
            Dictionary with 'response', 'topic', 'sources', and 'logs' keys
        """
        logs = []
        
        # Step 1: Trip Planner extracts the topic
        logs.append("🔍 Trip Planner Agent: Analyzing your question...")
        topic = self.trip_planner.extract_topic(user_query)
        logs.append(f"📍 Identified topic: {topic}")
        
        # Step 2: Info Agent retrieves relevant information
        logs.append("📚 Sarawak Info Agent: Searching knowledge base...")
        research_result = self.info_agent.research(topic)
        logs.append(f"📄 Found {len(research_result['sources'])} relevant sources")
        
        # Step 3: Tour Guide synthesizes the response
        logs.append("🎯 Tour Guide Agent: Preparing your answer...")
        response = self.tour_guide.synthesize(
            user_query=user_query,
            context=research_result['context'],
            sources=research_result['sources']
        )
        logs.append("✅ Response ready!")
        
        return {
            'response': response,
            'topic': topic,
            'sources': research_result['sources'],
            'logs': logs
        }


# For testing
if __name__ == "__main__":
    swarm = TourismSwarm()
    result = swarm.process_query("What can I see at Bako National Park?")
    
    print("\n=== AGENT LOGS ===")
    for log in result['logs']:
        print(log)
    
    print("\n=== RESPONSE ===")
    print(result['response'])
    
    print("\n=== SOURCES ===")
    for source in result['sources']:
        print(f"- {source}")
