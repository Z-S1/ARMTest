"""
So for this task I tried to think of it not just as an isolated piece of functionality but also how it might function
in a broader, extensible system. For that reason I implemented a couple of plotting strategies; though I
believe the line graph is the better choice in this case due to how the Interest Over Time field works in Google Trends.

To keep this project easily readable I opted to keep it all in one file. Of course in a production environment this
would likely be split into modules for extensibility and maintainability.
"""

import logging
from abc import ABC, abstractmethod

from pytrends.request import TrendReq
import matplotlib.pyplot as plt
import pandas as pd


logging.basicConfig(level=logging.INFO)


class DataFetchingStrategy(ABC):
    search_data_type: str

    @abstractmethod
    def fetch_data(self, **kwargs):
        pass


class DataPlottingStrategy(ABC):
    @abstractmethod
    def plot_data(self, data: pd.DataFrame, search_data_type: str):
        pass


class GoogleTrendsFetchingStrategy(DataFetchingStrategy):
    def __init__(self, keywords, timeframe):
        self.search_data_type = "Google Trends"
        self.keywords = keywords
        self.timeframe = timeframe

    def fetch_data(self):
        try:
            pytrends = TrendReq()
            pytrends.build_payload(kw_list=self.keywords, timeframe=self.timeframe)
            data = pytrends.interest_over_time()
            return data.drop(columns=['isPartial'])  # drop isPartial here to maintain data consistency across terms
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return pd.DataFrame()


class LineChartPlottingStrategy(DataPlottingStrategy):
    def plot_data(self, data: pd.DataFrame, search_data_type: str):
        plt.figure(figsize=(10, 6))
        for column in data.columns:
            plt.plot(data.index, data[column], label=column)
        plt.title(f"{search_data_type} Search Data Over Time")
        plt.xlabel('Date')
        plt.ylabel('Relative Search Volume')
        plt.legend()
        plt.show()


class StackedAreaChartPlottingStrategy(DataPlottingStrategy):
    def plot_data(self, data: pd.DataFrame, search_data_type: str):
        plt.figure(figsize=(10, 6))
        plt.stackplot(data.index, *[data[category] for category in data],
                      labels=[category for category in data])
        plt.title(f"{search_data_type} Search Data Over Time - Stacked Area Chart")
        plt.xlabel('Date')
        plt.ylabel('Relative Search Volume')
        plt.legend(loc='upper left')
        plt.show()


class TrendingSearchDataApplication:
    def __init__(self, fetch_strategy: DataFetchingStrategy, plot_strategy: DataPlottingStrategy):
        self.fetch_strategy: DataFetchingStrategy = fetch_strategy
        self.plot_strategy: DataPlottingStrategy = plot_strategy
        self.data = None

    def run(self):
        self.data = self.fetch_strategy.fetch_data()
        self.plot()

    def plot(self):
        if not self.data.empty:
            self.plot_strategy.plot_data(self.data, search_data_type=self.fetch_strategy.search_data_type)
        else:
            raise ValueError("No data available, try cls.run()")


if __name__ == "__main__":
    fetch_strategy = GoogleTrendsFetchingStrategy(keywords={"Football", "Rugby", "Tennis"}, timeframe='today 3-m')
    plot_strategy = LineChartPlottingStrategy()

    app = TrendingSearchDataApplication(fetch_strategy, plot_strategy)
    app.run()

    app.plot_strategy = StackedAreaChartPlottingStrategy()
    app.plot()
