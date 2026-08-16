import asyncio
from typing import Any, Optional
from bson import ObjectId
from loguru import logger
from pydantic import BaseModel, Field

from app.database import get_database
from app.services.embeddings import EmbeddingService
from app.config import settings
from app.models.rag import ChunkContent, ChunkMetadata, RetrievalMetadata, RetrievalResult




embeddings_service = EmbeddingService()

class RAGService:
    def __init__(self, index_name: str = None):
        self.index_name = index_name or settings.VECTOR_INDEX_NAME
        logger.debug("RAGService initialized", index_name=self.index_name)

    async def retrieve(
        self,
        query: str,
        k: int = 5,
        equipment_id: str | None = None,
        tenant_id: str | None = None,
        extra_filters: dict[str, Any] | None = None,
    ) -> RetrievalResult:
        db = get_database()
        collection = db[settings.DOCUMENT_CHUNKS_COLLECTION]

        try:
            logger.info(f"Starting retrieval for query: '{query[:50]}...' (k={k})")

            if collection is None:
                raise ConnectionError("MongoDB collection is not initialized. Database connection failed.")
            
            try:
                logger.debug("Generating query embedding...")
                query_embedding = embeddings_service.embed_text(query)
                logger.debug("Query embedding generated successfully")
            except Exception as e:
                logger.error(f"Failed to generate query embedding: {e}")
                raise

            filters = {}

            filters["is_disabled"] = {"$ne": True}

            if equipment_id:
                try:
                    filters["equipment_id"] = ObjectId(equipment_id)
                    logger.debug(f"Added equipment_id filter: {equipment_id}")
                except Exception as e:
                    logger.warning(f"Invalid equipment_id '{equipment_id}'; skipping filter. Error: {e}")

            if tenant_id:
                filters["tenant_id"] = tenant_id
                logger.debug(f"Added tenant_id filter: {tenant_id}")

            if extra_filters:
                filters.update(extra_filters)
                logger.debug(f"Added extra filters: {extra_filters}")

            vector_query = {
                "$vectorSearch": {
                    "index": self.index_name,
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": k * 5,
                    "limit": k,
                }
            }

            if filters:
                vector_query["$vectorSearch"]["filter"] = filters

            pipeline = [
                vector_query,
                {
                    "$project": {
                        "_id": 1,
                        "chunk_id": 1,
                        "document_id": 1,
                        "file_name": 1,
                        "text": 1,
                        "chunk_index": 1,
                        "equipment_id": 1,
                        "tenant_id": 1,
                        "score": {"$meta": "vectorSearchScore"},
                    }
                }
            ]

            try:
                logger.debug(f"Executing vector search with index: {self.index_name}")
                cursor = collection.aggregate(pipeline)
                results = await cursor.to_list(length=k)
                logger.info(f"Retrieved {len(results)} results from vector search")
            except Exception as e:
                logger.error(f"Failed to execute vector search aggregation: {e}")
                raise

            chunk_data = []
            chunk_metadata = []

            try:
                for res in results:
                    chunk_data.append(ChunkContent(
                        text=res.get("text", ""),
                        file_name=res.get("file_name"),
                        score=res.get("score"),
                    ))

                    chunk_metadata.append(ChunkMetadata(
                        chunk_id=res.get("chunk_id", ""),
                        document_id=str(res.get("document_id", "")),
                        equipment_id=str(res.get("equipment_id", "")),
                        tenant_id=res.get("tenant_id"),
                        chunk_index=res.get("chunk_index", 0),
                        score=res.get("score", 0.0),
                        file_name=res.get("file_name", ""),
                    ))

                    logger.success(f"Successfully processed {len(chunk_data)} chunks")

            except Exception as e:
                logger.error(f"Failed to process search results: {e}")
                raise

            result = RetrievalResult(
                data=chunk_data,
                metadata=RetrievalMetadata(
                    query=query,
                    k=k,
                    chunks_retrieved=len(chunk_data),
                    equipment_id=equipment_id,
                    tenant_id=tenant_id,
                    chunks=chunk_metadata,
                ),
            )

            return result
        
        except Exception as e:
            logger.error(f"Error during retrieval operation: {e}")
            raise



            