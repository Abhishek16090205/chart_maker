from motor.motor_asyncio import AsyncIOMotorClient
import logging
import os
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("Missing MongoDB configuration. Please set MONGO_URI environment variable.")

client = AsyncIOMotorClient(MONGO_URI)
db = client[os.getenv("MONGO_DB", "Filter_data")]
collection_unique_values = db["unique_values"]
collection_filter = db["filters"]


async def check_mongodb_connection() -> Dict[str, str]:
    try:
        await client.admin.command('ping')
        logger.info("MongoDB connection successful")
        return {"status": "MongoDB connection successful"}
    except Exception as e:
        logger.error(f"MongoDB connection error: {e}", exc_info=True)
        raise


async def save_unique_values(metadata: Dict[str, Any]) -> Dict[str, str]:
    try:
        await collection_unique_values.insert_one(metadata)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"MongoDB error: {e}", exc_info=True)
        raise


async def get_unique_values(document_id: str):
    doc = await collection_unique_values.find_one({"id": document_id})
    if not doc:
        raise ValueError("Document not found")
    return doc.get("filters_applied")


async def save_filters(metadata: Dict[str, Any]) -> Dict[str, str]:
    try:
        await collection_filter.insert_one(metadata)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"MongoDB error: {e}", exc_info=True)
        raise


async def get_filter(filter_id: str):
    doc = await collection_filter.find_one({"filter_id": filter_id})
    if not doc:
        raise ValueError("Document not found")
    return doc.get("filters_applied")
    