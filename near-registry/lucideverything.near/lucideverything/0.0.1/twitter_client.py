from tweepy import API, OAuthHandler, asynchronous, Stream, StreamRule
import os
import json
import logging
from typing import List, Dict, Any, Optional, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class TwitterClient:
    """
    A Twitter client that can post tweets and listen to mentions.
    Uses both synchronous and asynchronous Tweepy clients.
    """
    def __init__(self, 
                 consumer_key: str = None, 
                 consumer_secret: str = None,
                 access_token: str = None, 
                 access_token_secret: str = None,
                 bearer_token: str = None):
        """
        Initialize the Twitter client with API credentials.
        If no credentials are provided, they will be loaded from environment variables.
        """
        # Load credentials from environment variables if not provided
        self.consumer_key = consumer_key or os.getenv("TWITTER_API_KEY", "")
        self.consumer_secret = consumer_secret or os.getenv("TWITTER_API_KEY_SECRET", "")
        self.access_token = access_token or os.getenv("TWITTER_ACCESS_TOKEN", "")
        self.access_token_secret = access_token_secret or os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
        self.bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN", "")
        
        # Validate credentials
        if not all([self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret]):
            logger.warning("Twitter API credentials incomplete. Some functionality may not work.")
        
        # Initialize synchronous client (v1.1 API)
        self.auth = OAuthHandler(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret
        )
        self.auth.set_access_token(
            key=self.access_token,
            secret=self.access_token_secret
        )
        self.client = API(auth=self.auth, wait_on_rate_limit=True)
        
        # Initialize asynchronous client (v2 API)
        self.async_client = asynchronous.AsyncClient(
            bearer_token=self.bearer_token,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
        
        logger.info("Twitter client initialized")
    
    def post_tweet(self, text: str) -> Dict[str, Any]:
        """
        Post a text-only tweet using the synchronous API.
        
        Args:
            text (str): The text content of the tweet (max 280 characters)
            
        Returns:
            Dict: The response from the Twitter API
        """
        try:
            if len(text) > 280:
                logger.warning(f"Tweet text exceeds 280 characters, truncating: {len(text)}")
                text = text[:277] + "..."
                
            response = self.client.update_status(status=text)
            logger.info(f"Tweet posted successfully: {response.id}")
            return {
                "id": response.id,
                "text": response.text,
                "created_at": response.created_at.isoformat(),
                "url": f"https://twitter.com/user/status/{response.id}"
            }
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            raise
    
    def post_tweet_with_media(self, text: str, media_path: str) -> Dict[str, Any]:
        """
        Post a tweet with media attachment using the synchronous API.
        
        Args:
            text (str): The text content of the tweet
            media_path (str): Path to the media file to upload
            
        Returns:
            Dict: The response from the Twitter API
        """
        try:
            if len(text) > 280:
                logger.warning(f"Tweet text exceeds 280 characters, truncating: {len(text)}")
                text = text[:277] + "..."
                
            # Upload media
            media = self.client.media_upload(filename=media_path)
            
            # Post tweet with media
            response = self.client.update_status(
                status=text, 
                media_ids=[media.media_id]
            )
            
            logger.info(f"Tweet with media posted successfully: {response.id}")
            return {
                "id": response.id,
                "text": response.text,
                "created_at": response.created_at.isoformat(),
                "media_id": media.media_id,
                "url": f"https://twitter.com/user/status/{response.id}"
            }
        except Exception as e:
            logger.error(f"Error posting tweet with media: {str(e)}")
            raise
    
    async def post_tweet_async(self, text: str) -> Dict[str, Any]:
        """
        Post a text-only tweet using the asynchronous API.
        
        Args:
            text (str): The text content of the tweet
            
        Returns:
            Dict: The response from the Twitter API
        """
        try:
            if len(text) > 280:
                logger.warning(f"Tweet text exceeds 280 characters, truncating: {len(text)}")
                text = text[:277] + "..."
                
            response = await self.async_client.create_tweet(text=text)
            logger.info(f"Tweet posted asynchronously: {response.data.id}")
            return {
                "id": response.data.id,
                "text": text,
                "created_at": response.data.created_at.isoformat() if hasattr(response.data, 'created_at') else None,
                "url": f"https://twitter.com/user/status/{response.data.id}"
            }
        except Exception as e:
            logger.error(f"Error posting tweet asynchronously: {str(e)}")
            raise
    
    async def post_tweet_with_media_async(self, text: str, media_path: str) -> Dict[str, Any]:
        """
        Post a tweet with media attachment using a combination of sync and async APIs.
        
        Args:
            text (str): The text content of the tweet
            media_path (str): Path to the media file to upload
            
        Returns:
            Dict: The response from the Twitter API
        """
        try:
            if len(text) > 280:
                logger.warning(f"Tweet text exceeds 280 characters, truncating: {len(text)}")
                text = text[:277] + "..."
                
            # Upload media (using sync API as media upload is not available in async API)
            media = self.client.media_upload(filename=media_path)
            
            # Post tweet with media using async API
            response = await self.async_client.create_tweet(
                text=text, 
                media_ids=[media.media_id]
            )
            
            logger.info(f"Tweet with media posted asynchronously: {response.data.id}")
            return {
                "id": response.data.id,
                "text": text,
                "created_at": response.data.created_at.isoformat() if hasattr(response.data, 'created_at') else None,
                "media_id": media.media_id,
                "url": f"https://twitter.com/user/status/{response.data.id}"
            }
        except Exception as e:
            logger.error(f"Error posting tweet with media asynchronously: {str(e)}")
            raise
    
    async def setup_mention_stream(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Set up a stream to listen for mentions of the authenticated user.
        
        Args:
            callback (Callable): Function to call when a mention is received
        """
        try:
            # Get the authenticated user's username
            user_info = self.client.verify_credentials()
            username = user_info.screen_name
            
            # Set up rules for the filtered stream
            rules = [
                StreamRule(value=f"@{username}", tag="mentions")
            ]
            
            # Create a stream listener
            class MentionListener(Stream):
                def on_data(self, data):
                    tweet_data = json.loads(data)
                    callback(tweet_data)
                    return True
                
                def on_error(self, status_code):
                    logger.error(f"Stream error: {status_code}")
                    return True
            
            # Start the stream
            stream = MentionListener(
                self.consumer_key, self.consumer_secret,
                self.access_token, self.access_token_secret
            )
            stream.filter(track=[f"@{username}"], threaded=True)
            
            logger.info(f"Mention stream set up for @{username}")
            return stream
        except Exception as e:
            logger.error(f"Error setting up mention stream: {str(e)}")
            raise
    
    async def get_mentions(self, since_id: Optional[str] = None, count: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent mentions of the authenticated user.
        
        Args:
            since_id (str, optional): Only return mentions newer than this ID
            count (int): Maximum number of mentions to return
            
        Returns:
            List[Dict]: List of mention data
        """
        try:
            # Get mentions timeline
            mentions = self.client.mentions_timeline(since_id=since_id, count=count)
            
            # Format the response
            formatted_mentions = []
            for mention in mentions:
                formatted_mentions.append({
                    "id": mention.id_str,
                    "text": mention.text,
                    "created_at": mention.created_at.isoformat(),
                    "user": {
                        "id": mention.user.id_str,
                        "screen_name": mention.user.screen_name,
                        "name": mention.user.name
                    },
                    "url": f"https://twitter.com/{mention.user.screen_name}/status/{mention.id_str}"
                })
            
            logger.info(f"Retrieved {len(formatted_mentions)} mentions")
            return formatted_mentions
        except Exception as e:
            logger.error(f"Error getting mentions: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    # Initialize the client
    twitter_client = TwitterClient()
    
    # Post a tweet
    response = twitter_client.post_tweet("Hello from LucidEverything!")
    print(f"Tweet posted: {response['url']}")