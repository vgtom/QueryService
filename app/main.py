from fastapi import FastAPI, Depends
from .api.routes import router
from .database import engine
from .models import Base
from .auth import get_current_user
from .logging_config import LoggingMiddleware
import structlog

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SQL Query Manager")

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Add authentication to all routes
app.include_router(
    router,
    prefix="/api/v1",
    dependencies=[Depends(get_current_user)]
) 