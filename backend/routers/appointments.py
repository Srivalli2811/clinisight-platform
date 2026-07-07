from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database import get_connection
from dependencies import get_current_user

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
    dependencies=[Depends(get_current_user)]
)

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: str
    status: str = "Scheduled"
    notes: str = None

@router.get("/")
def get_all_appointments(
    status: Optional[str] = None,
    doctor_id: Optional[int] = None
):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT
                    a.appointment_id,
                    a.appointment_date,
                    a.status,

                    p.patient_id,
                    p.full_name AS patient_name,

                    d.doctor_id,
                    d.full_name AS doctor_name

                FROM appointments a

                JOIN patients p
                    ON a.patient_id = p.patient_id

                JOIN doctors d
                    ON a.doctor_id = d.doctor_id

                WHERE 1=1
            """

            params = []

            if status is not None:
                query += " AND a.status = %s"
                params.append(status)

            if doctor_id is not None:
                query += " AND a.doctor_id = %s"
                params.append(doctor_id)

            query += " ORDER BY a.appointment_date DESC"
            cursor.execute(query, tuple(params))
            appointments = cursor.fetchall()

        return {
            "status": "success",
            "total": len(appointments),
            "data": appointments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    finally:
        connection.close()

@router.get("/{appointment_id}")
def get_appointment(appointment_id: int):
    """Returns single appointment, joined with patient and doctor names."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    a.appointment_id, a.appointment_date, a.status, a.notes,
                    p.patient_id, p.full_name AS patient_name,
                    d.doctor_id, d.full_name AS doctor_name
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN doctors d ON a.doctor_id = d.doctor_id
                WHERE a.appointment_id = %s
            """, (appointment_id,))

            appointment = cursor.fetchone()
            if appointment is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Appointment with ID {appointment_id} not found"
                )

            return {
                "status": "success",
                "data": appointment
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()


@router.post("/")
def create_appointment(appointment: AppointmentCreate):
    """Books a new appointment with a plain INSERT (no stored procedure needed)."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO appointments
                    (patient_id, doctor_id, appointment_date, status, notes)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                appointment.patient_id,
                appointment.doctor_id,
                appointment.appointment_date,
                appointment.status,
                appointment.notes
            ))

            connection.commit()
            new_id = cursor.lastrowid

            return {
                "status": "success",
                "message": "Appointment booked successfully",
                "appointment_id": new_id
            }
        
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()