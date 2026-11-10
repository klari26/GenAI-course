"""Module for querying indexed LinkedIn profile data."""

import logging
from typing import Any, Dict, Optional

from llama_index.core import VectorStoreIndex, PromptTemplate

from modules.llm_interface import create_watsonx_llm
import config

logger = logging.getLogger(__name__)

def generate_initial_facts(index: VectorStoreIndex) -> str:
    """Generates interesting facts about the person's career or education.
    
    Args:
        index: VectorStoreIndex containing the LinkedIn profile data.
        
    Returns:
        String containing interesting facts about the person.
    """

    try:
        llm = create_watsonx_llm()
        prompt_template = PromptTemplate(template=config.INITIAL_FACTS_TEMPLATE)

        query_engine = index.as_query_engine(
            streaming=False, 
            similarity_top_k=config.SIMILARITY_TOP_K,
            llm=llm,
            text_qa_template=prompt_template
        )

        query = "Provide three interesting facts about this person\'s career or education."
        generated_facts = query_engine.query(query)

        return generated_facts.response

    except Exception as e:
        error_msg = f"Error in generate_initial_facts: {e}"
        logger.error(error_msg)

        return error_msg

    
def answer_user_query(index: VectorStoreIndex, user_query: str) -> Any:
    """Answers the user's question using the vector database and the LLM.
    
    Args:
        index: VectorStoreIndex containing the LinkedIn profile data.
        user_query: The user's question.
        
    Returns:
        Response object containing the answer to the user's question.
    """
    # 1. Create a Watsonx LLM for answering questions
    # 2. Create a prompt template for question answering
    # 3. Retrieve relevant nodes from the index
    # 4. Build context string from retrieved nodes
    # 5. Create a query engine with the LLM and prompt template
    # 6. Execute the query to generate answer
    # 7. Return the answer

    try:
        llm = create_watsonx_llm(
            temperature=0.0,
            max_new_tokens=250,
            decoding_method="greedy"
        )
        prompt_template = PromptTemplate(template=config.USER_QUESTION_TEMPLATE)

        retriever = index.as_retriever(similarity_top_k=config.SIMILARITY_TOP_K)
        source_nodes = retriever.retrieve(user_query)

        context_str = '\n\n'.join([node.node.get_text() for node in source_nodes])

        query_engine = index.as_query_engine(
            streaming=False,
            similarity_top_k=config.SIMILARITY_TOP_K,
            llm=llm,
            text_qa_template=prompt_template
        )
        
        # Execute the query
        answer = query_engine.query(user_query)
        return answer
        

    except Exception as e:
        error_msg = f"Error in answer_user_query: {e}"
        logger.error(error_msg)

        return error_msg