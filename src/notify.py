import os

import pandas as pd
import requests


class Notifier:
    def __init__(
        self,
        access_token_path: str,
    ):
        """
        with open(access_token_path, "r") as f:
            self._access_token = f.read()
        """
        self._access_token = os.environ.get("LINE_NOTIFY_TOKEN")

    def notify(self, title: str, bet: pd.Series):
        url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": "Bearer " + self._access_token}

        bet_umaban = bet.index.values
        bet_money = bet.values

        race = "\n{}".format(title)
        bet = ""
        for umaban, money in zip(bet_umaban, bet_money):
            bet += "\n{} {}円".format(umaban, money)

        message = "{}{}".format(race, bet)

        payload = {"message": message}
        r = requests.post(
            url,
            headers=headers,
            params=payload,
        )

    @property
    def message(self):
        return self._message
