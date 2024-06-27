import signal
import time

from app.utils.setup_logger import setup_logger
from app.utils.setup_logger import logger_extra_data

from app.utils.graph_helpers.graph_node_normalizer import normalize_data_from_user_input
from graph_indexer import GraphIndexer


# Global flag to signal shutdown
shutdown_flag = False
logger = setup_logger("Indexer")

# Shutdown handler to gracefully shutdown the indexer
def shutdown_handler():
    global shutdown_flag
    logger.info(
        "Shutdown signal received. Waiting for current indexing to complete before shutting down."
    )
    shutdown_flag = True

# Index the specific data into the graph database
def index(_graph_indexer):
    normalized_data = normalize_data_from_user_input()
    start_time = time.time()
    is_success_in_memory_graph = _graph_indexer.create_graph_focused_on_specific_data(normalized_data)
    end_time = time.time()
    time_taken = end_time - start_time
    formatted_time_taken = "{:6.2f}".format(time_taken)

    if time_taken > 0:
        logger.info("Processing transactions", extra = logger_extra_data(time_taken = formatted_time_taken))
    else:
        logger.info("Processed transactions in 0.00 seconds (  Inf TPS).")

    return is_success_in_memory_graph        
            
# Index the raw data from the blockchain into the graph database
def do_indexing(_graph_indexer):
    global shutdown_flag

    while not shutdown_flag:
        success = index(_graph_indexer)        
        if success:
            logger.info(f"Success to index block.")
        else:
            logger.error(f"Failed to index block.")
            time.sleep(30)


# Register the shutdown handler for SIGINT and SIGTERM
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    graph_indexer = GraphIndexer()
        
    logger.info("Creating indexes...")
    # graph_indexer.create_indexes()

    # Start indexing from the user-specified transaction data
    index(graph_indexer)

    # Close the connections
    graph_indexer.close()
    logger.info("Indexer stopped")
