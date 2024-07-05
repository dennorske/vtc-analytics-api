import os
import pprint
import re
import sys
from typing import Optional

import dotenv
import requests

dotenv.load_dotenv(".env")


class AnalyticsManager:
    def __init__(
        self,
        username: str = os.getenv("VTC_USERNAME", ""),
        password: str = os.getenv("VTC_PASSWORD", ""),
    ) -> None:
        """Manages connection to the analytics system, with reverse engineered
        logic. There is a hidden token in the login page needed to authenticate
        requests. This is not the intended way of using the API, so the
        requests should be VERY limited in volume. New API is on its way from
        the official devs, but this should be good enough for now.

        See code for reference.
        """
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Python-requests/{0}".format(requests.__version__),
                "Accept-Encoding": "gzip, deflate",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        self.api_token = self.__get_api_token(username, password)

        # API specific:
        self.valid_time_selection = [30, 60, 365, "TODAY", "MTD", "QTD", "YTD"]
        self.api_url = "https://alphahaulageltd.vtcanalytics.com/nova-api"

    def __get_login_token(self) -> Optional[str]:
        """Get the login token from the login page."""
        pattern = (
            r'<input type="hidden" name="_token" value="([^"]*)" autocomplete="off">'
        )
        # The token comes from the value from _input field which is hidden
        # in the login page.

        response = self.session.get("https://alphahaulageltd.vtcanalytics.com/login")

        match = re.search(pattern, response.text)
        if match:
            return match.group(1)
        return None

    def __get_api_token(self, username, password):
        """Please cache this! (self.api_token). API token is used to authenticate requests to the
        underlying API for VTCAnalytics.

        Args:
            username (str): Username
            password (str): Password

        Since users need a linked Steam account, this needs to run on an
        existing user, aka no service accounts possible atm.
        """
        # "Referer": "https://alphahaulageltd.vtcanalytics.com/login",
        # Get the vtctoken to use with API

        data = {
            "email": username,
            "password": password,
            "_token": self.__get_login_token(),
            "remember": "off",
        }

        response = self.session.post(
            "https://alphahaulageltd.vtcanalytics.com/login",
            allow_redirects=True,
            data=data,
        )

        data = response.headers.get("vtc_analytics_session", None)
        if "Whoops! Something went wrong" in response.text:
            raise Exception(
                "Login failed, please double check your credentials are set."
            )

        if data:
            raise Exception("Could not fetch API token")
        return data

    def get_driven_distance(self, range=30):
        """Get the data for the driven distance, in kilometers.

        Args:
            days (int|str, optional): Number of days to get data for. Defaults to 30.
                Valid values are 30, 60, 365, TODAY, MTD, QTD, YTD
        """
        if range not in self.valid_time_selection:
            raise ValueError(f"range must be one of {self.valid_time_selection}")

        response = self.session.get(
            f"{self.api_url}/metrics/deliveries-driven-distance",
            params={"timezone": "UTC", "range": range},
        )
        return response.json().get("value", {}).get("value", 0)

    def get_deliveries(self, range=30):
        """Get the data for the deliveries.

        Args:
            days (int|str, optional): Number of days to get data for. Defaults to 30.
                Valid values are 30, 60, 365, TODAY, MTD, QTD, YTD
        """
        if range not in self.valid_time_selection:
            raise ValueError(f"range must be one of {self.valid_time_selection:}")

        response = self.session.get(
            f"{self.api_url}/metrics/new-deliveries",
            params={"timezone": "UTC", "range": range},
        )
        return response.json().get("value", {}).get("value", 0)

