import chardet
from io import StringIO
from pandas_schema import Column, Schema
from pandas_schema.validation import MatchesPatternValidation, InRangeValidation, InListValidation, CustomSeriesValidation, DateFormatValidation, IsDistinctValidation

from validation_ans_schema import MasterDetail, ValidationLongColumn, ValidationColumnStatus, validateDateAutoColumn, validateEvntMarColumn

"""
	Tutoriale:

	function pour valider les colonnes:

	Function   												Description
	MatchesPatternValidation(r' Nombre de caracteres')   	function pour valider le numero de chiffres
	IsDistinctValidation()     								Validation de la colonne que les données doit être unique 
	InListValidation(['Actif', 'Archivé', 'Suspension'])    Valider que les données de la colonne se trouve dans la liste parametrée
	DateFormatValidation('%d/%m/%Y')  						Valider que le formatage de la date soit accorde indiqué


	MasterDetail(FileMaster, 'Code CIS', MasterFileName)
	(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required')) fonction pour valider que la colonne doit être présent obligatoirement 

"""


def schemaSpecialite(dfSource):
	schema_Specialite = Schema([
			Column('Code CIS', [MatchesPatternValidation(r'\d{8}'), # Doit être une chaine de caractères à 8 chiffres et obligatoire
								IsDistinctValidation() #Le code doit être unique								
								]),
			Column('Nom Spécialité', 
				[(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))   # fonction pour valider que la colonne doit être présent obligatoirement 
				]),
			
			Column('Statut AMM', [InListValidation(['Actif', 'Archivé', 'Suspension']),
							  (CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required')) #fonction pour valider que la colonne doit être présent obligatoirement 
							  ]), 

			Column('Date AMM', [DateFormatValidation('%d/%m/%Y'), #Valider que le formatage de la date soit accorde indiqué
								(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required')) #fonction pour valider que la colonne doit être présent obligatoirement 
								]),

			Column('Date Auto',[DateFormatValidation('%d/%m/%Y') #Valider que le formatage de la date soit accorde indiqué
								, validateDateAutoColumn(dfSource)
								],allow_empty=True),
			Column('Date fin de statut actif AMM',[DateFormatValidation('%d/%m/%Y'), #Valider que le formatage de la date soit accorde indiqué
										ValidationColumnStatus(dfSource)
										],allow_empty=True),

			Column('Procédure', [InListValidation(["Autorisation d'importation parallèle", 'Procédure centralisée','Procédure décentralisée', 'Procédure de reconnaissance mutuelle', 'Procédure nationale']),
							(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required')) #fonction pour valider que la colonne doit être présent obligatoirement 
							]),

			Column('Lib_ATC', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]), #fonction pour valider que la colonne doit être présent obligatoirement 
			Column('Code_ATC', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]), #fonction pour valider que la colonne doit être présent obligatoirement 
			Column('Classe virtuelle', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]), #fonction pour valider que la colonne doit être présent obligatoirement 

			Column('commentaire ACP') #La colonne doit être présent dans le fichier d'entre
	])

	return schema_Specialite

def schemaPresentation(FileMaster,MasterFileName):

	schema_presentation = Schema([
			Column('Code CIS', [MasterDetail(FileMaster, 'Code CIS', MasterFileName)]), # Doit être une chaine de caractères à 8 chiffres et obligatoire
			Column('Code CIP13', [MatchesPatternValidation(r'\d{13}')]), # Doit être une chaine de caractères à 13 chiffres et obligatoire
			Column('Code CIP7', [MatchesPatternValidation(r'\d{7}')]), # Doit être une chaine de caractères à 7 chiffres et obligatoire
			Column('Nom Presentation',[(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]) #fonction pour valider que la colonne doit être présent obligatoirement 
	])

	return schema_presentation

def schemaDispositif(FileMaster,FilePresentation,MasterFileName, PresentationFileName):

	# Schema for dispositif
	schema_dispositif = Schema([
			Column('Code CIS', [MasterDetail(FileMaster,'Code CIS', MasterFileName)]),
			Column('Code CIP13', [MasterDetail(FilePresentation,'Code CIP13', PresentationFileName)]),
			Column('Nature de dispositif')	#La colonne doit être présent dans le fichier de dispositif
		])

	return schema_dispositif

def schemaConditionnement(FileMaster,FilePresentation,MasterFileName, PresentationFileName):

	schema_Conditionnement = Schema([
			Column('Code CIS', [MasterDetail(FileMaster,'Code CIS', MasterFileName)]),
			Column('Code CIP13', [MasterDetail(FilePresentation,'Code CIP13', PresentationFileName)]),
			Column('Nom Element', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]), #fonction pour valider que la colonne doit être présent obligatoirement 

			Column('numElement',[ValidationLongColumn(1,1)]),

			Column('Recipient', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]) #fonction pour valider que la colonne doit être présent obligatoirement 
		])

	return schema_Conditionnement

def schemaSpecialiteEvenement(FileMaster,dfSource,MasterFileName):

	schema_SpecialiteEvenement = Schema([
		Column('Code CIS', [MasterDetail(FileMaster,'Code CIS', MasterFileName)]),
		Column('codeEvntSpec'), #La colonne doit être présent dans le fichier de Specilite evenement
		Column('DateEvnt_Spec',[DateFormatValidation('%d/%m/%Y'),
							(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))
										]),
		Column('remTerme Evnt', [InListValidation(['Changement de procédure', 'Changement de statut']),
							  (CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required')) #fonction pour valider que la colonne doit être présent obligatoirement 
							  ]),
		Column('EvntMar',[InListValidation(['actif', 'archivé', 'archivé (administratif)', 'changement de procédure', 'retire', 'suspension']),
						  (CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required')) #fonction pour valider que la colonne doit être présent obligatoirement 
						  ,validateEvntMarColumn(dfSource,['changement de procédure'],['Changement de procédure'])
						  ])
	])

	return schema_SpecialiteEvenement

def schemaEvenement(FileMaster,FilePresentation,MasterFileName, PresentationFileName):

	schema_Evenement = Schema([
		Column('Code CIS', [MasterDetail(FileMaster,'Code CIS', MasterFileName)]),
		Column('Code CIP13', [MasterDetail(FilePresentation,'Code CIP13', PresentationFileName)]),
		Column('codeEvntPres'), 	#La colonne doit être présent dans le fichier Evenement
		Column('DateEvnt_Presentation',[DateFormatValidation('%d/%m/%Y'),
										(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))
										]),
		Column('Evnt_Presentation',[(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required')) #fonction pour valider que la colonne doit être présent obligatoirement 
						]),
	])

	return schema_Evenement