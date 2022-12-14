import chardet
from io import StringIO
from pandas_schema import Column, Schema
from pandas_schema.validation import MatchesPatternValidation, InRangeValidation, InListValidation, CustomSeriesValidation, DateFormatValidation, IsDistinctValidation

from validation_ans_schema import MasterDetail, ValidationLongColumn

def schemaSpecialite():
	
	schema_Specialite = Schema([
			Column('Code CIS', [MatchesPatternValidation(r'\d{8}'), # Doit être une chaine de caractères à 8 chiffres
								IsDistinctValidation() #Le code doit être unique								
								]),
			Column('Nom Spécialité', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]),
			
			Column('Statut AMM', [InListValidation(['Actif', 'Archivé', 'Suspension']),
							  (CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]),

			Column('Date AMM', [DateFormatValidation('%d/%m/%Y'),
								(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))
								]),

			Column('Date Auto',[DateFormatValidation('%d/%m/%Y')],allow_empty=True),
			Column('Date fin de statut actif AMM',[DateFormatValidation('%d/%m/%Y')],allow_empty=True),

			Column('Procédure', [InListValidation(["Autorisation d'importation parallèle", 'Procédure centralisée','Procédure de reconnaissance mutuelle', 'Procédure nationale']),
							(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))
							]),

			Column('Lib_ATC', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]),
			Column('Code_ATC', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]),
			Column('Classe virtuelle', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]),

			Column('commentaire ACP')
	])

	return schema_Specialite

def schemaPresentation(FileMaster,MasterFileName):

	# Schema for presentation
	schema_presentation = Schema([
			Column('Code CIS', [MatchesPatternValidation(r'\d{8}'),
								MasterDetail(FileMaster, 'Code CIS', MasterFileName)								
				]),
			Column('Code CIP13', [MatchesPatternValidation(r'\d{13}')]),
			Column('Code CIP7', [MatchesPatternValidation(r'\d{7}')]),
			Column('Nom Presentation',[(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))])
	])

	return schema_presentation

def schemaDispositif(FileMaster,FilePresentation,MasterFileName, PresentationFileName):

	# Schema for dispositif
	schema_dispositif = Schema([
			Column('Code CIS', [MatchesPatternValidation(r'\d{8}'),
								MasterDetail(FileMaster,'Code CIS', MasterFileName)							
								]),
			Column('Code CIP13', [MatchesPatternValidation(r'\d{13}'),
								MasterDetail(FilePresentation,'Code CIP13', PresentationFileName)							
								]),
			Column('Nature de dispositif')	
		])

	return schema_dispositif

def schemaConditionnement(FileMaster,FilePresentation,MasterFileName, PresentationFileName):

	schema_Conditionnement = Schema([
			Column('Code CIS', [MatchesPatternValidation(r'\d{8}'),
								MasterDetail(FileMaster,'Code CIS', MasterFileName)
								]),
			Column('Code CIP13', [MatchesPatternValidation(r'\d{13}'),
								MasterDetail(FilePresentation,'Code CIP13', PresentationFileName)]),
			Column('Nom Element', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]),

			Column('numElement',[ValidationLongColumn(1,1)]),

			Column('Recipient', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))])
		])

	return schema_Conditionnement

def schemaSpecialiteEvenement(FileMaster,dfSource,MasterFileName):

	schema_SpecialiteEvenement = Schema([
		Column('Code CIS', [MatchesPatternValidation(r'\d{8}'),
							MasterDetail(FileMaster,'Code CIS', MasterFileName)
							]),
		Column('codeEvntSpec'),
		Column('DateEvnt_Spec',[DateFormatValidation('%d/%m/%Y'),
							(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))
										]),
		Column('remTerme Evnt', [InListValidation(['Changement de procédure', 'Changement de statut']),
							  (CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]),
		Column('EvntMar',[InListValidation(['actif', 'archivé', 'archivé (administratif)', 'changement de procédure', 'retire', 'suspension']),
						  (CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]),
	])

	return schema_SpecialiteEvenement


def schemaEvenement(FileMaster,FilePresentation,MasterFileName, PresentationFileName):

	schema_Evenement = Schema([
		Column('Code CIS', [MatchesPatternValidation(r'\d{8}'),
							MasterDetail(FileMaster,'Code CIS', MasterFileName)
							]),
		Column('Code CIP13', [MatchesPatternValidation(r'\d{13}'),
							MasterDetail(FilePresentation,'Code CIP13', PresentationFileName)
							]),
		Column('codeEvntPres'),
		Column('DateEvnt_Presentation',[DateFormatValidation('%d/%m/%Y'),
										(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))
										]),
		Column('Evnt_Presentation',[(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]),
	])

	return schema_Evenement