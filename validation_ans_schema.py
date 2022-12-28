import math
import pandas as pd
import numpy as np
import datetime
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

class longueurColonne(_SeriesValidation):
    def __init__(self, nlongueur ,**kwargs):
        self.nlongueur = nlongueur
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'la valuer est different à {} chiffre(s)'.format(self.nlongueur)

    def validation_longeur_value(self, value):
        print(value)
        try:
            if value.astype(str).str.len() == self.nlongueur:
                return True
        except:
            if value == 'nan':
                return True
            else:
                return False

    def validate(self, series: pd.Series) -> pd.Series:
        return series.astype(str).apply(self.validation_longeur_value)

class validationCommentaire_ACP(_SeriesValidation):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return ' la valeur doit être une valeur dans ["Enregistrement homéo", "Spécialité de phyto", "Spécialité contenant plus de 3 SA"]'

    def validate(self, series: pd.Series) -> pd.Series:
        
        return series.isin(['Enregistrement homéo', 'Spécialité de phyto', 'Spécialité contenant plus de 3 SA'])

class validateDateColumn(_SeriesValidation):

    def __init__(self,dateformat: str,**kwargs):
        self.date_format = dateformat
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'la colonne doit être une date de la forme dd/mm/yyyy .'.format(self.date_format)

    def valid_date_fmt(self, val):
        
        try:
            datetime.datetime.strptime(val, self.date_format)            
            return True
        except:
            if val == 'nan':
                return True
            else:
                return False

    def validate(self, series: pd.Series) -> pd.Series:
        return series.astype(str).apply(self.valid_date_fmt)

class dateApresCreation(_SeriesValidation):

    def __init__(self, dfSource, date_format: str,**kwargs):
        
        self.dfSource = dfSource
        self.date_format = date_format
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La date doit être une date **après** la Date_Creation au la forme {} ne correspond pas'.format('jj/mm/yyyy')

    def valid_date_fmt(self, val):
        
        try:
            datetime.datetime.strptime(val,self.date_format)
            return True
        except:
            return False

    def validate(self, series: pd.Series) -> pd.Series:

        self.series = series

        # Regle pour savoir si la date doit être une date **après** la Date_Creation_Proc
        self.outSerie = pd.Series(self.dfSource[self.dfSource.columns[1]].where(self.dfSource[self.dfSource.columns[1]].notnull())[self.dfSource[self.dfSource.columns[0]] > self.dfSource[self.dfSource.columns[1]]])
        
        # Pour valider le format de la date
        dfValidatefmt = self.dfSource[self.dfSource[self.dfSource.columns[1]].notnull()]
        self.outfmtSerie = pd.Series(dfValidatefmt[self.dfSource.columns[1]].astype(str).apply(self.valid_date_fmt))
        
        return (~self.outSerie.isin(self.series)) | (self.outfmtSerie.isin(self.series))