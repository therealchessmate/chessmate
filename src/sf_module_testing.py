from engines.stockfish import Stockfish
stockfish_path = r'/Users/daanbarsukoffponiatowsky/Projects/chessmate/stockfish_bin/patched_stockfish'

sf = Stockfish(stockfish_path)

sf.set_fen_position("r1b1k2r/pp3ppp/2pp4/4p2n/P2PP3/2P2N1q/BBP2PK1/R2QR3 w kq - 0 15")
print(sf.get_evaluation())
# print(sf.get_evaluation_parameters())
print(3)