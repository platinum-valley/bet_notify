import numpy as np
import pandas as pd
import pytest

from src.bettor import OptimizeTansyoBettor


# クラス初期化のためのフィクスチャ
@pytest.fixture
def bettor():
    return OptimizeTansyoBettor(
        budget=1000, pred_threshold=0, odds_threshold=1.0, exceed_profit_rate=1.1
    )


def test_generate_all_ticket(bettor):
    assert bettor._generate_all_ticket(5) == [5], "入力された数値を含むリストを返すべきです"


def test_generate_odds_matrix(bettor):
    # テスト用のモックデータを準備
    odds = np.array([2.0, 3.0])
    index = ["1", "2"]
    umaban_list = ["1", "2"]
    result = bettor._generate_odds_matrix(odds, index, umaban_list)

    assert np.all(np.equal(result, np.array([[2.0, 0, 1.0], [0, 3.0, 1.0]])))


# _correct_not_exceed_bet メソッドのテスト
def test_correct_not_exceed_bet(bettor):
    # モックの DataFrame と予算を準備
    df = pd.DataFrame(
        {"bet": [100, 500, 400], "odds": [2.0, 3.0, 1.0]}, index=["1", "2", "not_bet"]
    )
    budget = 1000
    result = bettor._correct_not_exceed_bet(df, budget)

    assert np.all(np.equal(result["bet"].values, np.array([0, 500, 500])))


def test_optimize(bettor):
    # odds, predictions などのモックデータを準備
    # _optimize メソッドを呼び出し
    # メソッドの期待される動作に基づいてアサーションを行う

    result = bettor.select_bet(
        pred=pd.Series([0.1, 0.5], index=["1", "2"]),
        odds=pd.Series([2.0, 3.0], index=["1", "2"]),
    )

    print(result)
