class Notifier:
    def __init__(
        self,
        message: str = "",
        api_key: str = "",
    ):
        self._message = message
        self._api_key = api_key

    def notify(self):
        print(self._message)

    @property
    def message(self):
        return self._message
