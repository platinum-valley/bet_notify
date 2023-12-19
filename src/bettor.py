from abc import ABCMeta, abstractmethod
from typing import List

import numpy as np
import pandas as pd
import scipy.optimize as sco


class Bettor(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        return NotImplementedError()

    @abstractmethod
    def select_bet(self, pred, odds):
        return NotImplementedError()


class OptimizeTansyoBettor(Bettor):
    """単勝予測確率と単勝オッズから購入馬券の最適化を行う。"""

    def __init__(
        self,
        budget: int = 1000,
        pred_threshold: float = 0,
        odds_threshold: float = 1.0,
        exceed_profit_rate: float = 1.1,
    ):
        """コンストラクタ

        Args:
            budget (int, optional): レースごとの投資予算. Defaults to 1000.
            pred_threshold (float, optional): 予測確率閾値. Defaults to 0.
            odds_threshold (float, optional): オッズ閾値. Defaults to 1.0.
            exceed_profit_rate (float, optional): 目標回収率. Defaults to 1.1.
        """
        self._budget = budget
        self._pred_threshold = pred_threshold
        self._odds_threshold = odds_threshold
        self._exceed_profit_rate = exceed_profit_rate

    def _generate_all_ticket(self, umaban: int) -> List[int]:
        """馬券種を返す

        Args:
            umaban (int): umaban

        Returns:
            List[int] : 単勝馬券種
        """

        return [umaban]

    def _generate_odds_matrix(
        self, odds: np.ndarray, index: List[str], umaban_list: List[int]
    ) -> np.ndarray:
        """汎用オッズ行列を作成する

        Args:
            odds (np.array): オッズ
            index (List[str]): オッズの券種リスト
            umaban_list (List[int]): 出走馬番リスト

        Returns:
            np.array: オッズ行列
        """
        odds_series = pd.Series(odds, index=index)

        odds_dict = {}
        odds_vectors = []
        for umaban in umaban_list:
            hit_ticket = self._generate_all_ticket(umaban)

            # 的中馬券のみoddsが入り、それ以外は0のベクトルを作成
            hit_odds = pd.Series(np.zeros_like(odds), index)
            hit_odds[hit_ticket] = 1
            tmp_odds = odds_series * hit_odds
            odds_vectors.append(tmp_odds)

        odds_matrix = pd.concat(odds_vectors, axis=1).T
        odds_matrix["not_bet"] = 1

        return odds_matrix.values

    def _correct_not_exceed_bet(self, df: pd.DataFrame, budget: int) -> pd.DataFrame:
        """
        データフレーム内の賭け金額を調整し、合計リターンが予算を超えないようにします。

        この関数は各賭けエントリについてのデータフレーム内の賭け金額とリターン値を変更します。
        賭けの合計額が指定された予算を超えないようにします。また、オッズに基づいてリターンを再計算し、
        'not_bet' エントリをそれに応じて更新します。

        引数:
            df (pandas.DataFrame): 賭けのデータを含むデータフレーム。'bet' と 'odds' の列があり、
                                特別なエントリ 'not_bet' を含むインデックスが期待されます。
            budget (int): 賭けに利用可能な合計予算。

        戻り値:
            pd.DataFrame: 賭け金額とリターンが調整されたデータフレーム。

        """
        # 元のデータを変更しないようにデータフレームのコピーを作成
        df_copy = df.copy()

        # 'not_bet' エントリを除いた利用可能な予算を計算
        available_budget = budget - df.loc["not_bet", "bet"]

        # 各賭けのリターンを計算
        df_copy["return"] = df["bet"] * df["odds"]

        # 払戻が予算を超えない場合にTrue
        df_copy["not_exceed"] = (
            (df_copy["return"] < available_budget)
            & (df_copy["bet"] != 0)
            & (df_copy.index != "not_bet")
        )

        # 'not_bet' エントリを自身の賭け金と予算を超えない賭けの合計金額で更新
        df_copy.loc["not_bet", ["bet", "return"]] = (
            df.loc["not_bet", "bet"] + df_copy.loc[df_copy["not_exceed"], "bet"].sum()
        )

        # 予算を超えない賭けの賭け金とリターンを0に設定
        df_copy.loc[df_copy["not_exceed"], ["bet", "return"]] = 0

        # 変更されたデータフレームを返す
        return df_copy[df.columns]

    def _optimize(
        self,
        odds: np.ndarray,
        pred: np.ndarray,
        index: List[str],
        umaban_list: List[int],
        budget: int = 1000,
    ) -> pd.DataFrame:
        def problem_func(
            weights: np.ndarray,
            odds_matrix: np.ndarray,
            pred: np.ndarray,
        ):
            """目的関数

            Args:
                weights (np.ndarray): 最適化変数
                odds_matrix (np.ndarray): オッズ行列
                pred (np.ndarray): 予測確率

            Returns:
                float: 損失
            """
            return -(pred * np.dot(odds_matrix, weights)).mean() / np.sqrt(
                np.cov(pred * np.dot(odds_matrix, weights))
            )

        def sum_x_equal_1(x):
            return -np.sum(x) + 1

        def all_bet_return_exceed_budget(x: np.ndarray, budget: int):
            loss_return = 0
            # not_betを除く全種で確認
            for i in range(len(x) - 1):
                # 100円以上賭ける馬券である場合
                if np.round(x[i] * budget / 100) > 0:
                    # 馬券的中の際に得られる利益が目標以上か確認する
                    exceed_profit = np.round(x[i] * budget / 100) * 100 * odds[
                        i
                    ] - self._exceed_profit_rate * budget * (
                        1 - np.round(x[-1] * budget / 100)
                    )
                    if exceed_profit < 0:
                        loss_return += exceed_profit

            return loss_return

        def all_bet_upper_minimum_bet(x: np.ndarray, budget: int):
            loss = 0
            for i in range(len(x) - 1):
                # 少額でもかける馬券に対して
                if x[i] > 0:
                    # 100円単位の掛け金に補正
                    bet = np.round(x[i] * budget / 100) * 100
                    # 少額だが100円未満の掛け金は損失とする
                    if bet == 0:
                        loss += x[i]
                return loss

        odds_matrix = self._generate_odds_matrix(odds, index, umaban_list) - 1
        odds = np.concatenate((odds, np.ones(1)), axis=0)

        # 制約条件
        constraints = []
        constraints.append({"type": "ineq", "fun": sum_x_equal_1})
        constraints.append(
            {"type": "ineq", "fun": all_bet_return_exceed_budget, "args": (budget,)}
        )
        constraints.append(
            {"type": "ineq", "fun": all_bet_upper_minimum_bet, "args": (budget,)}
        )

        # 初期解
        x0 = np.ones(len(odds)) / len(odds)

        # 上下制約
        bounds = [(0, 1)] * len(odds)

        # 最適化実行
        opts = sco.minimize(
            fun=problem_func,
            x0=x0,
            args=(odds_matrix, pred),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        df = pd.DataFrame([], index=list(index) + ["not_bet"])
        df["pred"] = pred + [1]
        df["odds"] = odds
        df["fraction"] = opts["x"]
        df["bet"] = np.round(opts["x"] * budget / 100) * 100
        df["return"] = df["bet"] * odds

        # 合計掛け金が予算を超えないように調整
        df = self._correct_not_exceed_bet(df, budget)

        if opts["success"]:
            return df["bet"]
        else:
            tmp = pd.Series(np.zeros_like(df["fraction"]), index=df.index)
            tmp["not_bet"] = budget
            return tmp

    def select_bet(self, pred: pd.Series, odds: pd.Series) -> pd.DataFrame:
        index = pred.index
        umaban_list = pred.index
        pred_list = []
        odds_list = []
        index_list = []
        for umaban in umaban_list:
            if (pred[umaban] >= self._pred_threshold) and (
                odds[umaban] >= self._odds_threshold
            ):
                pred_list.append(pred[umaban])
                odds_list.append(odds[umaban])
                index_list.append(f"{umaban}")

        if len(index_list) > 0:
            bet = self._optimize(
                odds_list, pred_list, index_list, index_list, self._budget
            )
        else:
            bet = pd.Series([self._budget], name="bet", index=["not_bet"])
        return bet
