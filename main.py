import datetime
import time
from typing import Any, Dict

import pandas as pd
import yaml

from src.bettor import OptimizeTansyoBettor
from src.load_pred import PredLoader
from src.notify import Notifier
from src.read_google_drive_json import GoogleDriveJsonReader
from src.scraper import OddsScraper


def is_time_difference_within_5_to_10_minutes(race_time: str, now_time: str) -> bool:
    """時間を "hhmm" 形式の文字列として受け取り、その差が5分から10分以内であるかどうかを判断する。

    Args:
        race_time (str): 比較する最初の時間（"hhmm"形式）。
        now_time (str): 比較する2番目の時間 ("hhmm"形式）。

    Returns:
        bool: 時間の差が5分から10分以内であればTrue、それ以外の場合はFalse。

    """
    # 文字列から時間オブジェクトに変換
    race_time = datetime.datetime.strptime(race_time, "%H%M")
    now_time = datetime.datetime.strptime(now_time, "%H%M")

    # 時間の差を計算（絶対値を取る）
    time_diff = (race_time - now_time).total_seconds() / 60

    # 5分以上10分以下かどうかを判断
    return 5 <= time_diff <= 10


def get_pred_in_time_range(
    json: Dict[str, Any], now_year: str, now_month_day: str, now_time: str
):
    if now_year in json.keys():
        if now_month_day in json[now_year].keys():
            for race_time in json[now_year][now_month_day]:
                # 現時刻と比較して5~10分後に発走するレースがあれば実行
                if not is_time_difference_within_5_to_10_minutes(race_time, now_time):
                    continue
                yield json[now_year][now_month_day][race_time]

    return None


def notify_bet():
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Google Driveの予測JSONファイルから予測を取得
    reader = GoogleDriveJsonReader(
        config["google_drive_credentials_json_path"],
        config["google_drive_token_json_path"],
        config["pred_json_path"],
    )

    # 現在の日時を取得
    now = datetime.datetime.now()
    now_year = now.strftime("%Y")
    now_month_day = now.strftime("%m%d")
    now_time = now.strftime("%H%M")

    print(now_year, now_month_day, now_time)

    # 現在時刻と予測ファイルの時間の開催時間が近いレースがあれば
    for race in get_pred_in_time_range(reader.json, now_year, now_month_day, now_time):
        jyo_cd = race["JyoCD"]
        jyo = race["Jyo"]
        kaiji = race["Kaiji"]
        nichiji = race["Nichiji"]
        race_num = race["RaceNum"]
        kyori = race["Kyori"]
        syubetu = race["Syubetu"]
        jyoken = race["Jyoken"]
        title = race["Title"]
        pred = pd.Series(race["pred"])

        # 該当レースのオッズをスクレイピング
        scraper = OddsScraper("https://race.netkeiba.com/odds/index.html?type=b1&")
        odds = scraper.get_odds_by_race(now_year, jyo_cd, kaiji, nichiji, race_num)

        # オッズと予測から馬券を最適化
        bettor = OptimizeTansyoBettor()
        bet = bettor.select_bet(pred, odds)

        # 購入馬券を通知する
        race_title = "{} {}R {} {} {}m {}".format(
            jyo, int(race_num), syubetu, jyoken, kyori, title if title != "nan" else ""
        )
        Notifier(
            config["line_notify_credential_path"],
        ).notify(race_title, bet[bet > 0])


def main():
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    while True:
        # 300秒(=5分)ごとに実行
        notify_bet()

        time.sleep(300)


if __name__ == "__main__":
    main()
