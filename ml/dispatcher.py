import os
from datetime import datetime
import pytz
from logging import getLogger
from data.gc_connector import GCPostgresConnector


class DispatcherApp:
    def __init__(self, environment: str, test_runs: int = 3):
        self.environment = environment
        self.test_runs = test_runs
        self.development_run = environment == 'dev'
        self.acceptance_run = environment == 'tst'
        self.prod_run = environment == 'prd'
        self.logger = getLogger("sf_evaluation")
        self.db = GCPostgresConnector(logger=self.logger)
        self.spark = SparkSession.builder.appName("Stockfish_Dispatcher").getOrCreate()
        self.dispatcher = None
        self.ems_dict = {}

    def get_secret(self, key: str) -> str:
        return os.getenv(key)

    def setup_stockfish_connection(self):
        base_url = 'https://api.gc.engine/api'
        acceptance_url = 'https://api.gc-acc.engine/api'
        api_path = 'v1/evaluate'

        if self.acceptance_run:
            conn = ConnectionSF(
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
            conn = ConnectionSF(
                base_url,
                api_path,
                self.logger,
                self.get_secret('gc-user'),
                self.get_secret('gc-pwd'),
                self.development_run,
                self.acceptance_run
            )
            self.ems_dict = {"api-stockfish": conn}

        self.dispatcher = DispatchManager(self.logger, self.spark, self.ems_dict)

    def get_last_timestamps(self):
        try:
            last_eval = self.db.query_latest_timestamp("evaluation_calculated", "last_delta_dt")
            last_delta = self.db.query_latest_timestamp("evaluation_delta", "minute_start")
        except Exception:
            self.logger.info("First run, tables don't exist yet.")
            now = datetime.now().replace(tzinfo=pytz.UTC)
            last_eval = last_delta = now
        return last_eval, last_delta

    def run(self):
        self.setup_stockfish_connection()
        last_eval, last_delta = self.get_last_timestamps()

        self.logger.info("LOOP")
        if self.prod_run:
            while True:
                try:
                    last_eval, last_delta = self.dispatcher.update_delta_and_evaluations(last_eval, last_delta)
                except Exception as e:
                    self.logger.exception(e)
        else:
            for _ in range(self.test_runs):
                try:
                    last_eval, last_delta = self.dispatcher.update_delta_and_evaluations(last_eval, last_delta)
                except Exception as e:
                    self.logger.exception(e)
