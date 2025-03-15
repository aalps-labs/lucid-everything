# LucidEverything Twitter Integration

This directory contains the Twitter integration for the LucidEverything NEAR AI agent. The agent can listen for Twitter mentions and respond with news summaries.

## Components

- `twitter_client.py`: A Twitter client class that handles posting tweets and listening for mentions
- `agent.py`: The main NEAR AI agent that processes Twitter mentions and generates responses
- `twitter_listener.py`: A standalone script that can be run to continuously listen for Twitter mentions

## Setup

1. Set up the following environment variables with your Twitter API credentials:

```
TWITTER_API_KEY=your_api_key
TWITTER_API_KEY_SECRET=your_api_key_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token
```

2. Install the required dependencies:

```
pip install tweepy nearai
```

## Usage

### Using the TwitterClient directly

```python
from twitter_client import TwitterClient

# Initialize the client
twitter_client = TwitterClient()

# Post a tweet
response = twitter_client.post_tweet("Hello from LucidEverything!")
print(f"Tweet posted: {response['url']}")

# Post a tweet with media
response = twitter_client.post_tweet_with_media("Check out this image!", "path/to/image.jpg")
print(f"Tweet with media posted: {response['url']}")

# Using async methods
import asyncio

async def post_async_tweet():
    response = await twitter_client.post_tweet_async("Hello asynchronously!")
    print(f"Async tweet posted: {response['url']}")

asyncio.run(post_async_tweet())
```

### Running the Twitter Listener

The `twitter_listener.py` script can be run as a standalone service to continuously listen for Twitter mentions and respond to them:

```
python twitter_listener.py
```

This script will:
- Check for new mentions every minute
- Post a daily news summary at 8:00 AM
- Attempt to set up a streaming listener for real-time mentions (if your API access level allows it)

### Integration with NEAR AI

The `agent.py` file integrates with the NEAR AI platform to handle Twitter mentions as events. When a Twitter mention event is received, the agent will:

1. Extract the query from the mention text
2. Generate a news summary based on the query
3. Reply to the mention with the summary

## Configuration

The Twitter integration is configured in the `metadata.json` file, which specifies that the agent should be triggered by Twitter mentions to `@lucideverything`.

## Troubleshooting

- If you encounter rate limiting issues, the client will automatically wait and retry
- Check the logs for detailed error messages
- Make sure your Twitter API credentials have the necessary permissions for reading mentions and posting tweets 