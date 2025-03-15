from typing import List, Dict, Any, Optional
import requests
import os
import logging
import json
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_API_URL = os.environ.get("LUCID_API_URL", "http://localhost:8002")  # Default API server URL
API_KEY_HEADER = "X-API-KEY"

class LucidClient:
    """
    Client for interacting with the Lucid API server.
    """
    def __init__(self, api_url: str = None, api_key: str = None):
        """
        Initialize the Lucid client.
        
        Args:
            api_url (str, optional): The URL of the API server
            api_key (str, optional): The API key for authentication
        """
        # Get API URL from environment variable or use default
        self.api_url = api_url or os.environ.get("LUCID_API_URL", DEFAULT_API_URL)
        
        # Get API key from environment variable or use provided key
        # This is where Near AI's environment secrets feature is used
        self.api_key = api_key or os.environ.get("LUCID_API_KEY")
        
        if not self.api_key:
            logger.warning("No API key provided. Some operations may fail.")
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """
        Make a request to the API server.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            data (Dict, optional): Request data
            
        Returns:
            Dict: Response data
        """
        url = f"{self.api_url}{endpoint}"
        headers = {API_KEY_HEADER: self.api_key} if self.api_key else {}
        
        try:
            logger.info(f"Making {method} request to {url}")
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response text: {e.response.text}")
            raise
    
    def health_check(self) -> Dict:
        """
        Check the health of the API server.
        
        Returns:
            Dict: Health status
        """
        return self._make_request("GET", "/health")
    
    def create_api_key(self, user_name: str) -> Dict:
        """
        Create a new API key for the specified user.
        
        Args:
            user_name (str): The name of the user
            
        Returns:
            Dict: The created API key information
        """
        data = {"user_name": user_name}
        return self._make_request("POST", "/create_api_key", data)
    
    def get_insight(self, insight_id: int) -> Dict:
        """
        Retrieve an insight by its ID.
        
        Args:
            insight_id (int): The ID of the insight to retrieve
            
        Returns:
            Dict: The insight data
        """
        return self._make_request("GET", f"/insights/{insight_id}")
    
    def create_news_summary(self, query: str, topics: List[str] = None, timespan: str = "24h") -> str:
        """
        Create a news summary for a given query, topics, and timespan.
        
        Args:
            query (str): The search query for news
            topics (List[str], optional): List of topics to focus on
            timespan (str, optional): Time period for news (e.g., "24h", "7d")
            
        Returns:
            str: A summary of the news
        """
        try:
            # Default topics if none provided
            if topics is None or len(topics) == 0:
                topics = ["finance", "technology", "world"]
            
            # Parse timespan to match API expectations
            if timespan.endswith("h"):
                timeframe = timespan
            elif timespan.endswith("d"):
                timeframe = timespan
            else:
                timeframe = f"{timespan}h"  # Default to hours
            
            # Log the request
            logger.info(f"Creating news summary for query: '{query}', topics: {topics}, timespan: {timespan}")
            
            # Prepare the request data
            request_data = {
                "user_prompt": query,
                "timeframe": timeframe,
                "workspace_id": 1  # Default workspace ID
            }
            
            # Make the API request
            response = self._make_request("POST", "/generate_keyword_news_summary", request_data)
            
            if not response.get("success", False):
                error_message = response.get("message", "Unknown error")
                logger.error(f"Failed to generate news summary: {error_message}")
                return f"Unable to generate news summary: {error_message}"
            
            # Get the insight ID from the response
            insight_id = response.get("insight_id")
            
            if insight_id:
                try:
                    # Try to fetch the actual insight content
                    insight = self.get_insight(insight_id)
                    
                    # Extract the summary from the insight
                    summary = insight.get("content", "")
                    if summary:
                        return summary
                    
                    # If we couldn't get the content, return a message with the insight ID
                    return f"News summary generated successfully. Insight ID: {insight_id}"
                except Exception as e:
                    logger.error(f"Error fetching insight: {str(e)}")
                    # Fall back to returning a message with the insight ID
                    return f"News summary generated successfully. Insight ID: {insight_id}"
            else:
                return "News summary request submitted, but no insight ID was returned."
            
        except Exception as e:
            logger.error(f"Error creating news summary: {str(e)}")
            return f"Unable to generate news summary due to an error: {str(e)}"
    
    def create_stream_news_summary(self, stream_ids: List[int], workspace_id: int = 1, 
                                  timespan: str = "24h", user_prompt: str = None) -> str:
        """
        Create a news summary for specific streams.
        
        Args:
            stream_ids (List[int]): List of stream IDs to include
            workspace_id (int, optional): Workspace ID
            timespan (str, optional): Time period for news (e.g., "24h", "7d")
            user_prompt (str, optional): Additional user prompt
            
        Returns:
            str: A summary of the news
        """
        try:
            # Parse timespan to match API expectations
            if timespan.endswith("h"):
                timeframe = timespan
            elif timespan.endswith("d"):
                timeframe = timespan
            else:
                timeframe = f"{timespan}h"  # Default to hours
            
            # Log the request
            logger.info(f"Creating stream news summary for streams: {stream_ids}, timespan: {timespan}")
            
            # Prepare the request data
            request_data = {
                "stream_ids": stream_ids,
                "workspace_id": workspace_id,
                "timeframe": timeframe,
                "user_prompt": user_prompt
            }
            
            # Make the API request
            response = self._make_request("POST", "/generate_stream_news_summary", request_data)
            
            if not response.get("success", False):
                error_message = response.get("message", "Unknown error")
                logger.error(f"Failed to generate stream news summary: {error_message}")
                return f"Unable to generate stream news summary: {error_message}"
            
            # Get the insight ID from the response
            insight_id = response.get("insight_id")
            
            if insight_id:
                try:
                    # Try to fetch the actual insight content
                    insight = self.get_insight(insight_id)
                    
                    # Extract the summary from the insight
                    summary = insight.get("content", "")
                    if summary:
                        return summary
                    
                    # If we couldn't get the content, return a message with the insight ID
                    return f"Stream news summary generated successfully. Insight ID: {insight_id}"
                except Exception as e:
                    logger.error(f"Error fetching insight: {str(e)}")
                    # Fall back to returning a message with the insight ID
                    return f"Stream news summary generated successfully. Insight ID: {insight_id}"
            else:
                return "Stream news summary request submitted, but no insight ID was returned."
            
        except Exception as e:
            logger.error(f"Error creating stream news summary: {str(e)}")
            return f"Unable to generate stream news summary due to an error: {str(e)}"

# For backward compatibility, provide the original function
def create_news_summary(query: str, topics: List[str] = None, timespan: str = "24h") -> str:
    """
    Create a news summary for a given query, topics, and timespan.
    This is a wrapper around the LucidClient class for backward compatibility.
    
    Args:
        query (str): The search query for news
        topics (List[str], optional): List of topics to focus on
        timespan (str, optional): Time period for news (e.g., "24h", "7d")
        
    Returns:
        str: A summary of the news
    """
    client = LucidClient()
    return client.create_news_summary(query, topics, timespan)

if __name__ == "__main__":
    # Test the client
    client = LucidClient()
    
    # Check if we can connect to the API server
    try:
        health = client.health_check()
        print(f"API server health: {health}")
    except Exception as e:
        print(f"Could not connect to API server: {str(e)}")
    
    # Test the news summary function
    summary = client.create_news_summary("crypto markets", ["finance", "technology"], "48h")
    print(summary)

