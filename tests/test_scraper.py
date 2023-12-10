import pytest

from src.scraper import OddsScraper


@pytest.fixture
def scraper():
    """テスト用のフィクスチャ"""
    base_url = "https://race.netkeiba.com/odds/index.html?type=b1&"
    year = 2023
    jyo = 5
    kaiji = 2
    nichiji = 2
    race_num = 11
    odds_scraper = OddsScraper()
    return odds_scraper


def test_init(scraper):
    """初期化のテスト"""
    assert scraper is OddsScraper
