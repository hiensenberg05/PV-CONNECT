# Doctor Registry - Mobile Number Matching

## ✅ Already Implemented and Working!

The system **already uses mobile number** to check if a doctor is verified. Here's exactly how it works:

## How It Works

### 1. Doctor Sends First Message
```
Doctor sends: "Reporting ADR: Patient on metformin 500mg BID"
From phone: +1234567890
```

### 2. System Detects Doctor
```python
# user_type_detection_node classifies as "doctor"
state["sender_type"] = "doctor"
```

### 3. Registry Check by Mobile Number
```python
# In graph.py - doctor_registry_check_node (Line 83-108)
async def doctor_registry_check_node(state: NovaState):
    phone = state.get("sender_phone")  # ← Gets mobile number
    
    # Check MongoDB using mobile number
    doctor = await mongodb_service.check_doctor_registry(phone)
    
    if doctor and doctor.get("verified"):
        # Doctor is verified!
        state["verified_doctor"] = True
        state["license_status"] = "approved"
        # → Goes directly to doctor_case_intake
    else:
        # Doctor not found or not verified
        state["verified_doctor"] = False
        state["license_status"] = "pending"
        # → Asks for license upload
```

### 4. MongoDB Lookup
```python
# In mongodb_service.py - check_doctor_registry (Line 143-158)
async def check_doctor_registry(self, phone_number: str):
    """Check if doctor is in registry by phone number"""
    
    # Query MongoDB doctors collection
    doctor = await self.db.doctors.find_one({
        "phone_number": phone_number  # ← Mobile number is the key
    })
    
    return doctor  # Returns doctor record or None
```

## Database Structure

### Doctors Collection
```javascript
{
  "_id": ObjectId("..."),
  "phone_number": "+1234567890",  // ← Primary lookup key
  "full_name": "Dr. Jane Smith",
  "license_number": "MD123456",
  "specialty": "Internal Medicine",
  "institution": "City Hospital",
  "country": "US",
  "verified": true,  // ← Verification status
  "verification_date": ISODate("2024-01-15"),
  "verified_by": "admin@nova.com",
  "registered_at": ISODate("2024-01-10"),
  "last_active": ISODate("2024-01-20")
}
```

## Workflow Flow

```
Doctor Message Received
    ↓
Language Detection
    ↓
User Type Detection → "doctor"
    ↓
doctor_registry_check_node
    ├─ Query: db.doctors.find_one({"phone_number": "+1234567890"})
    ├─ Found & verified=true?
    │   ├─ YES → state["verified_doctor"] = True
    │   │         → Go to doctor_case_intake (skip license request)
    │   │
    │   └─ NO → state["verified_doctor"] = False
    │            → Go to license_upload_request
    │            → Then proceed to doctor_case_intake
    ↓
Continue with case intake...
```

## Adding Doctors to Registry

### Method 1: Direct MongoDB Insert
```javascript
// In MongoDB shell or Compass
db.doctors.insertOne({
  "phone_number": "+1234567890",
  "full_name": "Dr. Jane Smith",
  "license_number": "MD123456",
  "specialty": "Internal Medicine",
  "verified": true,
  "verification_date": new Date(),
  "registered_at": new Date()
})
```

### Method 2: Using the Service
```python
# In Python
from app.services.mongodb_service import mongodb_service
from app.schemas.doctor_schemas import DoctorRegistry
from datetime import datetime

await mongodb_service.connect()

doctor = DoctorRegistry(
    phone_number="+1234567890",
    full_name="Dr. Jane Smith",
    license_number="MD123456",
    specialty="Internal Medicine",
    institution="City Hospital",
    country="US",
    verified=True,
    verification_date=datetime.utcnow()
)

await mongodb_service.save_doctor(doctor)
```

### Method 3: API Endpoint (Future Enhancement)
```python
# Could add to main.py
@app.post("/api/admin/register-doctor")
async def register_doctor(doctor: DoctorRegistry):
    await mongodb_service.save_doctor(doctor)
    return {"status": "registered", "phone": doctor.phone_number}
```

## Testing the Registry Check

### Test 1: Verified Doctor
```python
# 1. Add doctor to database
from app.services.mongodb_service import mongodb_service
from app.schemas.doctor_schemas import DoctorRegistry

await mongodb_service.connect()

doctor = DoctorRegistry(
    phone_number="+1987654321",
    full_name="Dr. Test Doctor",
    license_number="TEST123",
    verified=True
)

await mongodb_service.save_doctor(doctor)

# 2. Send message from that number
curl -X POST http://localhost:8000/api/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Reporting ADR: Patient developed rash",
    "sender_phone": "+1987654321"
  }'

# Expected: Should skip license request, go straight to case intake
```

### Test 2: Unverified Doctor
```python
# Send message from unknown number
curl -X POST http://localhost:8000/api/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Reporting ADR: Patient developed rash",
    "sender_phone": "+9999999999"
  }'

# Expected: Should ask for license upload
```

## Advantages of Mobile Number Matching

✅ **Fast Lookup** - Single database query by indexed field
✅ **No Login Required** - Seamless authentication
✅ **WhatsApp Ready** - Phone number is already available
✅ **Unique Identifier** - One phone = one doctor
✅ **Easy Management** - Simple to add/remove doctors

## Security Considerations

### Current Implementation
- ✅ Phone number as primary key
- ✅ Verification status flag
- ✅ License number stored
- ✅ Verification date tracked

### Future Enhancements (Optional)
- 🔄 Add phone number verification (OTP)
- 🔄 Add session management
- 🔄 Add rate limiting per phone number
- 🔄 Add audit log for doctor actions

## Summary

**✅ Mobile number matching is ALREADY WORKING!**

The system:
1. ✅ Receives doctor's phone number from message
2. ✅ Queries MongoDB: `db.doctors.find_one({"phone_number": phone})`
3. ✅ Checks `verified` status
4. ✅ Routes accordingly:
   - Verified → Direct to case intake
   - Not verified → Request license first

**No changes needed - it's already the best approach!** 🎉
