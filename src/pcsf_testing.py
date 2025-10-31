from engines.stockfish import StockfishWrapper
stockfish_path = r'/Users/daanbarsukoffponiatowsky/Projects/chessmate/stockfish_bin/patched_stockfish'


sf = StockfishWrapper(stockfish_path)
eval_breakdown = sf.get_evaluation_breakdown()

print(eval_breakdown)