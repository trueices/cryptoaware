import os
from app.utils.setup_logger import setup_logger
from neo4j import GraphDatabase

logger = setup_logger("GraphIndexer")


class GraphIndexer:
    def __init__(
        self,
        graph_db_url: str = None,
        graph_db_user: str = None,
        graph_db_password: str = None,
    ):
        if graph_db_url is None:
            self.graph_db_url = (
                os.environ.get("GRAPH_DB_URL") or "bolt://localhost:7687"
            )
        else:
            self.graph_db_url = graph_db_url

        if graph_db_user is None:
            self.graph_db_user = os.environ.get("GRAPH_DB_USER") or ""
        else:
            self.graph_db_user = graph_db_user

        if graph_db_password is None:
            self.graph_db_password = os.environ.get("GRAPH_DB_PASSWORD") or ""
        else:
            self.graph_db_password = graph_db_password

        self.driver = GraphDatabase.driver(
            self.graph_db_url,
            auth=(self.graph_db_user, self.graph_db_password),
        )

    def close(self):
        self.driver.close()

    def get_latest_block_number(self):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (t:Transaction)
                RETURN MAX(t.block_height) AS latest_block_height
                """
            )
            single_result = result.single()
            if single_result[0] is None:
               return 0

            return single_result[0]
        
    def set_min_max_block_height_cache(self, min_block_height, max_block_height):
        with self.driver.session() as session:
            # update min block height
            session.run(
                """
                MERGE (n:Cache {field: 'min_block_height'})
                SET n.value = $min_block_height
                RETURN n
                """,
                {"min_block_height": min_block_height}
            )

            # update max block height
            session.run(
                """
                MERGE (n:Cache {field: 'max_block_height'})
                SET n.value = $max_block_height
                RETURN n
                """,
                {"max_block_height": max_block_height}
            )

    def check_if_block_is_indexed(self, block_height: int) -> bool:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (t: Transaction{block_height: $block_height})
                RETURN t
                LIMIT 1;
                """,
                block_height=block_height
            )
            single_result = result.single()
            return single_result is not None

    def find_indexed_block_height_ranges(self):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (t:Transaction)
                RETURN DISTINCT t.block_height AS block_height
                ORDER BY block_height
                """,
            )
            block_heights = [record["block_height"] for record in result]

            if not block_heights:
                return []

            # Group consecutive gaps into ranges
            gap_ranges = []
            current_start = block_heights[0]
            current_end = block_heights[0]

            for height in block_heights[1:]:
                if height == current_end + 1:
                    # Consecutive gap, extend the current range
                    current_end = height
                else:
                    # Non-consecutive gap, start a new range
                    gap_ranges.append((current_start, current_end))
                    current_start = height
                    current_end = height

            # Add the last range
            gap_ranges.append((current_start, current_end))

            return gap_ranges

    def get_min_block_number(self):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (t:Transaction)
                RETURN MIN(t.block_height) AS min_block_height
                """
            )
            single_result = result.single()
            if single_result[0] is None:
               return 0

            return single_result[0]

    from decimal import getcontext

    # Set the precision high enough to handle satoshis for Bitcoin transactions
    getcontext().prec = 28

    def create_indexes(self):
        with self.driver.session() as session:
            # Fetch existing indexes
            existing_indexes = session.run("SHOW INDEX INFO")
            existing_index_set = set()
            for record in existing_indexes:
                label = record["label"]
                property = record["property"]
                index_name = f"{label}-{property}" if property else label
                if index_name:
                    existing_index_set.add(index_name)

            index_creation_statements = {
                "Cache": "CREATE INDEX ON :Cache;",
                "Transaction": "CREATE INDEX ON :Transaction;",
                "Transaction-tx_id": "CREATE INDEX ON :Transaction(tx_id);",
                "Transaction-block_height": "CREATE INDEX ON :Transaction(block_height);",
                "Transaction-out_total_amount": "CREATE INDEX ON :Transaction(out_total_amount)",
                "Address-address": "CREATE INDEX ON :Address(address);",
                "SENT-value_satoshi": "CREATE INDEX ON :SENT(value_satoshi)",
            }

            for index_name, statement in index_creation_statements.items():
                if index_name not in existing_index_set:
                    try:
                        logger.info(f"Creating index: {index_name}")
                        session.run(statement)
                    except Exception as e:
                        logger.error(f"An exception occurred while creating index {index_name}: {e}")

    # Create a graph focused on specific data
    def create_graph_focused_on_specific_data(self, normalized_data):
        transactions = normalized_data["transaction"]
        batch_step = 1

        with self.driver.session() as session:
            # Start a transaction
            transaction = session.begin_transaction()

            try:
                for i in range(0, len(transactions) - 1, batch_step):
                    tx_transactions = transactions[i : i + batch_step]

                    # Normalize the transactions for Memgraph indexing
                    tx_transactions_normalized = []

                    for tx in tx_transactions:
                        indexed_transaction = [{
                            "id": tx["transactionID"], 
                            "user_id": tx["userID"],
                            "wallet_id": tx["walletID"],
                            "exchange_id": tx["exchangeID"],
                            "counterparty_id": tx["counterpartyID"],
                            "type": tx["transaction_type"].lower(), 
                            "from": tx["source_address"], 
                            "to": tx["destination_address"],
                            "amount": tx["amount"], 
                            "currency": tx["currency"], 
                            "network": tx["network"],
                            "fee": tx["fee"],
                            "price": tx["price"],
                            "status": tx["status"],
                            "hash": tx["transaction_hash"],
                            "description": tx["transaction_description"],
                            "timestamp": tx["timestamp"],
                            }]
                        
                        tx_transactions_normalized += indexed_transaction
                    
                    # Create input edges/nodes (incoming/outcoming transactions)
                    transaction.run(
                        """
                        UNWIND $txs AS tx
                        MERGE (from:Address {address: tx.from})
                        MERGE (to:Address {address: tx.to})
                        CREATE (from)-[:Transaction { 
                            id: tx.id,
                            user_id: tx.user_id,
                            wallet_id: tx.wallet_id, 
                            exchange_id: tx.exchange_id,
                            counterparty_id: tx.counterparty_id, 
                            type: tx.type,
                            amount: tx.amount, 
                            currency: tx.currency, 
                            network: tx.network, 
                            fee: tx.fee, 
                            price: tx.price, 
                            status: tx.status, 
                            hash: tx.hash, 
                            description: tx.description,
                            timestamp: tx.timestamp
                        }]->(to)
                        """,
                        txs=tx_transactions_normalized
                    )
                    
                transaction.commit()
                logger.info(f"Success loading transactions into graph database")
                return True

            except Exception as e:
                transaction.rollback()
                logger.error(f"An exception occurred: {e}")
                return False

            finally:
                if transaction.closed() is False:
                    transaction.close()
