import time
from typing import Any, Dict

import yaml

from src.bettor import OptimizeTansyoBettor
from src.load_pred import PredLoader
from src.notify import Notifier
from src.read_google_drive_json import GoogleDriveJsonReader
from src.scraper import OddsScraper


def notify_bet(config: Dict[str, Any]):
    # Google Driveの予測JSONファイルから予測を取得
    json = GoogleDriveJsonReader(
        config["google_drive_credentials_json_path"],
        config["google_drive_token_json_path"],
        config["pred_json_path"],
    )
    # 現在時刻と予測ファイルの時間の開催時間が近いレースがあれば

    # 該当レースのオッズをスクレイピング

    # オッズと予測から馬券を最適化

    # 購入馬券を通知する
    pass


def main():
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    notify_bet(config)


if __name__ == "__main__":
    main()
