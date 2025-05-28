# cluster_analyser.py

import chess
import chess.engine
import numpy as np
import pandas as pd
from typing import List, Dict, Any
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class ClusterAnalyser:
    """
    An object that clusters similar chess positions using a set of handcrafted features:
    - Material difference
    - King safety (pawn shield)
    - Mobility (legal move count)
    - Time used on move
    - Centipawn loss
    - Evaluation

    Input: A DataFrame containing positions with FENs and metadata (time_used, eval_cp, cp_loss)
    Output: Same DataFrame with cluster labels and optional cluster center descriptions.
    """

    PIECE_VALUES = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }

    def __init__(self, n_clusters: int = 5, random_state: int = 42) -> None:
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.model = KMeans(n_clusters=n_clusters, random_state=random_state)
        self.cluster_centers_: List[List[float]] = []
        self.features_used: List[str] = []

    def extract_features_from_fen(self, fen: str) -> Dict[str, float]:
        board = chess.Board(fen)

        # Material balance: positive means white advantage
        material = 0
        for piece_type in self.PIECE_VALUES:
            material += (
                len(board.pieces(piece_type, chess.WHITE)) - len(board.pieces(piece_type, chess.BLACK))
            ) * self.PIECE_VALUES[piece_type]

        # King safety: count pawns in front of king (on own 2nd/3rd rank)
        def king_safety(board: chess.Board, color: bool) -> int:
            king_square = board.king(color)
            if king_square is None:
                return 0
            rank = chess.square_rank(king_square)
            file = chess.square_file(king_square)
            safety_zone = []
            if color == chess.WHITE:
                safety_zone = [chess.square(f, r) for r in [1, 2] for f in range(file-1, file+2) if 0 <= f <= 7]
            else:
                safety_zone = [chess.square(f, r) for r in [6, 5] for f in range(file-1, file+2) if 0 <= f <= 7]
            return sum(1 for sq in safety_zone if board.piece_type_at(sq) == chess.PAWN and board.color_at(sq) == color)

        king_safety_white = king_safety(board, chess.WHITE)
        king_safety_black = king_safety(board, chess.BLACK)
        king_safety_score = king_safety_white - king_safety_black

        # Mobility: number of legal moves for the side to move
        mobility = board.legal_moves.count()

        return {
            "material": material,
            "king_safety": king_safety_score,
            "mobility": mobility
        }

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        extracted = df["fen"].apply(self.extract_features_from_fen)
        feature_df = pd.DataFrame(extracted.tolist())
        combined_df = pd.concat([df.reset_index(drop=True), feature_df], axis=1)
        return combined_df

    def fit(self, df: pd.DataFrame) -> pd.DataFrame:
        df_features = self.prepare_features(df)

        # Use only numerical features for clustering
        feature_cols = ["material", "king_safety", "mobility", "time_used", "eval_cp", "cp_loss"]
        self.features_used = feature_cols

        X = df_features[feature_cols].fillna(0).values
        X_scaled = self.scaler.fit_transform(X)
        cluster_labels = self.model.fit_predict(X_scaled)

        df_features["cluster"] = cluster_labels
        self.cluster_centers_ = self.model.cluster_centers_

        return df_features

    def describe_clusters(self) -> pd.DataFrame:
        """Return a DataFrame summarizing the cluster centers."""
        centers_scaled = self.cluster_centers_
        centers_original = self.scaler.inverse_transform(centers_scaled)
        return pd.DataFrame(centers_original, columns=self.features_used)