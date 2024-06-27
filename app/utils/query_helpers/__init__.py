import os
import json
from typing import List

from app.utils.query_helpers.base_llm import BaseLLM
from app.utils.query_helpers.prompts import query_schema, interpret_prompt, general_prompt
from app.core.protocol import Query, protocol
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.utils.setup_logger import setup_logger

# Load environment variables from .env file
load_dotenv()

logger = setup_logger("OpenAI LLM")

# OpenAI LLM class #
class OpenAILLM(BaseLLM):
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY") or ""
        if not api_key:
            raise Exception("OpenAI_API_KEY is not set.")

        self.chat = ChatOpenAI(api_key=api_key, model="gpt-4", temperature=0)
        
    def build_query_from_question(self, llm_messages: list) -> Query:
        messages = [
            SystemMessage(
                content=query_schema
            ),
        ]
        for llm_message in llm_messages:
            if llm_message["type"] == protocol.LLM_MESSAGE_TYPE_USER:
                messages.append(HumanMessage(content=llm_message["content"]))
            else:
                messages.append(AIMessage(content=llm_message["content"]))
        try:
            ai_message = self.chat.invoke(messages)
            query = json.loads(ai_message.content)
            print(query)
            return Query(
                network=protocol.NETWORK_BITCOIN,
                type=query.get("type"),
                target=query.get("target"),
                where=query.get("where"),
                limit=query.get("limit"),
                skip=query.get("skip", 0)
            )
        except Exception as e:
            logger.error(f"LlmQuery build error: {e}")
            raise Exception(protocol.LLM_ERROR_TYPE_NOT_SUPPORTED)
        
    def interpret_result(self, llm_messages: list, result: list) -> str:
        messages = [
            SystemMessage(
                content=interpret_prompt.format(result=result)
            ),
        ]
        for llm_message in llm_messages:
            if llm_message.type == protocol.LLM_MESSAGE_TYPE_USER:
                messages.append(HumanMessage(content=llm_message.content))
            else:
                messages.append(AIMessage(content=llm_message.content))
        
        try:
            ai_message = self.chat.invoke(messages)
            return ai_message.content
        except Exception as e:
            logger.error(f"LlmQuery interpret result error: {e}")
            raise Exception(protocol.LLM_ERROR_INTERPRETION_FAILED)
        
    def generate_general_response(self, llm_messages: list) -> str:
        messages = [
            SystemMessage(
                content=general_prompt
            ),
        ]
        for llm_message in llm_messages:
            if llm_message["type"] == protocol.LLM_MESSAGE_TYPE_USER:
                messages.append(HumanMessage(content=llm_message["content"]))
            else:
                messages.append(AIMessage(content=llm_message["content"]))
                
        try:
            ai_message = self.chat.invoke(messages)
            if ai_message == "not applicable questions":
                raise Exception(protocol.LLM_ERROR_NOT_APPLICAPLE_QUESTIONS)
            else:
                return ai_message.content
        except Exception as e:
            logger.error(f"LlmQuery general response error: {e}")
            raise Exception(protocol.LLM_ERROR_GENERAL_RESPONSE_FAILED)
        
    def generate_llm_query_from_query(self, query: Query) -> str:
        pass
    