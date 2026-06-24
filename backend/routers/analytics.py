# routers/analytics.py
# All analytics endpoints for CliniSight API

from fastapi import APIRouter, HTTPException
from database import get_connection

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/overview")
def get_hospital_overview():
    """
    Returns hospital KPI metrics.
    Powers KPI cards on dashboard overview page.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM patients")
            total_patients = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) as total FROM appointments
                WHERE DATE(appointment_date) = CURDATE()
            """)
            today_appointments = cursor.fetchone()["total"]

            cursor.execute("SELECT ROUND(SUM(cost), 2) as total FROM treatments")
            total_revenue = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) as total FROM rooms
                WHERE is_occupied = TRUE
            """)
            occupied_rooms = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) as total FROM doctors")
            total_doctors = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) as total FROM bills
                WHERE payment_status = 'Pending'
            """)
            pending_bills = cursor.fetchone()["total"]

        return {
            "status": "success",
            "data": {
                "total_patients": total_patients,
                "today_appointments": today_appointments,
                "total_revenue": total_revenue,
                "occupied_rooms": occupied_rooms,
                "total_doctors": total_doctors,
                "pending_bills": pending_bills
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()


@router.get("/revenue")
def get_department_revenue():
    """
    Returns revenue by department using stored procedure.
    Powers revenue bar chart on dashboard.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.callproc("GetDepartmentRevenue")
            results = cursor.fetchall()
        return {
            "status": "success",
            "total_departments": len(results),
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()


@router.get("/billing")
def get_billing_summary():
    """
    Returns billing summary using stored procedure.
    Powers billing KPI cards on dashboard.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.callproc("GetBillingSummary")
            results = cursor.fetchall()
        return {
            "status": "success",
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()

