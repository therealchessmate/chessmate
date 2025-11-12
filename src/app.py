from contextlib import asynccontextmanager
from fastapi import FastAPI
from engines.stockfish import Stockfish
from api.evaluate import router as evaluate_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    print("Initializing Stockfish engine...")
    app.state.stockfish = Stockfish(path="./stockfish_bin/patched_stockfish", depth=15)
    
    yield  # ⬅️ The app runs while paused here.
    
    # --- Shutdown ---
    print("Shutting down Stockfish engine...")
    app.state.stockfish.__del__()


app = FastAPI(lifespan=lifespan)
app.include_router(evaluate_router)
