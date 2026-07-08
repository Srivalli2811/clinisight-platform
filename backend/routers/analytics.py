# routers/analytics.py
# All analytics endpoints for CliniSight API

from fastapi import APIRouter, HTTPException, Depends
from database import get_connection
from dependencies import get_current_user
from cache import get_from_cache, set_in_cache

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/overview")
def get_hospital_overview():
    """
    Returns hospital KPI metrics.
    Powers KPI cards on dashboard overview page.
    """
    cache_key = "analytics:overview"

    cached_result = get_from_cache(cache_key)

    if cached_result is not None:
        return {
            "status": "success",
            "data": cached_result,
            "source": "cache"
        }
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
            if total_revenue is not None:
               total_revenue = float(total_revenue)

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

        
        result = {
            "total_patients": total_patients,
            "today_appointments": today_appointments,
            "total_revenue": total_revenue,
            "occupied_rooms": occupied_rooms,
            "total_doctors": total_doctors,
            "pending_bills": pending_bills
        }
        
        set_in_cache(cache_key, result, expiry_seconds=60)

        return {
            "status": "success",
            "data": result,
            "source": "database"
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
    cache_key = "analytics:revenue"

    cached_result = get_from_cache(cache_key)

    if cached_result is not None:
        return {
            "status": "success",
            "data": cached_result,
            "source": "cache"
        }
    
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.callproc("GetDepartmentRevenue")
            results = cursor.fetchall()
        set_in_cache(cache_key, results, expiry_seconds=120)

        return {
            "status": "success",
            "total_departments": len(results),
            "data": results,
            "source": "database"
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
    cache_key = "analytics:billing"

    cached_result = get_from_cache(cache_key)

    if cached_result is not None:
        return {
            "status": "success",
            "data": cached_result,
            "source": "cache"
        }
    
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.callproc("GetBillingSummary")
            results = cursor.fetchall()
        set_in_cache(cache_key, results, expiry_seconds=120)

        return {
            "status": "success",
            "data": results,
            "source": "database"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()

