from nearai.agents.environment import Environment
from lucideverything.lucid_client import create_news_summary


def run(env: Environment):
    # Your agent code here
    prompt = {"role": "system", "content": "You are a news copilot that summarizes news given a query and list of topics"}
    result = env.completion([prompt] + env.list_messages())
    env.write_file("result.html", result)
    env.write_file("result.txt", result)
    env.add_reply(result)
    env.request_user_input()

def get_daily_news_summary():
    # private_key = env.env_vars.get('LUCIDEVERYTHING_PRIVATE_KEY', 'default_value')
    create_news_summary(query="", topics=[], timespan="")
run(env)

