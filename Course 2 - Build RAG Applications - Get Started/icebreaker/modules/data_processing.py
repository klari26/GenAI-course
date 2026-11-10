"""Module for processing LinkedIn profile data."""

import json
import logging
from typing import Dict, List, Any, Optional

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter

from modules.llm_interface import create_watsonx_embedding
import config

logger = logging.getLogger(__name__)

def split_profile_data(profile_data: Dict[str, Any]) -> List:
    """Splits the LinkedIn profile JSON data into nodes.
    
    Args:
        profile_data: LinkedIn profile data dictionary.
        
    Returns:
        List of document nodes.
    """
    # 1. Convert the profile data to a JSON string
    # 2. Create a Document object from the JSON string
    # 3. Split the document into nodes using SentenceSplitter
    # 4. Return the nodes

    try:
        profile_data_str = json.dumps(profile_data)
        document_obj = Document(text=profile_data_str)
        nodes = SentenceSplitter(chunk_size=config.CHUNK_SIZE).get_nodes_from_documents([document_obj])
    
        logger.info(f"Created {len(nodes)} nodes from profile data")

        return nodes
    except Exception as e:
        logger.error(f"Error in split_profile_data: {e}")

        return []


def create_vector_database(nodes: List) -> Optional[VectorStoreIndex]:
    """Stores the document chunks (nodes) in a vector database.
    
    Args:
        nodes: List of document nodes to be indexed.
        
    Returns:
        VectorStoreIndex or None if indexing fails.
    """
    try:
        embedding_model = create_watsonx_embedding()
        index = VectorStoreIndex(
            nodes=nodes,
            embed_model=embedding_model,
            show_progress=True
        )
        
        logger.info(f"Created the vector database.")

        return index
    except e as Exception:
        logger.error(f"Error in create_vector_database: {e}")
        return None  

def verify_embeddings(index: VectorStoreIndex) -> bool:
    """Verify that all nodes have been properly embedded.
    
    Args:
        index: VectorStoreIndex to verify.
        
    Returns:
        True if all embeddings are valid, False otherwise.
    """
    # 1. Get the vector store from the index
    # 2. Get the node IDs from the index
    # 3. Check if each node has a valid embedding
    # 4. Return True if all embeddings are valid, False otherwise

    try:
        vector_store = index._storage_context.vector_store
        node_ids = list(index.index_struct.nodes_dict.keys())
        missing_embeddings = False

        for node_id in node_ids:
            embedding = vector_store.get(node_id)
            if embedding is None:
                logger.warning(f"Node ID {node_id} has a None embedding")
                missing_embeddings = True
            else:
                logger.debug(f"Node ID {node_id} has a valid embedding")
        
        if not missing_embeddings:
            logger.info("All node embeddings are missing")
            return True
        else:
            return False 

    except Exception as e:
        logger.error(f"Error in verify_embeddings: {e}")
        return False  # Replace with your implementation