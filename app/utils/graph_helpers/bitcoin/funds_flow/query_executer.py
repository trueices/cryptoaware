
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import MemgraphGraph
from langchain_openai import ChatOpenAI

from app.utils.query_helpers import OpenAILLM
from app.utils.graph_helpers.bitcoin.funds_flow.env_fetcher import EnvFetcher
from app.core.protocol import protocol
from app.utils.setup_logger import setup_logger

logger = setup_logger("Query Controller")

# Fetch environment variables
env = EnvFetcher()

# Define a demo query
demo_query = "what is bitcoin?"
# demo_query = "Like how many deposits were made for the userID 176026497?"
# demo_query = "For the userID = 54430774 what's the sum of withdrawals and what currency is used?"
# demo_query = "What currency did userID 176026497 deposit?"
# demo_query = "Show all transactions from wallet ID <555552328d7af662ef00462b> involving Bitcoin and Ethereum where the transaction size exceeded 10 BTC or 100 ETH respectively."


def query_executer(question: str):
    """
    Demo function to execute a query
    Args:
        demoQuestion: A demo question
    Returns:
        AI response to the question
    """

    # Execute the cypher query
    try:
        graph = MemgraphGraph(url=env.db_url, username=env.db_username, password=env.db_password)
        chain = GraphCypherQAChain.from_llm(
            ChatOpenAI(api_key=env.api_key, temperature=0), graph=graph, verbose=True, model_name="gpt-4"
        )

        cypher_response = chain.run(demo_query)
        return cypher_response    
        
    # Generate a general response if the query is not
    except Exception as e:
        try:
            queryObj = OpenAILLM()
            logger.info(f"getting AI response to general question: {question}")
            general_response = queryObj.generate_general_response([{"content":question, "type": protocol.LLM_MESSAGE_TYPE_USER}])
            return general_response
        except Exception as e:
            logger.error(f"Chat creation error: {e}")

print(query_executer(demo_query))