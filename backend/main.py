"""
Event Management API - Main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Import domain routers
from domains.events.router import router as events_router
from domains.users.router import router as users_router
from domains.registrations.router import router as registrations_router

# Create FastAPI app
app = FastAPI(title="Event Management API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoints
@app.get("/")
def read_root():
    return {"message": "Event Management API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Register domain routers
app.include_router(events_router)
app.include_router(users_router)
app.include_router(registrations_router)

# Lambda handler
handler = Mangum(app)
