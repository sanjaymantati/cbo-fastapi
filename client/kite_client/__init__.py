import logging
import os

from kiteconnect import KiteConnect

logging.basicConfig(level=logging.DEBUG)


class KiteClient:
    def __init__(self):
        self.api_secret = os.environ.get("KITE_API_SECRET")
        self.api_key = os.environ.get("KITE_API_KEY")
        self.access_token = os.environ.get("KITE_API_ACCESS_TOKEN")

    def historical_data(self, instrument_token, from_date, to_date, interval,
                        continuous=False, oi=False):
        kite = self.__get_kite_client()
        return kite.historical_data(instrument_token, from_date, to_date,
                                    interval,
                                    continuous=continuous, oi=oi)

    def __get_kite_client(self) -> KiteConnect:
        return KiteConnect(api_key=self.api_key,
                           access_token=self.access_token)
