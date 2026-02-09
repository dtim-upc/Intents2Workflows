from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from cleanup import cleanup_old_sessions
import asyncio

from routes import data_product, intent, workflow, middleware
from database.database import init_db

import uvicorn

# --- Lifespan context manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the cleanup loop in the background
    async def cleanup_loop():
        while True:
            try:
                print("[Cleanup] Running daily cleanup...")
                cleanup_old_sessions()
            except Exception as e:
                print(f"[Cleanup] Error: {e}")
            # Wait 24 hours
            await asyncio.sleep(60 * 60 * 24)

    task = asyncio.create_task(cleanup_loop())
    yield  # App runs here
    # Cancel task on shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

# Initialize Database
init_db()

app.add_middleware(middleware.SessionMiddleware)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(data_product.router)
app.include_router(intent.router)
app.include_router(workflow.router)

root_app = FastAPI()
root_app.mount("/intent2Workflow-backend", app)

if __name__ == "__main__":
    uvicorn.run(root_app, host="0.0.0.0", port=9001)
