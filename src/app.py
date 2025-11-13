from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.evaluate import router as evaluate_router
from src.engines.stockfish import Stockfish
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Stockfish engine...")
    app.state.stockfish = Stockfish(
        path="/app/stockfish_bin/patched_stockfish",  # inside container
        depth=15
    )
    yield
    print("Shutting down Stockfish engine...")
    try:
        app.state.stockfish.__del__()
    except Exception:
        pass


app = FastAPI(lifespan=lifespan)

# Include API routes
app.include_router(evaluate_router)

# Serve frontend (static HTML)
app.mount("/", StaticFiles(directory="src/static", html=True), name="static")
