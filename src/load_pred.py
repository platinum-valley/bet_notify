import json


class PredLoader:
    def __init__(self, pred_json_path):
        self._data = self._load_pred_json(pred_json_path)

    def _load_pred_json(self, pred_json_path):
        try:
            with open(pred_json_path, "r") as f:
                pred = json.load(f)
            return pred
        except FileNotFoundError:
            raise FileNotFoundError(f"ファイルが見つかりません: {pred_json_path}")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"ファイルが見つかりません: {pred_json_path}")

    @property
    def data(self):
        return self._data
