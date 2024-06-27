from app.core.protocol import protocol, LlmMessage
from app.core.protocol import Query

from abc import ABC, abstractmethod
from typing import List

# BaseLLM class #
class BaseLLM(ABC):
    @abstractmethod
    def __init__(self) -> None:
        """
        Initialize LLM
        """
    
    @abstractmethod
    def build_query_from_question(self, llm_messages: List[LlmMessage]) -> Query:
        """
        Build query entity from natural language query
        """

    @abstractmethod
    def interpret_result(self, llm_messages: List[LlmMessage], result: list) -> str:
        """
        Interpret result into natural language based on user's query and structured result dict
        """

    @abstractmethod
    def generate_general_response(self, llm_messages: List[LlmMessage]) -> str:
        """
        Generate general response based on chat history
        """
    
    @abstractmethod
    def generate_llm_query_from_query(self, query: Query) -> str:
        """
        Generate natural language query from Query object
        """
