from fastapi import FastAPI

from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from squared_api.database import get_session

from squared_api.routers import auth

app = FastAPI(title="Squared API")

# creates server object. Everything gets attached to this app
app = FastAPI(title="Squared API") 

@app.get("/health")
async def health(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str]:
    await session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}

app.include_router(auth.router)