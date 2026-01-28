import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.schemas.case import Case
from app.schemas.user import User

logger = logging.getLogger(__name__)


class MongoDBService:
    """
    MongoDB service for PV-CONNECT.

    Responsibilities:
    - Store FINAL case data (not conversation state)
    - Store message history (optional)
    - Store doctor/user registry info

    NOT responsible for:
    - Workflow logic
    - Question ordering
    - State decisions
    """

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

    # --------------------------------------------------
    # CONNECTION
    # --------------------------------------------------

    async def connect(self):
        self.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            uuidRepresentation="standard"
        )
        self.db = self.client[settings.MONGODB_DATABASE]

        # Ping
        await self.client.admin.command("ping")
        logger.info("MongoDB connected")

    async def disconnect(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB disconnected")

    # --------------------------------------------------
    # CASE OPERATIONS
    # --------------------------------------------------

    async def save_case(self, case: Case) -> str:
        """
        Save or update a PvPI case.
        """
        data = case.model_dump()
        data["case_id"] = str(case.case_id)
        data["updated_at"] = datetime.utcnow()

        await self.db.cases.update_one(
            {"case_id": str(case.case_id)},
            {"$set": data},
            upsert=True
        )

        logger.info(f"Case saved: {case.case_id}")
        return str(case.case_id)

    async def get_case(self, case_id: UUID) -> Optional[Dict[str, Any]]:
        return await self.db.cases.find_one(
            {"case_id": str(case_id)}
        )

    async def get_cases_by_phone(self, phone_number: str) -> List[Dict[str, Any]]:
        cursor = self.db.cases.find({"patient_phone": phone_number})
        return await cursor.to_list(length=50)

    async def update_case_status(self, case_id: UUID, is_complete: bool) -> bool:
        result = await self.db.cases.update_one(
            {"case_id": str(case_id)},
            {
                "$set": {
                    "is_complete": is_complete,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0

    # --------------------------------------------------
    # MESSAGE HISTORY (OPTIONAL)
    # --------------------------------------------------

    async def save_message(
        self,
        case_id: UUID,
        role: str,
        content: str
    ) -> bool:
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }

        result = await self.db.cases.update_one(
            {"case_id": str(case_id)},
            {"$push": {"messages": message}}
        )
        return result.modified_count > 0

    # --------------------------------------------------
    # USER / DOCTOR REGISTRY
    # --------------------------------------------------

    async def get_user(self, phone_number: str) -> Optional[Dict[str, Any]]:
        return await self.db.users.find_one(
            {"phone_number": phone_number}
        )

    async def save_user(self, user: User) -> bool:
        await self.db.users.update_one(
            {"phone_number": user.phone_number},
            {"$set": user.model_dump()},
            upsert=True
        )
        return True


# Singleton
mongodb_service = MongoDBService()
