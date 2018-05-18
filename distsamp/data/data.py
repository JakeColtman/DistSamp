import pandas as pd


class Data:

    def __init__(self):
        pass

    def run(self, f_approximate_tilted, cavity):
        raise NotImplementedError("")


class LocalData:

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe

    def run(self, f_approximate_tilted, cavity):
        return f_approximate_tilted(self.df, cavity)


class SparkData:

    def __init__(self, dataframe):
        self.sdf = dataframe

    def run(self, f_approximate_tilted, cavity):
        return self.sdf.apply_or_such_like(f_approximate_tilted, cavity)