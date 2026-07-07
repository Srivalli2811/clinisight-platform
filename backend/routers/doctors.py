from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database import get_connection
from dependencies import get_current_user, require_admin

router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"],
    dependencies=[Depends(get_current_user)]
)

class DoctorCreate(BaseModel):
    full_name: str
    specialization: str
    dept_id: int
    email: str
    phone: str

@router.get("/")
def get_all_doctors(
    dept_id: Optional[int] = None,
    specialization: Optional[str] = None
):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT
                    d.doctor_id,
                    d.full_name,
                    d.specialization,
                    d.dept_id,
                    dept.dept_name,
                    d.email,
                    d.phone
                FROM doctors d
                JOIN departments dept
                    ON d.dept_id = dept.dept_id
                WHERE 1=1
            """
            params = []
            if dept_id is not None:
                query += " AND d.dept_id = %s"
                params.append(dept_id)

            if specialization is not None:
                query += " AND d.specialization = %s"
                params.append(specialization)
            query += " ORDER BY d.full_name"

            cursor.execute(query, tuple(params))
            doctors = cursor.fetchall()
            return {
                "status": "success",
                "total": len(doctors),
                "data": doctors
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()


@router.get("/{doctor_id}")
def get_doctor(doctor_id: int):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    d.doctor_id,
                    d.full_name,
                    d.specialization,
                    d.dept_id,
                    dept.dept_name,
                    d.email,
                    d.phone
                FROM doctors d
                JOIN departments dept
                    ON d.dept_id = dept.dept_id
                WHERE d.doctor_id = %s
            """, (doctor_id,))

            doctor = cursor.fetchone()
            if doctor is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Doctor with ID {doctor_id} not found"
                )

            return {"status": "success", "data": doctor}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()


@router.post("/")
def create_doctor(
    doctor: DoctorCreate,
    current_user: dict = Depends(require_admin)
):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO doctors
                (full_name, specialization, dept_id, email, phone)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                doctor.full_name,
                doctor.specialization,
                doctor.dept_id,
                doctor.email,
                doctor.phone
            ))
            connection.commit()
            new_id = cursor.lastrowid
            return {
                "status": "success",
                "message": "Doctor added successfully",
                "doctor_id": new_id
            }
        
    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    finally:
        connection.close()