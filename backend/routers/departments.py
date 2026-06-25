from fastapi import APIRouter,HTTPException
from database import get_connection

router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)

@router.get("/")
def get_all_departments():
    """
    Returns all departments with a count of doctors in each.
    Uses LEFT JOIN so departments with zero doctors still appear.
    """
    connection = get_connection()
    try:
       with connection.cursor() as cursor:
           cursor.execute("""
            SELECT
                dept.dept_id,
                dept.dept_name,
                dept.location,
                COUNT(d.doctor_id) AS doctor_count
            FROM departments dept
            LEFT JOIN doctors d ON dept.dept_id = d.dept_id
            GROUP BY dept.dept_id, dept.dept_name, dept.location
            ORDER BY dept.dept_name
            """)
           departments = cursor.fetchall()

           return {
            "status": "success",
            "total": len(departments),
            "data": departments
           }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
       connection.close()

    """"
      This endpoint returns all departments with doctor counts using a LEFT JOIN 
      so even departments without doctors are included, and GROUP BY aggregates doctors per department.
    """

@router.get("/{dept_id}")
def get_department(dept_id: int):
    connection = get_connection()
    try:
     with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM departments WHERE dept_id = %s",
            (dept_id,)
        )
        department = cursor.fetchone()

        if department is None:
            raise HTTPException(
                status_code=404,
                detail=f"Department with ID {dept_id} not found"
            )
        cursor.execute(
            "SELECT doctor_id, full_name, specialization, email, phone "
            "FROM doctors WHERE dept_id = %s",
            (dept_id,)
        )
        doctors = cursor.fetchall()
        department["doctors"] = doctors
        department["doctor_count"] = len(doctors)

        return {"status": "success", "data": department}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()