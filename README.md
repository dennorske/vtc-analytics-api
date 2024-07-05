# vtc-analytics-api
A way to fetch data from VTCAnalytics while we wait for official API documentation. This script uses the flow that normal users go through in order to log in to the dashboard.

# How to use
Simply import AnalyticsManager and try to call a method. Here is an example:

```py
from AnalyticsManager import AnalyticsManager

manager = AnalyticsManager()
print(manager.get_driven_distance(30))  # Get driven distance for the VTC the last 30 days
```

You will need to install `python-dotenv` and have a `.env` file located in the root of your project with `VTC_USERNAME` and `VTC_PASSWORD` set.

WIP.
