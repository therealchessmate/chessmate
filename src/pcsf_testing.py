from engines.stockfish import StockfishWrapper

stockfish_path = r'/Users/daanbarsukoffponiatowsky/Projects/chessmate/stockfish_bin/patched_stockfish'

sf = StockfishWrapper(stockfish_path)
print(sf.get_evaluation())


