import pytest

from src.scraper import OddsScraper


@pytest.fixture
def scraper():
    """テスト用のフィクスチャ"""
    base_url = "https://race.netkeiba.com/odds/index.html?type=b1&"
    odds_scraper = OddsScraper(base_url)
    return odds_scraper


def test_init(scraper: OddsScraper):
    """初期化のテスト"""
    assert type(scraper) is OddsScraper


def test_has_driver(scraper: OddsScraper):
    """ドライバーを持つかテスト"""
    assert scraper._driver


def test_get_odds(scraper: OddsScraper):
    odds = scraper.get_odds_by_race(
        year=2023,
        jyo=5,
        kaiji=2,
        nichiji=12,
        race_num=11,
    )
    assert odds["1"] == 54.9
    assert odds["12"] == 8.3


def test_get_odds_2(scraper):
    year = 2022
    jyo = 5
    kaiji = 5
    nichiji = 8
    race_num = 12
    odds = scraper.get_odds_by_race(
        year=2023,
        jyo=5,
        kaiji=5,
        nichiji=8,
        race_num=12,
    )

    assert odds["2"] == 1.3
    assert odds["1"] == 3.7
