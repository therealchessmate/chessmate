from fastapi import APIRouter, Request, Query

router = APIRouter(prefix="/api")

@router.get("/evaluate")
def evaluate(request: Request, fen: str = Query(...)):
    """Evaluate position at current engine depth."""
    sf = request.app.state.stockfish
    sf.set_fen_position(fen)
    return sf.get_evaluation()


@router.get("/top-moves")
def top_moves(request: Request, fen: str, n: int = 5):
    """Get top N moves for the given position."""
    sf = request.app.state.stockfish
    sf.set_fen_position(fen)
    return sf.get_top_moves(num_top_moves=n)


@router.get("/evaluation-info")
def evaluation_info(request: Request, fen: str = Query(...)):
    """Return full evaluation info (score breakdown)."""
    sf = request.app.state.stockfish
    sf.set_fen_position(fen)
    return sf.get_evaluation_info()


@router.post("/depth")
def set_depth(request: Request, depth: int = Query(...)):
    """Update Stockfish search depth."""
    sf = request.app.state.stockfish
    sf.set_depth(depth)
    return {"message": f"Depth updated to {depth}"}
