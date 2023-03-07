import math
import pandas as pd
import numpy as np
import datetime
import re
import typing
from pandas_schema import Column, Schema, validation
from pandas_schema.validation import _SeriesValidation, CustomSeriesValidation
from pandas_schema import ValidationWarning
from pandas_schema.errors import PanSchArgumentError


class ColonneObligatoire(_SeriesValidation):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La colonne est obligatoire'

    def validate(self, series: pd.Series) -> pd.Series:
        self.series = series

        return ~self.series.isna()

class ValidationNumElement(_SeriesValidation):
    
    def __init__(self, dfsource, dfsourcefk, nomFichier, **kwargs):
        self.dfsource = dfsource
        self.dfsourcefk = dfsourcefk
        self.nomFichier = nomFichier
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'Cet identifiant d''élément pour ce code CIS n\'existe pas dans le fichier {}'.format(self.nomFichier)

    def validate(self, series: pd.Series) -> pd.Series:
        self.series = series

        dfSourcePK = pd.DataFrame()
        dfSourceFK = pd.DataFrame()
        dfSourcePK['CodeCis-Element']  = self.dfsource['Code_CIS'].astype(str)+'-'+self.dfsource['Num_Element'].astype(str)
        dfSourceFK['CodeCis-Element'] = self.dfsourcefk['Code_CIS'].astype(str)+'-'+self.dfsourcefk['Num_Element'].astype(str)

        return dfSourcePK['CodeCis-Element'].isin(dfSourceFK['CodeCis-Element'])

class MasterDetail(_SeriesValidation):

    def __init__(self, masterSource, columnKey : str, MasterFilename ,**kwargs):
        
        self.masterSource = masterSource
        self.columnKey = columnKey
        self.MasterFilename = MasterFilename
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La valeur n\'a pas été trouvée dans le fichier "{}" '.format(self.MasterFilename)


    def validate(self, series: pd.Series) -> pd.Series:
        outputList = list()
        self.series = series
        
        #print(self.series.name)

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
        return 'la valeur est differente de "Archivé" ou "Suspension"'

    def validate(self, series: pd.Series) -> pd.Series:
        self.series = series

        df = self.dfSource[self.dfSource['Date_fin_statut_actif_AMM'].notna()]
        dfFilter = df[['Date_fin_statut_actif_AMM','Statut_AMM']]
        #outputSerie = pd.Series(dfFilter['Date_fin_statut_actif_AMM'].dropna().where(dfFilter['Statut_AMM'].isin(['Archivé','Suspension'])))
        outputSerie = pd.Series(dfFilter['Date_fin_statut_actif_AMM'].dropna().where(dfFilter['Statut_AMM'] != 'Actif'))
        return ~outputSerie.astype(str).str.contains("nan")

class validateDateAutoColumn(_SeriesValidation):

    def __init__(self, dfSource ,**kwargs):
        
        self.dfSource = dfSource
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La colonne est obligatoire'


    def validate(self, series: pd.Series) -> pd.Series:

        self.series = series
        df = self.dfSource[['Date_AMM','Date_Auto']]
        dfout = df[~df['Date_Auto'].isnull()]
       
        return ~self.series.isin(dfout)

class validateEvntMarColumn(_SeriesValidation):

    def __init__(self, dfSource, valuesList : list(), conditionList : list ,**kwargs):
        
        self.dfSource = dfSource
        self.valuesList = valuesList
        self.conditionList = conditionList
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La colonne "remTerme Evnt" est égale à "Changement de procédure", cette colonne "Evnt_Mar_Spc" doit avoir la valeur "changement de procédure"'


    def validate(self, series: pd.Series) -> pd.Series:

        self.series = series
        
        df = self.dfSource
        outSerie = pd.Series(df['Evnt_Mar_Spc'].where(df['Type_Evnt_Spc'].isin(self.conditionList) & ~df['Evnt_Mar_Spc'].isin(self.valuesList)))

        return outSerie.astype(str).str.contains("nan")

class longueurColonne(_SeriesValidation):
    def __init__(self, nlongueur ,**kwargs):
        self.nlongueur = nlongueur
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'la valeur doit avoir {} chiffre(s)'.format(self.nlongueur)

    def returnValue(self, result):
        

        if str(float(result)).lower() == 'nan':
            return True            
        else:
            if len(result) == self.nlongueur:
              return True  
            else:
                return False


    def validate(self, series: pd.Series) -> pd.Series:
        #s = series.replace('<NA>','-')
        return series.astype(str).apply(self.returnValue)

class validationValeurList(_SeriesValidation):

    def __init__(self, condition ,**kwargs):
        self.condition = condition
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La valeur doit être dans la liste {} '.format(self.condition)

    def valida_result(self, value):

        try:
            self.condition.index(value)
            return True
        except ValueError:
            if value == 'nan':
                return True
            else:
                return False

    def validate(self, series: pd.Series) -> pd.Series:
        return series.astype(str).apply(self.valida_result)

class validateFmtDateColumn(_SeriesValidation):

    def __init__(self,dateformat: str,**kwargs):
        self.date_format = dateformat
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La valeur doit être une date de la forme dd/mm/yyyy'.format(self.date_format)

    def valid_date_fmt(self, fmtValue):

        if fmtValue == 'nan':
            return True
        else:
            try:
                bool(datetime.datetime.strptime(fmtValue, self.date_format))
                return True                
            except:
                return False

            

    def validate(self, series: pd.Series) -> pd.Series:
        return series.astype(str).apply(self.valid_date_fmt)

class dateApresCreation(_SeriesValidation):

    def __init__(self, dfSource, **kwargs):
        
        self.dfSource = dfSource
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La date doit être **postérieure** à la date de création'

    def validate(self, series: pd.Series) -> pd.Series:

        self.series = series

        # Regle pour savoir si la date doit être une date **après** la Date_Creation_Proc
        self.outSerie = pd.Series(self.dfSource[self.dfSource.columns[1]].where(self.dfSource[self.dfSource.columns[1]].notnull())[self.dfSource[self.dfSource.columns[0]] > self.dfSource[self.dfSource.columns[1]]])
        
        return ~series.isin(self.outSerie)

class MatchesPatternValidation_fr(_SeriesValidation):
    """
    Validates that a string or regular expression can match somewhere in each element in this column
    """

    def __init__(self, pattern, options={}, **kwargs):
        """
        :param kwargs: Arguments to pass to Series.str.contains
            (http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.str.contains.html)
            pat is the only required argument
        """
        self.pattern = pattern
        self.options = options
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La valeur ne correspond pas au modèle "{}"'.format(self.pattern)

    def validate(self, series: pd.Series) -> pd.Series:
        return series.astype(str).str.contains(self.pattern, **self.options)

class DistinctValidation_fr(_SeriesValidation):
    """
    Checks that every element of this column is different from each other element
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La valeur n\'est pas unique'

    def validate(self, series: pd.Series) -> pd.Series:
        return ~series.duplicated(keep='first') 

class InListValidation_fr(_SeriesValidation):
    """
    Checks that each element in this column is contained within a list of possibilities
    """

    def __init__(self, options: typing.Iterable, case_sensitive: bool = True, **kwargs):
        """
        :param options: A list of values to check. If the value of a cell is in this list, it is considered to pass the
            validation
        """
        self.case_sensitive = case_sensitive
        self.options = options
        super().__init__(**kwargs)

    @property
    def default_message(self):
        values = ', '.join(str(v) for v in self.options)
        return 'La valeur ne se trouvée pas dans la list ({})'.format(values)

    def validate(self, series: pd.Series) -> pd.Series:
        if self.case_sensitive:
            return series.isin(self.options)
        else:
            return series.str.lower().isin([s.lower() for s in self.options])

class validationStatut_Specialite(_SeriesValidation):

    def __init__(self,dfSource,dfESpecialite,nomESpecialite,**kwargs):
        self.dfSource = dfSource
        self.dfESpecialite = dfESpecialite
        self.nomESpecialite = nomESpecialite
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La valeur du Status ne correspond pas avec la valeur "Evnt_Mar_Spc" du fichier {}'.format(self.nomESpecialite)

    def recupereMaxValeur(self, dfInput):
        
        
        df = dfInput[dfInput['Type_Evnt_Spc'] == 'Changement de statut']
        codeCis = pd.Series(df['Code_CIS'].unique())
        outputMax = list()
        for code in codeCis:
            dfOut = df[df['Code_CIS'].isin([code])]
            dfOper = dfOut[['Code_CIS','Evnt_Mar_Spc']][pd.to_datetime(dfOut['Date_Evnt_Spc'],format='%d/%m/%Y') == max(pd.to_datetime(dfOut['Date_Evnt_Spc'],format='%d/%m/%Y'))]
            #[dfOut['DateEvnt_Spec'].astype('datetime64[ns]') == max(dfOut['DateEvnt_Spec'].astype('datetime64[ns]'))]
            outputMax.append([x for l in dfOper.values for x in l])

        lst = list()
        for listOutput in outputMax:
            if len(listOutput) > 0:
                lst.append([listOutput[0],listOutput[1]])
        
        dfOutput = pd.DataFrame(lst,columns=['Code_CIS','Evnt_Mar_Spc'])
        return dfOutput

    def validationStatus(self,dfESpecialite, dfSpecialite):

        dfinner = pd.merge(left=dfSpecialite, right=dfESpecialite, how='left', left_on='Code_CIS', right_on='Code_CIS')
        dfOutput = dfinner[['Code_CIS','Statut_AMM','Evnt_Mar_Spc']]
       
        return dfOutput

    def outputResultat(self,rowdata):

        if rowdata.isna().any():
            return True
        else:
            if rowdata['values'] == False:
                return False
            else:
                return True

    def validate(self, series: pd.Series) -> pd.Series:

        #Evenement specialité
        dfEvSpecialite = self.recupereMaxValeur(self.dfESpecialite)
        # Validation        
        self.df = self.validationStatus(dfEvSpecialite,self.dfSource)
        self.df['values'] = (self.df['Statut_AMM'].apply(str.lower) == self.df['Evnt_Mar_Spc']) & ((self.df['Statut_AMM'] != "nan") & (self.df['Evnt_Mar_Spc']) != "nan")

        return self.df.apply(lambda x : self.outputResultat(x),axis=1)
       
class validateIntValeur(_SeriesValidation):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La valeur n\'est pas un entier'

    def validaTypeInt(self,value):
        valeur = str(value)
        if valeur != 'nan':
            i,d = valeur.split('.')
            if int(d) == 0:
                return True
            else:
                return False
        else:
            return True

    def validate(self, series: pd.Series) -> pd.Series:
        return series.apply(self.validaTypeInt)

class validateValeurIntorVergule(_SeriesValidation):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La valeur Quantité n\'est pas un intier'

    def validaValeur(self,value):
        valeur = str(value)
        if valeur != 'nan':
            try:
                if "." in valeur:
                    return True
                else:
                    float(valeur).is_integer()
                    return True
            except:
                if "," in valeur:
                    return False
                else:
                    return False
        else:
            return True

    def validate(self, series: pd.Series) -> pd.Series:
        return series.apply(self.validaValeur)

class validateCle(_SeriesValidation):
    def __init__(self, dfSource, colonne,nomFichier,**kwargs):
        self.df = dfSource
        self.nomFichier = nomFichier
        self.colonne = colonne
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return 'La valeur de la procedure n\'exist pas dans le fichier {}'.format(self.nomFichier)

    def evaluer(self,value):
        try:
            value in self.df[self.colonne]
            return True
        except:
            return False
            
    def validate(self, series: pd.Series) -> pd.Series:
        return series.apply(self.evaluer)
        

class valideCodeSubstanceFlag(_SeriesValidation):

    def __init__(self, dfDenominations, **kwargs):
        self.df = dfDenominations
        super().__init__(**kwargs)

    @property
    def default_message(self):
        return "Le code substance ne peut avoir qu\'une ligne avec le Flag_Substance = 'ANS nom préféré.'"

    def validate(self,series: pd.Series) -> pd.Series:

        dfOutput = pd.DataFrame()
        dfOutput['CODE'] = self.df['Code_Substance'].astype(str)+self.df['Flag_Substance'].astype(str)
        outputSerie = pd.Series(dfOutput['CODE'])
        return ~outputSerie.duplicated(keep='first')