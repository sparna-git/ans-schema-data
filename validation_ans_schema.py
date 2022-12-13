
import math
import pandas as pd
import numpy as np

from pandas_schema import column
from pandas_schema.validation import _SeriesValidation 
from pandas_schema import ValidationWarning
from pandas_schema.errors import PanSchArgumentError

class ValidationLongColumn(_SeriesValidation):
    """
    Checks that each element in the series is within a given numerical range
    """

    def __init__(self, min: float = -math.inf, max: float = math.inf, **kwargs):
        """
        :param min: The minimum (inclusive) value to accept
        :param max: The maximum (exclusive) value to accept
        """
        self.min = min
        self.max = max
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'was not in the range {}'.format(self.min, self.max)

    def validate(self, series: pd.Series) -> pd.Series:
        series = pd.to_numeric(series, errors="coerce")
        return (series >= self.min) & (series <= self.max)

# function custom
class MasterDetail(_SeriesValidation):

    def __init__(self, masterSource, detailSource, columnKey : str, sourceNameMaster, MasterFilename ,**kwargs):
        
        self.masterSource = masterSource
        self.detailSource = detailSource
        self.columnKey = columnKey
        self.sourceName = sourceNameMaster
        self.MasterFilename = MasterFilename
        super().__init__(**kwargs)


    @property
    def default_message(self):
        #values = ', '.join(v["name"] for v in self.list_dfOuput) #self.namefile
        return 'Id does not match in the "{}" file '.format(self.MasterFilename)


    def validate(self, series: pd.Series) -> pd.Series:
        outputList = list()
        self.series = series
        

        dfResult = pd.DataFrame()
        dfResult[self.columnKey] = self.series #self.masterSource[self.columnKey]
        #dfResult["Value"] = self.masterSource[self.columnKey].isin(self.detailSource[self.columnKey])
        dfResult["Value"] = self.series.isin(self.masterSource[self.columnKey])
        dfResult["NameFile"] = self.sourceName 

        # Filter only the results not found
        self.dfOutput = dfResult[~dfResult["Value"]].fillna(method="ffill")

        #dfOutput = dfResult[~dfResult["Value"]].fillna(method="ffill")
        
        return ~self.series.isin(self.dfOutput[self.columnKey])
