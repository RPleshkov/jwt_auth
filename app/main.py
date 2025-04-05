import logging

import uvicorn
from api import router
from fastapi import FastAPI
from messaging import router as nats_router

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


app = FastAPI(title="AUTH_PRACTICE")

app.include_router(router)
app.include_router(nats_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
