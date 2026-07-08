# main.py
# CliniSight FastAPI Backend — Entry Point
# Run with: uvicorn main:app --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import patients, analytics, departments,doctors,appointments,auth
from database import get_connection
from cache import is_redis_available

app = FastAPI(
    title="CliniSight API",
    description="Hospital Intelligence Platform — Backend API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(analytics.router)
app.include_router(departments.router)
app.include_router(doctors.router)
app.include_router(appointments.router)

@app.get("/")
def root():
    """Health check — verify server is running."""
    return {
        "message": "CliniSight API is running",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "Visit /docs for interactive API documentation"
    }

@app.get("/test-db")
def test_database():
    """Tests MySQL connection — verify database is reachable."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM patients")
            result = cursor.fetchone()
        return {
            "status": "connected",
            "message": "Successfully connected to MySQL CliniSight database",
            "total_patients": result["total"]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        connection.close()

@app.get("/test-redis")
def test_redis():
    """Temporary dev endpoint to verify Redis connection."""
    available = is_redis_available()

    return {
        "redis_connected": available,
        "message": "Redis is running" if available else "Redis not reachable"
    }