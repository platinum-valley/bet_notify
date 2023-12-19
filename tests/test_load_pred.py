import json

import pytest

from src.load_pred import PredLoader

json_pred_data = {
    "2023": {
        "1224": {
            "15:40": {
                "JyoCD": "05",
                "RaceNum": "11",
                "pred": {
                    "1": 0.03,
                    "2": 0.10,
                    "3": 0.23,
                    "4": 0.05,
                    "5": 0.03,
                    "6": 0.32,
                    "7": 0.06,
                    "8": 0.04,
                },
            }
        }
    }
}


@pytest.fixture(scope="module")
def test_json_file(tmp_path_factory: pytest.TempPathFactory):
    test_json_file = tmp_path_factory.mktemp("test_data") / "test_data.json"
    with open(test_json_file, "w") as f:
        json.dump(json_pred_data, f)

    return test_json_file


@pytest.fixture(scope="module")
def pred_loader(test_json_file):
    return PredLoader(test_json_file)


def test_generate_loader(pred_loader: PredLoader):
    assert type(pred_loader) == PredLoader


def test_not_found_json_file():
    with pytest.raises(FileNotFoundError):
        PredLoader("not_found.json")


def test_load_data(pred_loader: PredLoader):
    assert pred_loader.data == json_pred_data
