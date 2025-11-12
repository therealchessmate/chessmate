from fastapi import APIRouter, Request, Query

router = APIRouter(prefix="/api")

@router.get("/evaluate")
def evaluate(request: Request, fen: str = Query(...), depth: int = Query(None)):
    sf = request.app.state.stockfish
    if depth:
        sf.set_depth(depth)
    sf.set_fen_position(fen)
    return sf.get_evaluation()

@router.get("/top-moves")
def top_moves(request: Request, fen: str, n: int = 5):
    sf = request.app.state.stockfish
    sf.set_fen_position(fen)
    return sf.get_top_moves(num_top_moves=n)
