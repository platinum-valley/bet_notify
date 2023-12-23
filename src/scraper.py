import os

import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


class OddsScraper:
    """NetKeibaサイトから指定レースの単勝オッズをスクレイピングする"""

    def __init__(self, base_url):
        self._driver = self._set_driver()

    def _set_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # or use pyvirtualdiplay
        options.add_argument("--no-sandbox")  # needed, because colab runs as root
        options.add_argument("enable-automation")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument('--proxy-server="direct://"')
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--lang=ja")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--dns-prefetch-disable")
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        )
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("user-agent=" + UserAgent().random)
        options.binary_location = "/usr/share/headless-chromium"

        # ドライバー指定でChromeブラウザを開く
        # chrome_service = fs.Service(ChromeDriverManager().install())
        chrome_service = fs.Service(executable_path="/usr/share/chromedriver")

        # open it, go to a website, and get results
        driver = webdriver.Chrome(options=options)

        return driver

    def get_odds_by_race(
        self, year: int, jyo: int, kaiji: int, nichiji: int, race_num: int
    ) -> pd.Series:
        """引数に該当するレースの単勝オッズを返す

        Args:
            year (int): 年
            jyo (int): 競馬場
            kaiji (int): 回次
            nichiji (int): 日次
            race_num (int): レース番組

        Returns:
            pd.Series: 該当レースの単勝オッズ
        """
        self._driver.get(
            "https://race.netkeiba.com/odds/index.html?type=b1&race_id={}{:02}{:02}{:02}{:02}".format(
                year, jyo, kaiji, nichiji, race_num
            )
        )

        html = self._driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        tracks = soup.find(class_="RaceOdds_HorseList Tanfuku", id="odds_fuku_block")
        uma_kumi_list = []
        odds_dict = {}
        for track in tracks.select("[class='W31']"):
            umaban1 = track.contents[0]
            uma_kumi_list.append(umaban1)
        for uma_kumi in uma_kumi_list:
            id_ = "odds-1_{}".format(uma_kumi.zfill(2))
            odds = soup.find("span", id=id_)
            if odds is not None:
                odds_num = float(odds.string)
                # if odds_num < odds_threshold:
                odds_dict[uma_kumi] = odds_num
        return pd.Series(odds_dict)

    @property
    def driver(self):
        return self._driver
