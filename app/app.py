from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1 import v1_router

app = FastAPI()

app.include_router(v1_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # we need everything so IoT clients can connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
