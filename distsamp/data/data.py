from typing import Any, Callable

import pandas as pd

from distsamp.state.state import State


class Data:
    """
    Encapsulates data to allow operations to be run across multiple data sources
    Contains the logic of how to apply the approximating method to the data

    Should be subclassed into concrete implementations, for example:
        - LocalData
        - SparkData
    """

    def __init__(self):
        pass

    def run(self, f_approximate_tilted: Callable[[Any, State], State], cavity: State) -> State:
        raise NotImplementedError("")


class LocalData:

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe

    def run(self, f_approximate_tilted: Callable[[pd.DataFrame, State], State], cavity: State) -> State:
        return f_approximate_tilted(self.df, cavity)


class SparkData:

    def __init__(self, dataframe):
        self.sdf = dataframe

    def run(self, f_approximate_tilted: Callable[[Any, State], State], cavity: State) -> State:
        return self.sdf.apply_or_such_like(f_approximate_tilted, cavity)
