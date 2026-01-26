try:
    from motor.motor_asyncio import AsyncIOMotorClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    AsyncIOMotorClient = None

from typing import Optional, Dict, Any
from datetime import datetime
from app.config import MONGODB_URI, MONGODB_DATABASE
import logging

logger = logging.getLogger(__name__)

# Global client instance
_client: Optional[Any] = None
_db = None


async def get_db():
    """Get MongoDB database instance (async)"""
    global _client, _db
    
    if not MONGODB_AVAILABLE:
        logger.warning("MongoDB (motor) not available - running in test mode")
        return None
    
    if _client is None:
        # Keep MongoDB operations snappy in local/dev when Mongo isn't running.
        # Without these timeouts, first queries can block ~30s and make the app look "hung".
        _client = AsyncIOMotorClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=2000,
            connectTimeoutMS=2000,
            socketTimeoutMS=2000,
        )
        _db = _client[MONGODB_DATABASE]
        logger.info(f"Connected to MongoDB: {MONGODB_DATABASE}")
    return _db


async def find_user(phone: str) -> Optional[Dict[str, Any]]:
    """Find user by phone number"""
    if not MONGODB_AVAILABLE:
        logger.debug(f"MongoDB unavailable - returning None for user {phone}")
        return None
    
    try:
        db = await get_db()
        if db is None:
            return None
        user = await db.users.find_one({"phone": phone})
        return user
    except Exception as e:
        logger.error(f"Error finding user {phone}: {e}")
        return None


async def upsert_case(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Insert or update case in MongoDB"""
    if not MONGODB_AVAILABLE:
        # Fallback: generate case_id and return data without saving
        if "case_id" not in case_data:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            phone = case_data.get("phone_number", "UNKNOWN")
            case_data["case_id"] = f"CASE_{timestamp}_{phone[-4:]}"
        logger.info(f"MongoDB unavailable - case generated but not saved: {case_data.get('case_id')}")
        return case_data
    
    try:
        db = await get_db()
        if db is None:
            # Same fallback as above
            if "case_id" not in case_data:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                phone = case_data.get("phone_number", "UNKNOWN")
                case_data["case_id"] = f"CASE_{timestamp}_{phone[-4:]}"
            return case_data
            
        case_id = case_data.get("case_id")
        
        if case_id:
            result = await db.cases.update_one(
                {"case_id": case_id},
                {"$set": case_data},
                upsert=True
            )
        else:
            # Generate case_id if not provided
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            phone = case_data.get("phone_number", "UNKNOWN")
            case_id = f"CASE_{timestamp}_{phone[-4:]}"
            case_data["case_id"] = case_id
            await db.cases.insert_one(case_data)
        
        logger.info(f"Case saved: {case_id}")
        return case_data
    except Exception as e:
        logger.error(f"Error saving case: {e}")
        # Still return case_data with generated ID
        if "case_id" not in case_data:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            phone = case_data.get("phone_number", "UNKNOWN")
            case_data["case_id"] = f"CASE_{timestamp}_{phone[-4:]}"
        return case_data


async def get_case_by_id(case_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve case by case_id"""
    if not MONGODB_AVAILABLE:
        logger.debug(f"MongoDB unavailable - cannot retrieve case {case_id}")
        return None
    
    try:
        db = await get_db()
        if db is None:
            return None
        case = await db.cases.find_one({"case_id": case_id})
        return case
    except Exception as e:
        logger.error(f"Error retrieving case {case_id}: {e}")
        return None


async def save_message(phone: str, message: str, role: str = "user", case_id: Optional[str] = None):
    """Save message to conversation history"""
    if not MONGODB_AVAILABLE:
        logger.debug(f"MongoDB unavailable - message not saved: {role} from {phone}")
        return
    
    try:
        db = await get_db()
        if db is None:
            return
        await db.messages.insert_one({
            "phone": phone,
            "message": message,
            "role": role,  # "user" or "assistant"
            "case_id": case_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error saving message: {e}")



async def find_doctor(phone: str) -> Optional[Dict[str, Any]]:
    """Find doctor by phone number"""
    if not MONGODB_AVAILABLE:
        return None
    try:
        db = await get_db()
        if db is None:
            return None
        # Normalize phone - remove leading + if present in DB but not in query or vice versa
        # For this dataset, phones have format +91...
        # Simple regex match or exact match
        doctor = await db.doctors.find_one({"phone_number": phone})
        return doctor
    except Exception as e:
        logger.error(f"Error finding doctor: {e}")
        return None


async def search_drugs(query: str) -> Optional[Dict[str, Any]]:
    """Search for drug by name and return profile"""
    if not query:
        return None
    
    if not MONGODB_AVAILABLE:
        return None
    
    try:
        db = await get_db()
        if db is None:
            return None
        
        # Try exact match first
        drug = await db.drugs_database.find_one({"drug_name": {"$regex":f"^{query}$", "$options": "i"}})
        
        # If not found, try text search if index exists, or regex
        if not drug:
            drug = await db.drugs_database.find_one({"drug_name": {"$regex": query, "$options": "i"}})
            
        return drug
    except Exception as e:
        logger.error(f"Error searching drug: {e}")
        return None

# Alias for backward compatibility
get_drug_profile = search_drugs


