# routers/patients.py
# Patient endpoints for CliniSight API

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_connection

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

# Pydantic model — validates data for creating a new patient
class PatientCreate(BaseModel):
    full_name: str
    dob: str
    gender: str
    phone: str
    email: str = None
    address: str = None


@router.get("/")
def get_all_patients(
    gender: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Returns patients, optionally filtered by gender and/or name search.
    Example: GET /patients/?gender=Female&search=Amy
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT
                    patient_id, full_name, gender, dob,
                    phone, email, registered_at
                FROM patients
                WHERE 1=1
            """
            params = []

            if gender is not None:
                query += " AND gender = %s"
                params.append(gender)

            if search is not None:
                query += " AND full_name LIKE %s"
                params.append(f"%{search}%")

            query += " ORDER BY registered_at DESC"

            cursor.execute(query, tuple(params))
            patients = cursor.fetchall()

        return {
            "status": "success",
            "total": len(patients),
            "data": patients
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()


@router.get("/{patient_id}")
def get_patient(patient_id: int):
    """Returns single patient by ID."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    patient_id, full_name, gender, dob,
                    phone, email, registered_at
                FROM patients
                WHERE patient_id = %s
            """, (patient_id,))
            patient = cursor.fetchone()

        if patient is None:
            raise HTTPException(
                status_code=404,
                detail=f"Patient with ID {patient_id} not found"
            )

        return {"status": "success", "data": patient}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()


@router.get("/{patient_id}/history")
def get_patient_history(patient_id: int):
    """Returns complete hospital history using GetPatientHistory stored procedure."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.callproc("GetPatientHistory", (patient_id,))
            results = cursor.fetchall()

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No history found for patient {patient_id}"
            )

        return {
            "status": "success",
            "patient_id": patient_id,
            "total_records": len(results),
            "data": results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()


@router.post("/")
def create_patient(patient: PatientCreate):
    """
    Registers a new patient.
    Request body must match PatientCreate model.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO patients (full_name, dob, gender, phone, email, address)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                patient.full_name,
                patient.dob,
                patient.gender,
                patient.phone,
                patient.email,
                patient.address
            ))
            connection.commit()
            new_id = cursor.lastrowid

        return {
            "status": "success",
            "message": "Patient registered successfully",
            "patient_id": new_id
        }
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()


class AdmitPatientRequest(BaseModel):
    full_name: str
    dob: str
    gender: str
    phone: str
    doctor_id: int
    room_number: str

@router.post("/admit")
def admit_patient(admission: AdmitPatientRequest):
    """
    Admits a new patient using the AdmitPatient stored procedure.
    This performs, as one atomic transaction:
    1. Insert patient
    2. Insert appointment
    3. Assign room (only if room is free)
    4. Create initial bill
    All four succeed together, or all are rolled back together.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.callproc("AdmitPatient", (
                admission.full_name,
                admission.dob,
                admission.gender,
                admission.phone,
                admission.doctor_id,
                admission.room_number
            ))
            connection.commit()
            results = cursor.fetchall()
            if not results:
                raise HTTPException(
                    status_code=500,
                    detail="Admission failed — no confirmation returned from procedure"
                )

        return {
            "status": "success",
            "data": results[0]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Admission failed: {str(e)}"
        )
    finally:
        connection.close()