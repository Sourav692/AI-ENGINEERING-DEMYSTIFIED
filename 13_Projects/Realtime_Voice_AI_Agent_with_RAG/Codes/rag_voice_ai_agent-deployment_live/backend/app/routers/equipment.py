import os
import tempfile
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from loguru import logger
from bson import ObjectId
from app.services.text_extraction import TextExtractionService
from app.services.embeddings import EmbeddingService

from app.database import get_database
from app.models.equipment import Equipment
from app.models.document import Document
from app.config import settings


router = APIRouter()

@router.post("/", response_model=Equipment, status_code=status.HTTP_201_CREATED)
async def create_equipment(equipment: Equipment):
    
    """Create a new equipment"""
    db = get_database()
    
    # Check if equipment name already exists
    existing = await db.equipment.find_one({"name": equipment.name, "tenant_id": equipment.tenant_id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Equipment with this name already exists"
        )
    
    # Add timestamps
    now = datetime.utcnow()
    equipment_dict = equipment.model_dump(exclude={"id"}, exclude_none=True)
    equipment_dict["created_at"] = now
    equipment_dict["updated_at"] = now
    
    # Insert into database
    result = await db.equipment.insert_one(equipment_dict)
    # Create response with _id as string
    response_dict = equipment.model_dump(exclude={"id"}, exclude_none=True)
    response_dict["_id"] = str(result.inserted_id)
    return Equipment(**response_dict)



@router.get("/", response_model=List[Equipment], status_code=status.HTTP_200_OK)
async def get_equipment():
    """Get all equipment"""
    db = get_database()
    equipment_list = await db.equipment.find({}).to_list(length=None)
    # Convert ObjectId to string for _id field
    result = []
    for item in equipment_list:
        item_dict = dict(item)
        if '_id' in item_dict and isinstance(item_dict['_id'], ObjectId):
            item_dict['_id'] = str(item_dict['_id'])
        result.append(Equipment(**item_dict))
    return result


@router.get("/{equipment_id}", response_model=Equipment, status_code=status.HTTP_200_OK)
async def get_one_equipment(equipment_id: str):
    """Get an equipment by ID"""
    db = get_database()
    equipment = await db.equipment.find_one({"_id": ObjectId(equipment_id)})
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    equipment_dict = dict(equipment)
    if '_id' in equipment_dict and isinstance(equipment_dict['_id'], ObjectId):
        equipment_dict['_id'] = str(equipment_dict['_id'])
    return Equipment(**equipment_dict)



@router.post("/{equipment_id}/documents", status_code=status.HTTP_201_CREATED)
async def upload_equipment_documents(
    equipment_id: str,
    files: List[UploadFile] = File(...),
    description: Optional[str] = Form(None),
):
    db = get_database()

    equipment = await db.equipment.find_one({"_id": ObjectId(equipment_id)})
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    text_extractor = TextExtractionService()
    embedding_service = EmbeddingService()
    tenant_id = settings.TENANT_ID

    created_docs = []

    for file in files:
        try:
            data = await file.read()
            size = len(data)
            original_name = file.filename or "upload.bin"
            content_type = file.content_type or "application/octet-stream"

            logger.info(f"Processing file: {original_name} ({size} bytes)")

            if not text_extractor.is_supported(content_type, original_name):
                logger.warning(f"Unsupported file format: {content_type}")
                continue

            temp_file_path = None

            try:
                _, ext = os.path.splitext(original_name)
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    tmp.write(data)
                    temp_file_path = tmp.name 

                try:
                    extracted_text = text_extractor.extract_text(temp_file_path, content_type)
                except ValueError as e:
                    # Unsupported format
                    logger.warning(f"Unsupported file format: {original_name} - {str(e)}")
                    continue
                except FileNotFoundError as e:
                    logger.error(f"File not found: {original_name} - {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"Text extraction failed: {original_name} - {str(e)}")
                    continue                      

                logger.info(
                    "Text extracted from document",
                    file_name=original_name,
                    text_length=len(extracted_text or ""),
                )

                if not extracted_text or not extracted_text.strip():
                    logger.warning(f"EMPTY_DOCUMENT: No text content extracted from {original_name}")
                    continue

                chunks = embedding_service.split_text(extracted_text)
                logger.info(
                    "Document text split into chunks",
                    file_name=original_name,
                    chunk_count=len(chunks),
                )

                if not chunks:
                    raise ValueError("NO_CHUNKS: Text splitting resulted in no chunks")
                

                storage_key = f"{tenant_id}/equipment/{equipment_id}/{uuid.uuid4().hex}-{original_name}"
                now = datetime.utcnow()

                doc_dict = {
                    "equipment_id": ObjectId(equipment_id),
                    "tenant_id": tenant_id,
                    "file_name": original_name,
                    "content_type": content_type,
                    "size": size,
                    "storage_key": storage_key,
                    "uploaded_by": settings.USER_ID,
                    "description": description,
                    "document_type": "knowledge",
                    "embedding_status": "processing",
                    "created_at": now,
                    "updated_at": now,
                }

                doc_result = await db.documents_metadata.insert_one(doc_dict)
                document_id = doc_result.inserted_id
                logger.info("Document inserted with processing status", document_id=str(document_id))

                chunk_documents = []

                for index, chunk_text in enumerate(chunks):

                    try:
                        embedding_vector = embedding_service.embed_text(chunk_text)

                        chunk_doc = {
                            "document_id": document_id,
                            "equipment_id": ObjectId(equipment_id),
                            "tenant_id": tenant_id,
                            "file_name": original_name,
                            "chunk_id": str(uuid.uuid4()),
                            "chunk_index": index,
                            "text": chunk_text,
                            "embedding": embedding_vector,
                            "is_disabled": False,
                        }

                        chunk_documents.append(chunk_doc)

                        if (index + 1) % 10 == 0 or index == len(chunks) - 1:
                            logger.debug(
                                "Chunk embedding progress",
                                document_id=str(document_id),
                                chunks_embedded=index + 1,
                                total_chunks=len(chunks),
                            )

                    except Exception as e:
                        # If embedding fails for a specific chunk, log but continue
                        logger.warning(
                            "Failed to embed chunk",
                            document_id=str(document_id),
                            chunk_index=index,
                            error=str(e),
                        )
                        continue

                if not chunk_documents:
                    # Update document status to failed
                    await db.documents_metadata.update_one(
                        {"_id": document_id},
                        {
                            "$set": {
                                "embedding_status": "failed",
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
                    raise Exception("EMBEDDING_FAILED: Failed to generate embeddings for all chunks")
                
                await db[settings.DOCUMENT_CHUNKS_COLLECTION].insert_many(chunk_documents)
                logger.info(
                    "Chunks inserted into database",
                    document_id=str(document_id),
                    chunks_inserted=len(chunk_documents),
                )

                await db.documents_metadata.update_one(
                    {"_id": document_id},
                    {
                        "$set": {
                            "embedding_status": "completed",
                            "updated_at": datetime.utcnow()
                        }
                    }
                )

                logger.info(
                    "Document embedding completed",
                    document_id=str(document_id),
                    chunks_created=len(chunk_documents),
                    total_chunks=len(chunks),
                )

                doc_dict["_id"] = str(document_id)
                doc_dict["equipment_id"] = str(doc_dict["equipment_id"])
                # Convert datetime to ISO format string
                if isinstance(doc_dict.get("created_at"), datetime):
                    doc_dict["created_at"] = doc_dict["created_at"].isoformat()
                if isinstance(doc_dict.get("updated_at"), datetime):
                    doc_dict["updated_at"] = doc_dict["updated_at"].isoformat()
                created_docs.append(doc_dict)

                logger.success(f"Successfully processed {original_name}")

            finally:
                # Clean up temp file
                if temp_file_path and os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                    except Exception as e:
                        logger.warning(f"Failed to delete temp file: {e}")

        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {e}", exc_info=True)
            continue

    return {"documents": created_docs, "count": len(created_docs)}














@router.get("/{equipment_id}/documents", status_code=status.HTTP_200_OK)
async def list_equipment_documents(equipment_id: str):
    """List all documents for an equipment"""
    db = get_database()
    
    # Verify equipment exists
    equipment = await db.equipment.find_one({"_id": ObjectId(equipment_id)})
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    documents = await db.documents_metadata.find({
        "equipment_id": ObjectId(equipment_id),
        "is_disabled": {"$ne": True}
    }).to_list(length=1000)
    
    # Convert ObjectId and datetime fields to strings for JSON serialization
    serialized_documents = []
    for doc in documents:
        doc_dict = dict(doc)
        if '_id' in doc_dict and isinstance(doc_dict['_id'], ObjectId):
            doc_dict['_id'] = str(doc_dict['_id'])
        if 'equipment_id' in doc_dict and isinstance(doc_dict['equipment_id'], ObjectId):
            doc_dict['equipment_id'] = str(doc_dict['equipment_id'])
        if 'created_at' in doc_dict and isinstance(doc_dict['created_at'], datetime):
            doc_dict['created_at'] = doc_dict['created_at'].isoformat()
        if 'updated_at' in doc_dict and isinstance(doc_dict['updated_at'], datetime):
            doc_dict['updated_at'] = doc_dict['updated_at'].isoformat()
        serialized_documents.append(doc_dict)
    
    return {"documents": serialized_documents, "count": len(serialized_documents)}