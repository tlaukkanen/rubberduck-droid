"""
Long-term memory tool for DroidAgent using Azure Cosmos DB.
Stores and retrieves facts, traits, and conversation context.
"""

import os
import uuid
import json
from datetime import datetime
from typing import List, Optional
from azure.cosmos import CosmosClient, PartitionKey
from pydantic import BaseModel, Field

from langchain.tools import StructuredTool
class MemoryToolInput(BaseModel):
    action: str = Field(..., description="Action to perform: store or retrieve")
    memory_type: Optional[str] = Field(None, description="Type of memory: fact, trait, preference, context")
    content: Optional[str] = Field(None, description="The actual memory content")
    category: Optional[str] = Field(None, description="Category or topic of the memory")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for searching")
    confidence: Optional[float] = Field(1.0, description="Confidence level of the memory (0-1)")
    query: Optional[str] = Field(None, description="Search query for retrieving memories")
    limit: Optional[int] = Field(10, description="Number of memories to retrieve")


class MemoryItem(BaseModel):
    """Represents a memory item stored in Cosmos DB."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(description="Identifier for the user")
    memory_type: str = Field(
        description="Type of memory: fact, trait, preference, context"
    )
    content: str = Field(description="The actual memory content")
    category: str = Field(description="Category or topic of the memory")
    confidence: float = Field(
        default=1.0, description="Confidence level of the memory (0-1)"
    )
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    tags: List[str] = Field(default_factory=list, description="Tags for searching")


class LongTermMemoryManager:
    """Manager for long-term memory using Azure Cosmos DB."""

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id

        # Initialize Cosmos DB client
        endpoint = os.environ.get("COSMOS_ENDPOINT")
        key = os.environ.get("COSMOS_KEY")

        if not endpoint or not key:
            raise ValueError(
                "COSMOS_ENDPOINT and COSMOS_KEY environment variables must be set"
            )

        self.client = CosmosClient(endpoint, key)
        self.database_name = "droid_memory"
        self.container_name = "memories"

        # Initialize database and container
        self._initialize_cosmos_db()

    def _initialize_cosmos_db(self):
        """Initialize the Cosmos DB database and container if they don't exist."""
        self.database = self.client.create_database_if_not_exists(id=self.database_name)
        self.container = self.database.create_container_if_not_exists(
            id=self.container_name,
            partition_key=PartitionKey(path="/user_id"),
            offer_throughput=400,
        )

    def store_memory(
        self,
        memory_type: str,
        content: str,
        category: str,
        tags: Optional[List[str]] = None,
        confidence: float = 1.0,
    ) -> str:
        """Store a new memory item."""
        memory_item = MemoryItem(
            user_id=self.user_id,
            memory_type=memory_type,
            content=content,
            category=category,
            tags=tags or [],
            confidence=confidence,
        )

        self.container.create_item(body=memory_item.dict())
        return f"Memory stored successfully with ID: {memory_item.id}"

    def remove_memory(self, memory_id: str) -> str:
        """Remove a memory item by its ID."""
        try:
            self.container.delete_item(item=memory_id, partition_key=self.user_id)
            return f"Memory with ID {memory_id} deleted successfully."
        except Exception as e:
            return f"Error deleting memory with ID {memory_id}: {str(e)}"

    def retrieve_memories(
        self,
        query: str,
        memory_type: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> str:
        """Retrieve memories based on query."""
        # Build query conditions
        conditions = [f"c.user_id = '{self.user_id}'"]

        if memory_type:
            conditions.append(f"c.memory_type = '{memory_type}'")

        if category:
            conditions.append(f"c.category = '{category}'")

        # Add text search conditions
        query_words = query.lower().split()
        text_conditions = []
        for word in query_words:
            # Escape single quotes for SQL
            escaped_word = word.replace("'", "''")
            text_conditions.append(f"CONTAINS(LOWER(c.content), '{escaped_word}')")

        if text_conditions:
            conditions.append(f"({' OR '.join(text_conditions)})")

        sql_query = f"""
        SELECT * FROM c 
        WHERE {" AND ".join(conditions)}
        ORDER BY c.timestamp DESC
        OFFSET 0 LIMIT {limit}
        """

        items = list(
            self.container.query_items(
                query=sql_query, enable_cross_partition_query=True
            )
        )

        if not items:
            return "No memories found matching the query."

        result = f"Found {len(items)} memories:\n"
        for item in items:
            result += f"- ID: {item['id']} | [{item['memory_type']}] {item['content']} (Category: {item['category']})\n"

        return result


def create_memory_tool(user_id: str = "default_user") -> StructuredTool:
    """Factory function to create a long-term memory tool."""



    def memory_tool_func(*args, **kwargs) -> str:
        """Handle memory tool operations. Accepts both positional and keyword arguments for compatibility with StructuredTool."""
        try:
            memory_manager = LongTermMemoryManager(user_id)

            # If called with a single positional argument (string or dict)
            if args and not kwargs:
                tool_input = args[0]
                if isinstance(tool_input, dict):
                    params = tool_input
                elif isinstance(tool_input, str):
                    try:
                        params = json.loads(tool_input)
                        action = params.get("action", "").lower()
                    except (json.JSONDecodeError, TypeError):
                        # Simple text input - assume it's a retrieve operation
                        return memory_manager.retrieve_memories(tool_input)
                else:
                    return "Invalid input type."
            # If called with keyword arguments (StructuredTool style)
            else:
                params = kwargs

            action = params.get("action", "").lower() if isinstance(params, dict) else ""

            if action == "store":
                return memory_manager.store_memory(
                    memory_type=params.get("memory_type", "fact"),
                    content=params.get("content", ""),
                    category=params.get("category", "general"),
                    tags=params.get("tags", []),
                    confidence=params.get("confidence", 1.0),
                )
            elif action == "retrieve":
                return memory_manager.retrieve_memories(
                    query=params.get("query", ""),
                    memory_type=params.get("memory_type"),
                    category=params.get("category"),
                    limit=params.get("limit", 10),
                )
            elif action == "remove":
                memory_id = params.get("memory_id")
                if not memory_id:
                    return "Missing 'memory_id' for remove action."
                return memory_manager.remove_memory(memory_id)
            elif args and not kwargs and isinstance(args[0], str):
                # Simple string input, treat as retrieve
                return memory_manager.retrieve_memories(args[0])
            else:
                return f"Unknown action: {action}. Available actions: store, retrieve, remove"

        except (ValueError, TypeError, ConnectionError) as e:
            return f"Error in memory tool: {str(e)}"

    return StructuredTool(
        name="long_term_memory",
        description="""Use this tool to store, retrieve, and remove long-term memories about users, facts, and conversation context.

For storing memories, use JSON format: {"action": "store", "memory_type": "fact|trait|preference|context", "content": "memory content", "category": "category name"}

For retrieving memories, use JSON format: {"action": "retrieve", "query": "search query"} or just provide the search query directly.

For removing a memory, use JSON format: {"action": "remove", "memory_id": "<memory_id>"}

Examples:
- Store: {"action": "store", "memory_type": "preference", "content": "User likes Python programming", "category": "programming"}
- Retrieve: {"action": "retrieve", "query": "programming preferences"}
- Simple retrieve: "programming preferences"
- Remove: {"action": "remove", "memory_id": "<memory_id>"}

Memory types:
- fact: Factual information about the user
- trait: Personal characteristics and traits
- preference: User preferences for various topics
- context: Conversation context and technical details
""",
        func=memory_tool_func,
        args_schema=MemoryToolInput,
    )
