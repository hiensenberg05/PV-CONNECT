# backend/app/services/inactivity_checker.py
"""
Background service to check for inactive conversations.
If a user hasn't responded in 1 hour, sends a reminder with Case ID.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

from app.db.mongo_db import mongodb_service
from app.workflows.cache_store import delete_state
from app.utils.whatsapp_utils import send_whatsapp_message


INACTIVITY_TIMEOUT_HOURS = 1
CHECK_INTERVAL_MINUTES = 5


async def get_inactive_states():
    """
    Get all conversation states that have been inactive for more than 1 hour.
    """
    inactive_states = []
    cutoff_time = datetime.now() - timedelta(hours=INACTIVITY_TIMEOUT_HOURS)

    # Query MongoDB for states with last_activity older than cutoff
    cursor = mongodb_service.db.conversation_states.find({
        "last_activity": {"$lt": cutoff_time.isoformat()},
        "case_complete": {"$ne": True},
        "inactivity_notified": {"$ne": True}
    })

    async for state in cursor:
        inactive_states.append(state)

    return inactive_states


def generate_inactivity_message(case_id: str) -> str:
    """
    Generate the inactivity reminder message.
    """
    return (
        f"⏰ *Aapka chat 1 ghante se inactive hai.*\n\n"
        f"Aapka Case ID hai:\n*{case_id}*\n\n"
        f"📋 Wapas aane aur continue karne ke liye yeh Case ID use karein.\n\n"
        f"Agar aap aur jaankari dene mein asmarth hain, toh kripya yeh Case ID apne prescribed doctor ko share karein.\n\n"
        f"Thank you! 🏥"
    )


async def mark_inactivity_notified(phone_number: str):
    """
    Mark a state as having been notified about inactivity.
    """
    await mongodb_service.db.conversation_states.update_one(
        {"phone_number": phone_number},
        {"$set": {"inactivity_notified": True}}
    )


async def check_and_notify_inactive_users():
    """
    Main function to check for inactive users and send reminders.
    """
    try:
        inactive_states = await get_inactive_states()

        for state in inactive_states:
            phone_number = state.get("phone_number")
            case_id = state.get("case_id")

            if phone_number and case_id:
                message = generate_inactivity_message(case_id)
                await send_whatsapp_message(phone_number, message)
                await mark_inactivity_notified(phone_number)

                # Clean up cache
                delete_state(phone_number)

                print(f"[Inactivity] Notified {phone_number} about case {case_id}")

    except Exception as e:
        print(f"[Inactivity] Error: {e}")


async def run_inactivity_checker():
    """
    Background task that runs continuously.
    Checks every 5 minutes for inactive conversations.
    """
    print("[Inactivity] Checker started")
    while True:
        await check_and_notify_inactive_users()
        await asyncio.sleep(CHECK_INTERVAL_MINUTES * 60)
