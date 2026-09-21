import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from utils.ev_tools import getUserData, fetch_lobby_links
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from system_prompt import system_prompt
load_dotenv()

tools = [getUserData,TavilySearch(),fetch_lobby_links]

# from langchain_aws import ChatBedrockConverse
# llm = ChatBedrockConverse(
#     model="mistral.mistral-large-3-675b-instruct",
#     region_name="us-east-1",
#     temperature=0.1,
# )

llm=ChatOpenAI(
    model="openai/gpt-oss-20b",
    temperature=0.1,
    reasoning=None,
    base_url=os.environ.get('OPENAI_BASE_URL'),
    api_key=os.environ.get('OPENAI_API_KEY')  
)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt    
)


def main():
    
    
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": """
                    
                    Yo man, I hear 69Lucifer69 has a sick crosshair, send me a download link for it from the api?
                    """,
                }
            ]   
        },
        # config={"recursion_limit": 2},
    )
    
    print(result['messages'][-1].content)

if __name__ == "__main__":
    main()
