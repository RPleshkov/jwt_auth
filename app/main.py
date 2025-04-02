import logging

import uvicorn
from api import router
from fastapi import FastAPI

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


app = FastAPI(title="AUTH_PRACTICE")

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
