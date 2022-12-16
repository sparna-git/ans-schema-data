
import math
import pandas as pd
import numpy as np

from pandas_schema import column
from pandas_schema.validation import _SeriesValidation, CustomSeriesValidation
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

    def __init__(self, masterSource, columnKey : str, MasterFilename ,**kwargs):
        
        self.masterSource = masterSource
        self.columnKey = columnKey
        self.MasterFilename = MasterFilename
        super().__init__(**kwargs)


    @property
    def default_message(self):
        return 'Id does not match in the "{}" file '.format(self.MasterFilename)


    def validate(self, series: pd.Series) -> pd.Series:
        outputList = list()
        self.series = series
        

        dfResult = pd.DataFrame()
        dfResult[self.columnKey] = self.series
        dfResult["Value"] = self.series.isin(self.masterSource[self.columnKey])
        
        # Filter only the results not found
        self.dfOutput = dfResult[~dfResult["Value"]].fillna(method="ffill")
        
        return ~self.series.isin(self.dfOutput[self.columnKey])


class ValidationColumnStatus(_SeriesValidation):
    def __init__(self, dfSource ,**kwargs):
        
        self.dfSource = dfSource
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'la colonne "Statut AMM" est different à "Archivé" '

    def validate(self, series: pd.Series) -> pd.Series:
        self.series = series

        df = self.dfSource[['Statut AMM','Date fin de statut actif AMM']]
        dfOut = df[~df['Date fin de statut actif AMM'].isnull()]
        self.dfValue = dfOut[dfOut['Statut AMM'] != 'Archivé'].fillna(method="ffill")
        
        return ~self.series.isin(self.dfValue['Date fin de statut actif AMM'])


class validateDateAutoColumn(_SeriesValidation):

    def __init__(self, dfSource ,**kwargs):
        
        self.dfSource = dfSource
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'la colonne "Statut AMM" est vide '


    def validate(self, series: pd.Series) -> pd.Series:

        self.series = series
        df = self.dfSource[['Date AMM','Date Auto']]
        dfout = df[~df['Date Auto'].isnull()]
       
        return ~self.series.isin(dfout)



class validateEvntMarColumn(_SeriesValidation):

    def __init__(self, dfSource, valuesList : list(), conditionList : list ,**kwargs):
        
        self.dfSource = dfSource
        self.valuesList = valuesList
        self.conditionList = conditionList
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La colonne ne respecte pas la règle établie entre la colonne "remTerme Evnt" et "EvntMar", la valeur doit être obligatoirement "changement de procédure" '


    def validate(self, series: pd.Series) -> pd.Series:

        self.series = series
        
        df = self.dfSource[self.dfSource['remTerme Evnt'].isin(self.conditionList)]
        dfOutput = df[df['EvntMar'].isin(self.valuesList)]
        
        return self.series.isin(dfOutput)