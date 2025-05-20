import os
from datetime import datetime
import pytz
from logging import getLogger
from data.gc_connector import GCPostgresConnector
from logic.lichess_wrapper import LichessWrapper
from logic.stockfish_wrapper import StockfishWrapper
from ml.cluster_analysis.cluster_analysis import ClusterAnalysis
from ml.mistake_identifier.mistake_identifier import MistakeIdentifier
from ml.impact_finder.impact_finder import ImpactFinder()


class DispatcherApp:
    def __init__(self, environment: str, test_runs: int = 3):
        self.environment = environment
        self.test_runs = test_runs
        self.development_run = environment == 'dev'
        self.acceptance_run = environment == 'tst'
        self.prod_run = environment == 'prd'
        self.logger = getLogger("sf_evaluation")
        self.connection_gc: GCPostgresConnector
        self.dispatcher = None
        self.dict = {}

    def get_secret(self, key: str) -> str:
        return os.getenv(key)

    def setup_gc_connection(self):
        base_url = 'https://api.gc.engine/api'
        acceptance_url = 'https://api.gc-acc.engine/api'
        api_path = 'v1/evaluate'

        if self.acceptance_run:
            conn = self.connection_gc(
                acceptance_url,
                api_path,
                self.logger,
                self.get_secret('gc-acc-user'),
                self.get_secret('gc-acc-pwd'),
                self.development_run,
                self.acceptance_run
            )
            self.ems_dict = {"api-acceptance": conn}
        else:
            conn = self.connection_gc(
                base_url,
                api_path,
                self.logger,
                self.get_secret('gc-user'),
                self.get_secret('gc-pwd'),
                self.development_run,
                self.acceptance_run
            )
            self.dict = {"api-stockfish": conn}


    def run(self,
            name,
            start_dt_utc:datetime,
            end_dt_utc: datetime):
        evaluated_pgns = {}
        self.setup_gc_connection()
        lichess_wrapper = LichessWrapper()
        stockfish_wrapper = StockfishWrapper()
        cluster_analysis = ClusterAnalysis()
        mistake_identifier = MistakeIdentifier()
        impact_finder = ImpactFinder()

        pgns = lichess_wrapper.get_pgns_by_user(name,start_dt_utc, end_dt_utc)
        for pgn in pgns:
            evaluated_pgn = stockfish_wrapper.evaluate_game(pgn)
        evaluated_pgns[evaluated_pgn.id] = evaluated_pgn
        clusters = cluster_analysis(evaluated_pgns)
        mistakes = mistake_identifier(clusters)
        biggest_impact_mistakes = ImpactFinder(mistakes)


        



        

        
        
