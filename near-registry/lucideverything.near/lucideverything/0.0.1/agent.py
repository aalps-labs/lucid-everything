from nearai.agents.environment import Environment
from .lucid_client import create_news_summary, LucidClient
import asyncio
import logging
import json
import os
import secrets
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# System prompt for the news copilot
NEWS_COPILOT_PROMPT = """
You are a news copilot that summarizes news given a query and list of topics.
Your goal is to provide concise, accurate, and relevant news summaries.

Key capabilities:
- Generate comprehensive news summaries based on user queries
- Focus on specific topics when requested
- Provide time-relevant information (recent news vs historical context)
- Highlight key facts and developments
- Maintain neutrality and present multiple perspectives
- Cite sources when available
- Format information in an easily digestible way

When responding to users:
1. Be clear and concise
2. Organize information logically
3. Highlight the most important developments first
4. Provide context for complex topics
5. Avoid unnecessary jargon
"""

class NewsAgent:
    """
    News Agent class that handles interactions with the NEAR AI agent environment.
    """
    def __init__(self, env: Environment):
        """
        Initialize the News Agent.
        
        Args:
            env (Environment): The NEAR AI agent environment
        """
        self.env = env
        self.thread = self.env.get_thread()
        self.state = self.initialize_state()
        self.lucid_client = self.initialize_lucid_client()
    
    def initialize_state(self):
        """
        Initialize the agent's state, retrieving any saved data.
        
        Returns:
            dict: The agent's state
        """
        try:
            # Get the thread ID to use for state storage
            thread_id = self.thread.metadata.get("parent_id") or self.thread.id
            
            # Retrieve any saved state
            data = self.env.get_agent_data_by_key(thread_id)
            state = data.get("value") if data else {}
            
            if not state:
                # Initialize with default state
                state = {
                    "api_key": None,
                    "user_id": None,
                    "user_name": "LucidEverything User"
                }
            
            logger.info(f"Initialized state: {json.dumps(state, default=str)}")
            return state
        except Exception as e:
            logger.error(f"Error initializing state: {str(e)}")
            # Return default state on error
            return {
                "api_key": None,
                "user_id": None,
                "user_name": "LucidEverything User"
            }
    
    def save_state(self):
        """
        Save the agent's state.
        """
        try:
            thread_id = self.thread.metadata.get("parent_id") or self.thread.id
            self.env.save_agent_data(thread_id, self.state)
            logger.info(f"Saved state: {json.dumps(self.state, default=str)}")
        except Exception as e:
            logger.error(f"Error saving state: {str(e)}")
    
    def initialize_lucid_client(self):
        """
        Initialize the Lucid client with API key if available.
        
        Returns:
            LucidClient: The initialized Lucid client
        """
        api_key = self.state.get("api_key")
        
        # If we don't have an API key, create one
        if not api_key:
            api_key = self.create_api_key()
        
        # Initialize the client with the API key
        return LucidClient(api_key=api_key)
    
    def create_api_key(self):
        """
        Create a new API key for the Lucid API.
        
        Returns:
            str: The created API key
        """
        try:
            # Create a temporary client without an API key to call the create_api_key endpoint
            temp_client = LucidClient()
            
            # Call the API to create a new key
            user_name = self.state.get("user_name", "LucidEverything User")
            response = temp_client.create_api_key(user_name)
            
            # Extract the API key and user ID from the response
            api_key = response.get("api_key")
            user_id = response.get("user_id")
            
            if not api_key:
                logger.error("Failed to create API key: No API key in response")
                # Fall back to generating a mock key
                api_key = secrets.token_hex(32)
            
            # Store the API key and user ID in the state
            self.state["api_key"] = api_key
            if user_id:
                self.state["user_id"] = user_id
            self.save_state()
            
            logger.info(f"Created API key for user: {user_name}")
            
            return api_key
        except Exception as e:
            logger.error(f"Error creating API key: {str(e)}")
            # Fall back to generating a mock key
            api_key = secrets.token_hex(32)
            self.state["api_key"] = api_key
            self.save_state()
            return api_key
    
    def check_api_key(self):
        """
        Check if the API key is valid and refresh it if needed.
        
        Returns:
            bool: True if the API key is valid, False otherwise
        """
        try:
            # If we don't have an API key, create one
            if not self.state.get("api_key"):
                logger.info("No API key found, creating a new one")
                self.create_api_key()
                return True
            
            # Try to make a health check request to verify the API key
            logger.info("Checking API key validity")
            health = self.lucid_client.health_check()
            
            # If we get a successful response, the API key is valid
            if health.get("status") == "healthy":
                logger.info("API key is valid")
                return True
            
            # If we get here, the API key might not be valid, so create a new one
            logger.warning("API key might not be valid, creating a new one")
            self.create_api_key()
            
            # Reinitialize the client with the new API key
            self.lucid_client = LucidClient(api_key=self.state.get("api_key"))
            
            return True
        except Exception as e:
            logger.error(f"Error checking API key: {str(e)}")
            
            # Try to create a new API key
            logger.info("Creating a new API key after error")
            self.create_api_key()
            
            # Reinitialize the client with the new API key
            self.lucid_client = LucidClient(api_key=self.state.get("api_key"))
            
            return False
    
    def generate_news_summary(self, query: str, topics=None, timespan="24h"):
        """
        Generate a news summary based on the query, topics, and timespan.
        
        Args:
            query (str): The search query for news
            topics (list, optional): List of topics to focus on
            timespan (str, optional): Time period for news (e.g., "24h", "7d")
            
        Returns:
            str: A summary of the news
        """
        try:
            logger.info(f"Generating news summary for query: '{query}', topics: {topics}, timespan: {timespan}")
            
            # Check if the API key is valid
            self.check_api_key()
            
            # Call the create_news_summary method directly on our client instance
            # This ensures we're using the authenticated client with our API key
            summary = self.lucid_client.create_news_summary(query, topics or [], timespan)
            
            return summary
        except Exception as e:
            logger.error(f"Error generating news summary: {str(e)}")
            return f"Unable to generate news summary due to an error: {str(e)}"
    
    async def process_user_message(self, user_message):
        """
        Process a user message and generate a response.
        
        Args:
            user_message (str): The user's message
            
        Returns:
            str: The agent's response
        """
        try:
            # Extract query, topics, and timespan from the user message
            # This is a simple implementation - in a real agent, you might want to use
            # more sophisticated NLP to extract these parameters
            
            # Default values
            query = user_message
            topics = []
            timespan = "24h"
            
            # Check if the user specified topics
            if "topics:" in user_message.lower():
                parts = user_message.lower().split("topics:")
                query = parts[0].strip()
                topics_part = parts[1].strip()
                
                # Extract topics
                if "," in topics_part:
                    topics = [t.strip() for t in topics_part.split(",")]
                else:
                    topics = [topics_part.strip()]
            
            # Check if the user specified a timespan
            if "timespan:" in user_message.lower():
                parts = user_message.lower().split("timespan:")
                if "topics:" not in parts[0].lower():
                    query = parts[0].strip()
                timespan = parts[1].strip().split()[0]  # Take the first word after "timespan:"
            
            # Generate the news summary
            logger.info(f"Generating news summary with query: '{query}', topics: {topics}, timespan: {timespan}")
            
            # Add a processing message to the user
            self.env.add_message('assistant', "Processing your request... This may take a moment.")
            
            # Generate the news summary
            summary = self.generate_news_summary(query, topics, timespan)
            
            # Check if the summary indicates an error
            if summary.startswith("Unable to generate news summary"):
                # Try to provide a more helpful error message
                error_message = (
                    f"{summary}\n\n"
                    "This could be due to one of the following reasons:\n"
                    "1. The Lucid API server might be unavailable\n"
                    "2. There might be an issue with your API key\n"
                    "3. The query might be too complex or contain unsupported characters\n\n"
                    "Please try again with a simpler query, or try again later."
                )
                return error_message
            
            # Format the summary with some context
            formatted_summary = (
                f"# News Summary: {query}\n\n"
                f"**Topics:** {', '.join(topics) if topics else 'General'}\n"
                f"**Timespan:** {timespan}\n\n"
                f"{summary}\n\n"
                f"---\n"
                f"*Summary generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
            )
            
            return formatted_summary
        except Exception as e:
            logger.error(f"Error processing user message: {str(e)}")
            return (
                f"An error occurred while processing your request: {str(e)}\n\n"
                "Please try again with a different query, or contact support if the issue persists."
            )
    
    async def run(self):
        """
        Main method to run the agent.
        """
        try:
            # Check if the API key is valid at startup
            self.check_api_key()
            
            # Get the last message from the user
            messages = self.env.list_messages()
            if not messages:
                # If there are no messages, provide a welcome message
                welcome_message = (
                    "Welcome to the News Copilot! I'm here to help you stay informed with the latest news. "
                    "Ask me to summarize news on any topic, and I'll provide you with a concise summary.\n\n"
                    "You can also specify topics and a timespan for your query. For example:\n"
                    "- 'Tell me about climate change topics: environment, policy, technology'\n"
                    "- 'Latest tech news timespan: 48h'\n"
                    "- 'Updates on AI research topics: machine learning, neural networks timespan: 7d'"
                )
                self.env.add_reply(welcome_message)
                self.env.request_user_input()
                return
            
            last_message = messages[-1]['content'] if messages[-1]['role'] == 'user' else None
            if not last_message:
                self.env.add_reply("Please provide a query for news summarization.")
                self.env.request_user_input()
                return
            
            # Process the user's message
            response = await self.process_user_message(last_message)
            
            # Add the response to the agent's reply
            self.env.add_reply(response)
            
            # Save the response as HTML and text files
            self.env.write_file("result.html", response)
            self.env.write_file("result.txt", response)
            
            # Request user input for the next interaction
            self.env.request_user_input()
        except Exception as e:
            logger.error(f"Error in agent run: {str(e)}")
            self.env.add_reply(f"An error occurred: {str(e)}")
            self.env.request_user_input()

def run(env: Environment):
    """
    Main entry point for the agent.
    
    Args:
        env (Environment): The NEAR AI agent environment
    """
    try:
        # Create and run the news agent
        agent = NewsAgent(env)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(agent.run())
    except Exception as e:
        logger.error(f"Error in agent run: {str(e)}")
        env.add_reply(f"An error occurred: {str(e)}")
        env.request_user_input()

# Start the agent if this file is run directly
if __name__ == "__main__":
    from nearai.agents.environment import Environment
    env = Environment()
    run(env)

