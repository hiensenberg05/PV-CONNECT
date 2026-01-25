"""
MongoDB Service for NOVA Pharmacovigilance
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict, List
import logging
from datetime import datetime
from app.config import settings
from app.schemas.case_schemas import CaseDocument
from app.schemas.doctor_schemas import DoctorRegistry, LicenseVerification

logger = logging.getLogger(__name__)


class MongoDBService:
    """Service for MongoDB operations"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URI)
            self.db = self.client[settings.MONGODB_DATABASE]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {settings.MONGODB_DATABASE}")
            
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    # ==================== CASE OPERATIONS ====================
    
    async def save_case(self, case: CaseDocument) -> str:
        """
        Save or update a case document
        
        Args:
            case: CaseDocument to save
            
        Returns:
            case_id of saved document
        """
        try:
            case_dict = case.model_dump()
            case_dict["updated_at"] = datetime.utcnow()
            
            result = await self.db.cases.update_one(
                {"case_id": case.case_id},
                {"$set": case_dict},
                upsert=True
            )
            
            logger.info(f"Saved case: {case.case_id}")
            return case.case_id
            
        except Exception as e:
            logger.error(f"Error saving case: {str(e)}")
            raise
    
    async def get_case(self, case_id: str) -> Optional[Dict]:
        """
        Retrieve a case by ID
        
        Args:
            case_id: Case identifier
            
        Returns:
            Case document or None
        """
        try:
            case = await self.db.cases.find_one({"case_id": case_id})
            return case
            
        except Exception as e:
            logger.error(f"Error retrieving case: {str(e)}")
            return None
    
    async def get_cases_by_phone(self, sender_phone: str) -> List[Dict]:
        """
        Get all cases for a phone number
        
        Args:
            sender_phone: Phone number
            
        Returns:
            List of case documents
        """
        try:
            cursor = self.db.cases.find({"sender_phone": sender_phone})
            cases = await cursor.to_list(length=100)
            return cases
            
        except Exception as e:
            logger.error(f"Error retrieving cases by phone: {str(e)}")
            return []
    
    async def update_case_status(
        self, 
        case_id: str, 
        status: str
    ) -> bool:
        """
        Update case status
        
        Args:
            case_id: Case identifier
            status: New status (open, escalated, closed)
            
        Returns:
            Success boolean
        """
        try:
            result = await self.db.cases.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "status": status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating case status: {str(e)}")
            return False
    
    # ==================== DOCTOR OPERATIONS ====================
    
    async def check_doctor_registry(self, phone_number: str) -> Optional[Dict]:
        """
        Check if doctor is in registry
        
        Args:
            phone_number: Doctor's phone number
            
        Returns:
            Doctor registry entry or None
        """
        try:
            doctor = await self.db.doctors.find_one({"phone_number": phone_number})
            return doctor
            
        except Exception as e:
            logger.error(f"Error checking doctor registry: {str(e)}")
            return None
    
    async def save_doctor(self, doctor: DoctorRegistry) -> bool:
        """
        Save doctor to registry
        
        Args:
            doctor: DoctorRegistry object
            
        Returns:
            Success boolean
        """
        try:
            doctor_dict = doctor.model_dump()
            
            result = await self.db.doctors.update_one(
                {"phone_number": doctor.phone_number},
                {"$set": doctor_dict},
                upsert=True
            )
            
            logger.info(f"Saved doctor: {doctor.phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving doctor: {str(e)}")
            return False
    
    async def save_license_verification(
        self, 
        verification: LicenseVerification
    ) -> bool:
        """
        Save license verification request
        
        Args:
            verification: LicenseVerification object
            
        Returns:
            Success boolean
        """
        try:
            verification_dict = verification.model_dump()
            
            result = await self.db.license_verifications.update_one(
                {"phone_number": verification.phone_number},
                {"$set": verification_dict},
                upsert=True
            )
            
            logger.info(f"Saved license verification: {verification.phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving license verification: {str(e)}")
            return False
    
    async def get_license_verification(
        self, 
        phone_number: str
    ) -> Optional[Dict]:
        """
        Get license verification status
        
        Args:
            phone_number: Doctor's phone number
            
        Returns:
            Verification document or None
        """
        try:
            verification = await self.db.license_verifications.find_one(
                {"phone_number": phone_number}
            )
            return verification
            
        except Exception as e:
            logger.error(f"Error getting license verification: {str(e)}")
            return None
    
    # ==================== MESSAGE OPERATIONS ====================
    
    async def save_message(
        self, 
        case_id: str, 
        role: str, 
        content: str
    ) -> bool:
        """
        Save a message to case history
        
        Args:
            case_id: Case identifier
            role: Message role (user/assistant/system)
            content: Message content
            
        Returns:
            Success boolean
        """
        try:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = await self.db.cases.update_one(
                {"case_id": case_id},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            return False


# Global service instance
mongodb_service = MongoDBService()
