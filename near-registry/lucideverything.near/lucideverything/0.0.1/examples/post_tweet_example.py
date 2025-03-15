#!/usr/bin/env python3
"""
Example script demonstrating how to use the TwitterClient to post tweets.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Add the parent directory to the path so we can import the TwitterClient
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from twitter_client import TwitterClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

async def post_tweet_examples():
    """
    Demonstrate different ways to post tweets using the TwitterClient.
    """
    try:
        # Initialize the Twitter client
        twitter_client = TwitterClient()
        
        # Example 1: Post a simple text tweet
        logger.info("Posting a simple text tweet...")
        response = twitter_client.post_tweet(f"Hello from LucidEverything! This is a test tweet posted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Tweet posted: {response['url']}")
        
        # Example 2: Post a tweet with media (if an image file is available)
        image_path = os.path.join(os.path.dirname(__file__), "example_image.jpg")
        if os.path.exists(image_path):
            logger.info("Posting a tweet with media...")
            response = twitter_client.post_tweet_with_media(
                f"Check out this image! Posted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                image_path
            )
            logger.info(f"Tweet with media posted: {response['url']}")
        else:
            logger.warning(f"Image file not found at {image_path}, skipping media tweet example")
        
        # Example 3: Post a tweet asynchronously
        logger.info("Posting a tweet asynchronously...")
        response = await twitter_client.post_tweet_async(
            f"Hello asynchronously from LucidEverything! Posted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        logger.info(f"Async tweet posted: {response['url']}")
        
        # Example 4: Post a tweet with media asynchronously (if an image file is available)
        if os.path.exists(image_path):
            logger.info("Posting a tweet with media asynchronously...")
            response = await twitter_client.post_tweet_with_media_async(
                f"Check out this image (posted asynchronously)! Posted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                image_path
            )
            logger.info(f"Async tweet with media posted: {response['url']}")
        
        logger.info("All examples completed successfully!")
    except Exception as e:
        logger.error(f"Error in post_tweet_examples: {str(e)}")

if __name__ == "__main__":
    # Run the examples
    asyncio.run(post_tweet_examples()) 