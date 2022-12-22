
import math
import pandas as pd
import numpy as np

from pandas_schema import column
from pandas_schema.validation import _SeriesValidation, CustomSeriesValidation
from pandas_schema import ValidationWarning
from pandas_schema.errors import PanSchArgumentError

class ColonneObligatoire(_SeriesValidation):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La colonne doit être obligatoire'

    def validate(self, series: pd.Series) -> pd.Series:
        self.series = series

        return ~self.series.isna()

class ValidationLongColumn(_SeriesValidation):
    """
    Checks that each element in the series is within a given numerical range
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'Un seul chiffre entre 0 et 9'

    def validate(self, series: pd.Series) -> pd.Series:
        self.series = series

        return self.series.between(1,9,inclusive=True)

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
        return 'la colonne "Statut AMM" est different à "Archivé" or "Suspension"'

    def validate(self, series: pd.Series) -> pd.Series:
        self.series = series

        df = self.dfSource[['Statut AMM','Date fin de statut actif AMM']]
        outputSerie = pd.Series(df['Date fin de statut actif AMM'].dropna().where(df['Statut AMM'].isin(['Archivé','Suspension'])))
        return ~outputSerie.astype(str).str.contains("nan")

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
        
        df = self.dfSource
        outSerie = pd.Series(df['EvntMar'].where(df['remTerme Evnt'].isin(self.conditionList) & ~df['EvntMar'].isin(self.valuesList)))

        return outSerie.astype(str).str.contains("nan")

class validateIsDataColonne(_SeriesValidation):
    def __init__(self ,**kwargs):
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'la valuer de chiffre est different à 7'

    def validate(self, series: pd.Series) -> pd.Series:
        self.series = series

        df = pd.DataFrame(self.series.astype('Int32').astype(str), dtype='str')
        df.applymap(str)
        print(df)

        return 1