from agents.pv_followup_agent import run_pv_followup_agent

def run_test(title, state):
    print("\n" + "="*80)
    print("TEST:", title)
    print("="*80)

    result = run_pv_followup_agent(state)

    print("\nFOLLOWUP MESSAGE:\n")
    print(result.get("followup_msg"))

    print("\nCASE COMPLETE:", result.get("case_complete"))
    print("="*80)


# ---------- TEXT ONLY TEST ----------
# state_text = {
#     "case_id": "CASE_TEXT",
#     "user_type": "patient",
#     "current_message": "hi meri age 45 hai aur male hoon , muje headache hua tha paracetamol liya aur mera paas medical bill nai hai",
#     "prev_msgs": [],
#     "extracted_data": {},
#     "curr_doc_id": None,
#     "curr_voice_id": None,
# }

# # ---------- IMAGE TEST (mock ID) ----------
state_image = {
    "case_id": "CASE_IMAGE",
    "user_type": "patient",
    "current_message": "",
    "prev_msgs": [],
    "extracted_data": {},
    "curr_doc_id": "MOCK_IMAGE_ID",
    "curr_voice_id": None,
}

# # ---------- VOICE TEST (mock ID) ----------
# state_voice = {
#     "case_id": "CASE_VOICE",
#     "user_type": "patient",
#     "current_message": "",
#     "prev_msgs": [],
#     "extracted_data": {},
#     "curr_doc_id": None,
#     "curr_voice_id": "MOCK_VOICE_ID",
# }

# # ---------- MIXED INPUT ----------
state_mixed = {
    "case_id": "CASE_MIXED",
    "user_type": "patient",
    "current_message": "maine kal dawai li thi",
    "prev_msgs": [
        {"role": "user", "content": "hi"},
        {"role": "agent", "content": "age bataiye"}
    ],
    "extracted_data": {
        "patient_age_value": 45
    },
    "curr_doc_id": "MOCK_IMAGE_ID",
    "curr_voice_id": "MOCK_VOICE_ID",
}

state_patient_2 = {
    "case_id": "CASE_P2",
    "user_type": "patient",
    "current_message": "text hi sahi hai",
    "prev_msgs": [
        {"role": "user", "content": "maine kal dawai li thi"},
        {"role": "agent", "content": "Jo voice note aapne bheja hai, usme valid info nahi mili. Aap details text mein bhi bata sakte ho."}
    ],
    "extracted_data": {
        "patient_age_value": 45
    },
    "curr_doc_id": "MOCK_IMAGE_ID",
    "curr_voice_id": "MOCK_VOICE_ID",
}

# state_patient_3 = {
#     "case_id": "CASE_P3",
#     "user_type": "patient",
#     "current_message": "mere paas prescription nahi hai",
#     "prev_msgs": [
#         {"role": "user", "content": "maine kal dawai li thi"},
#         {"role": "agent", "content": "Patient age, gender aur kaunsi dawai li thi bata do. Prescription ho to upload kar sakte ho."}
#     ],
#     "extracted_data": {
#         "patient_age_value": 45,
#         "patient_gender": "Male"
#     },
#     "curr_doc_id": "MOCK_IMAGE_ID",
#     "curr_voice_id": "MOCK_VOICE_ID",
#     "missing": [
#         "patient_name",
#         "patient_gender",
#         "patient_age_value",
#         "patient_age_unit",

#         "reason_for_medicine",
#         "medicine_advised_by",
#         "self_medicated",
#         "past_disease_history",

#         "medicine_name",
#         "medicine_quantity_taken",
#         "medicine_dosage_form",
#         "medicine_expiry_date",
#         "medicine_start_date",
#         "medicine_stop_date",

#         "side_effect_start_date",
#         "side_effect_continuing",
#         "side_effect_stop_date",

#         "severity_no_daily_activity_effect",
#         "severity_affected_daily_activity",
#         "severity_hospitalized",
#         "severity_death",
#         "severity_other",

#         "side_effect_description",
#         "management_action_taken"
#         ]
#         "extracted_data": {
#     "patient_name": null,
#     "patient_gender": null,
#     "patient_age_value": null,
#     "patient_age_unit": null,

#     "reason_for_medicine": null,
#     "medicine_advised_by": null,
#     "self_medicated": null,
#     "past_disease_history": null,

#     "medicine_name": null,
#     "medicine_quantity_taken": null,
#     "medicine_dosage_form": null,
#     "medicine_expiry_date": null,
#     "medicine_start_date": null,
#     "medicine_stop_date": null,

#     "side_effect_start_date": null,
#     "side_effect_continuing": null,
#     "side_effect_stop_date": null,

#     "severity_no_daily_activity_effect": false,
#     "severity_affected_daily_activity": false,
#     "severity_hospitalized": false,
#     "severity_death": false,
#     "severity_other": null,

#     "side_effect_description": null,
#     "management_action_taken": null
#     }
#     }

state_doctor_1 = {
    "case_id": "CASE_D1",
    "user_type": "doctor",
    "current_message": "patient ko vomiting hui",
    "prev_msgs": [
        {"role": "user", "content": "hi"},
    ],
    "extracted_data": {
        "doctor_verified": False
    },
    "curr_doc_id": "MOCK_IMAGE_ID",
    "curr_voice_id": "MOCK_VOICE_ID",
    "extracted_data": {
        "patient_name": None,
        "patient_gender": "Male",
        "patient_age_value": 45,
        "patient_age_unit": None,

        "reason_for_medicine": None,
        "medicine_advised_by": None,
        "self_medicated": None,
        "past_disease_history": None,

        "medicine_name": None,
        "medicine_quantity_taken": None,
        "medicine_dosage_form": None,
        "medicine_expiry_date": None,
        "medicine_start_date": None,
        "medicine_stop_date": None,

        "side_effect_start_date": None,
        "side_effect_continuing": None,
        "side_effect_stop_date": None,

        "severity_no_daily_activity_effect": None,
        "severity_affected_daily_activity": None,
        "severity_hospitalized": None,
        "severity_death": None,
        "severity_other": None,

        "side_effect_description": None,
        "management_action_taken": None
    },

    "missing": [
        "patient_name",
        "patient_age_unit",

        "reason_for_medicine",
        "medicine_advised_by",
        "self_medicated",
        "past_disease_history",

        "medicine_name",
        "medicine_quantity_taken",
        "medicine_dosage_form",
        "medicine_expiry_date",
        "medicine_start_date",
        "medicine_stop_date",

        "side_effect_start_date",
        "side_effect_continuing",
        "side_effect_stop_date",

        "severity_no_daily_activity_effect",
        "severity_affected_daily_activity",
        "severity_hospitalized",
        "severity_death",
        "severity_other",

        "side_effect_description",
        "management_action_taken"
    ]

}


state_doctor_1 = {
    "case_id": "CASE_D1",
    "user_type": "doctor",
    "current_message": "patient ko vomiting hui",
    "verified_doctor": False,
    "doc_all": [],
    "voice_all": [],
    "chat_history": [
        {"role": "user", "content": "hi"},
    ],

    "curr_doc_id": "MOCK_IMAGE_ID",
    "curr_voice_id": "MOCK_VOICE_ID",

    "extracted_data": {
        # 🔹 Doctor verification
        "doctor_verified": False,

        # 🔹 Patient details
        "patient_name": None,
        "patient_gender": "Male",
        "patient_age_value": 45,
        "patient_age_unit": "Years",

        # 🔹 Medical background
        "reason_for_medicine": None,
        "medicine_advised_by": "Doctor",
        "self_medicated": False,
        "past_disease_history": None,

        # 🔹 Medicine details
        "medicine_name": None,
        "medicine_quantity_taken": None,
        "medicine_dosage_form": None,
        "medicine_expiry_date": None,
        "medicine_start_date": None,
        "medicine_stop_date": None,

        # 🔹 Side effect timeline
        "side_effect_start_date": None,
        "side_effect_continuing": None,
        "side_effect_stop_date": None,

        # 🔹 Severity
        "severity_no_daily_activity_effect": None,
        "severity_affected_daily_activity": None,
        "severity_hospitalized": None,
        "severity_death": None,
        "severity_other": None,

        # 🔹 Adverse event
        "side_effect_description": "Vomiting",
        "management_action_taken": None
    },

    "missing": [
        # 🔹 Patient
        "patient_name",

        # 🔹 Medical background
        "reason_for_medicine",
        "past_disease_history",

        # 🔹 Medicine
        "medicine_name",
        "medicine_quantity_taken",
        "medicine_dosage_form",
        "medicine_expiry_date",
        "medicine_start_date",
        "medicine_stop_date",

        # 🔹 Side effect dates
        "side_effect_start_date",
        "side_effect_continuing",
        "side_effect_stop_date",

        # 🔹 Severity
        "severity_no_daily_activity_effect",
        "severity_affected_daily_activity",
        "severity_hospitalized",
        "severity_death",
        "severity_other",

        # 🔹 Management
        "management_action_taken"
    ]
}


state_doctor_2 = {
    "case_id": "CASE_D2",
    "user_type": "doctor",
    "current_message": "suspected paracetamol induced gastritis",
    "prev_msgs": [
        {"role": "user", "content": "license uploaded"},
        {"role": "agent", "content": "Thank you, you are verified."}
    ],
    "extracted_data": {
        "doctor_verified": True
    },
    "curr_doc_id": "MOCK_IMAGE_ID",
    "curr_voice_id": "MOCK_VOICE_ID",

}

state_patient_3 = {
    "case_id": "CASE_P3",
    "user_type": "patient",
    # "current_message": "mujhe bawasir hai baitha bhi nhi jaata. Prescription nahi hai tum manually puch lo",
    "current_message": "",
    "chat_history": [
        {"role": "user", "content": "maine kal dawai li thi"},
        {
            "role": "agent",
            "content": "Patient age, gender aur kaunsi dawai li thi bata do. Prescription ho to upload kar sakte ho."
        }
    ],

    "curr_doc_id": "MOCK_IMAGE_ID",
    "curr_voice_id": "MOCK_VOICE_ID",

    "extracted_data": {
        "patient_name": None,
        "patient_gender": "Male",
        "patient_age_value": 45,
        "patient_age_unit": None,

        "reason_for_medicine": None,
        "medicine_advised_by": None,
        "self_medicated": None,
        "past_disease_history": None,

        "medicine_name": None,
        "medicine_quantity_taken": None,
        "medicine_dosage_form": None,
        "medicine_expiry_date": None,
        "medicine_start_date": None,
        "medicine_stop_date": None,

        "side_effect_start_date": None,
        "side_effect_continuing": None,
        "side_effect_stop_date": None,

        "severity_no_daily_activity_effect": None,
        "severity_affected_daily_activity": None,
        "severity_hospitalized": None,
        "severity_death": None,
        "severity_other": None,

        "side_effect_description": None,
        "management_action_taken": None
    },

    "missing": [
        "patient_name",
        "patient_age_unit",

        "reason_for_medicine",
        "medicine_advised_by",
        "self_medicated",
        "past_disease_history",

        "medicine_name",
        "medicine_quantity_taken",
        "medicine_dosage_form",
        "medicine_expiry_date",
        "medicine_start_date",
        "medicine_stop_date",

        "side_effect_start_date",
        "side_effect_continuing",
        "side_effect_stop_date",

        "severity_no_daily_activity_effect",
        "severity_affected_daily_activity",
        "severity_hospitalized",
        "severity_death",
        "severity_other",

        "side_effect_description",
        "management_action_taken"
    ]
}




if __name__ == "__main__":
    # run_test("TEXT ONLY", state_text)
    # run_test("IMAGE ONLY", state_image)
    # run_test("VOICE ONLY", state_voice)
    # run_test("MIXED INPUT", state_mixed)
    # run_test("PATIENT 2", state_patient_2)
    run_test("PATIENT 3", state_patient_3)
    # run_test("DOCTOR 1", state_doctor_1)
    # run_test("DOCTOR 2", state_doctor_2)