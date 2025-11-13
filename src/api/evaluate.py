from fastapi import APIRouter, Request, Query, Response

router = APIRouter(prefix="/api")

@router.get("/evaluate")
def evaluate(request: Request, fen: str = Query(...)):
    sf = request.app.state.stockfish
    sf.set_fen_position(fen)
    return sf.get_evaluation()

@router.get("/top-moves")
def top_moves(request: Request, fen: str, n: int = 5):
    sf = request.app.state.stockfish
    sf.set_fen_position(fen)
    return sf.get_top_moves(num_top_moves=n)

@router.get("/evaluation-info")
def evaluation_info(request: Request, fen: str = Query(...)):
    sf = request.app.state.stockfish
    sf.set_fen_position(fen)
    info_text = sf.get_evaluation_info()
    return Response(content=info_text, media_type="text/plain")

@router.post("/depth")
def set_depth(request: Request, depth: int = Query(...)):
    sf = request.app.state.stockfish
    sf.set_depth(depth)
    return {"message": f"Depth updated to {depth}"}
