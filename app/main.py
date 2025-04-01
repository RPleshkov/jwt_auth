import logging

import uvicorn
from fastapi import FastAPI

from api import router


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


app = FastAPI(title="AUTH_PRACTICE")

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
