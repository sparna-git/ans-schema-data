import chardet
from io import StringIO
from pandas_schema import Column, Schema
from pandas_schema.validation import MatchesPatternValidation, InRangeValidation, InListValidation, CustomSeriesValidation, DateFormatValidation, IsDistinctValidation

from validation_ans_schema import MasterDetail, ValidationLongColumn, ValidationColumnStatus, validateDateAutoColumn, validateEvntMarColumn, validateIsDataColonne, ColonneObligatoire

"""
	Tutoriale:

	function pour valider les colonnes:

	Function   												Description
	MatchesPatternValidation(r' Nombre de caracteres')   	function pour valider le numero de chiffres
	IsDistinctValidation()     								Validation de la colonne que les données doit être unique 
	InListValidation(['Actif', 'Archivé', 'Suspension'])    Valider que les données de la colonne se trouve dans la liste parametrée
	DateFormatValidation('%d/%m/%Y')  						Valider que le formatage de la date soit accorde indiqué


	MasterDetail(FileMaster, 'Code CIS', MasterFileName)
	(CustomSeriesValidation(lambda x: x.str.len() > 0, 'La coLonne doit être obligatoire')) fonction pour valider que la colonne doit être présent obligatoirement 

"""


def schemaSpecialite(dfSource):
	schema_Specialite = Schema([
			Column('Code CIS', [MatchesPatternValidation(r'\d{8}'), # Doit être une chaine de caractères à 8 chiffres et obligatoire
								IsDistinctValidation(), #Le code doit être unique								
								ColonneObligatoire()
								]),
			Column('Nom Spécialité',[ColonneObligatoire()]),
			
			Column('Statut AMM', [InListValidation(['Actif', 'Archivé', 'Suspension']),
							  ColonneObligatoire()
							  ]), 

			Column('Date AMM', [DateFormatValidation('%d/%m/%Y'), #Valider que le formatage de la date soit accorde indiqué
								ColonneObligatoire()
								]),

			Column('Date Auto',[DateFormatValidation('%d/%m/%Y') #Valider que le formatage de la date soit accorde indiqué
								, validateDateAutoColumn(dfSource)
								],allow_empty=True),
			Column('Date fin de statut actif AMM',[DateFormatValidation('%d/%m/%Y'), #Valider que le formatage de la date soit accorde indiqué
										ValidationColumnStatus(dfSource)
										],allow_empty=True),

			Column('Procédure', [InListValidation(["Autorisation d'importation parallèle", 'Procédure centralisée','Procédure décentralisée', 'Procédure de reconnaissance mutuelle', 'Procédure nationale']),
							ColonneObligatoire()
							]),

			Column('Lib_ATC', [ColonneObligatoire()]), #fonction pour valider que la colonne doit être présent obligatoirement 
			Column('Code_ATC', [ColonneObligatoire()]), #fonction pour valider que la colonne doit être présent obligatoirement 
			Column('Classe virtuelle', [ColonneObligatoire()]), #fonction pour valider que la colonne doit être présent obligatoirement 

			Column('commentaire ACP') #La colonne doit être présent dans le fichier d'entre
	])

	return schema_Specialite

def schemaPresentation(FileMaster,MasterFileName):

	schema_presentation = Schema([
			Column('Code CIS', [MasterDetail(FileMaster, 'Code CIS', MasterFileName), ColonneObligatoire()]), # Doit être une chaine de caractères à 8 chiffres et obligatoire
			Column('Code CIP13', [MatchesPatternValidation(r'\d{13}'), 
								  ColonneObligatoire()
								  ]),
			Column('Code CIP7'),
			Column('Nom Presentation',[ColonneObligatoire()])
	])

	return schema_presentation

def schemaDispositif(FileMaster,FilePresentation,MasterFileName, PresentationFileName):

	# Schema for dispositif
	schema_dispositif = Schema([
			Column('Code CIS', [MasterDetail(FileMaster,'Code CIS', MasterFileName), ColonneObligatoire()]),
			Column('Code CIP13', [MasterDetail(FilePresentation,'Code CIP13', PresentationFileName), ColonneObligatoire()]),
			Column('Nature de dispositif')	#La colonne doit être présent dans le fichier de dispositif
		])

	return schema_dispositif

def schemaConditionnement(FileMaster,FilePresentation,MasterFileName, PresentationFileName):

	schema_Conditionnement = Schema([
			Column('Code CIS', [MasterDetail(FileMaster,'Code CIS', MasterFileName), ColonneObligatoire()]),
			Column('Code CIP13', [MasterDetail(FilePresentation,'Code CIP13', PresentationFileName)]),
			Column('Nom Element', [ColonneObligatoire()]),
			Column('numElement',[ValidationLongColumn()]),
			Column('Recipient', [ColonneObligatoire()])
		])

	return schema_Conditionnement

def schemaSpecialiteEvenement(FileMaster,dfSource,MasterFileName):

	schema_SpecialiteEvenement = Schema([
		Column('Code CIS', [MasterDetail(FileMaster,'Code CIS', MasterFileName),ColonneObligatoire()]),
		Column('codeEvntSpec',[ColonneObligatoire()]),
		Column('DateEvnt_Spec',[DateFormatValidation('%d/%m/%Y'),
							ColonneObligatoire()
										]),
		Column('remTerme Evnt', [InListValidation(['Changement de procédure', 'Changement de statut']),
							  ColonneObligatoire()
							  ]),
		Column('EvntMar',[InListValidation(['actif', 'archivé', 'archivé (administratif)', 'changement de procédure', 'retire', 'suspension']),
						  ColonneObligatoire(),
						  validateEvntMarColumn(dfSource,['changement de procédure'],['Changement de procédure'])
						  ])
	])

	return schema_SpecialiteEvenement

def schemaEvenement(FileMaster,FilePresentation,MasterFileName, PresentationFileName):

	schema_Evenement = Schema([
		Column('Code CIS', [MasterDetail(FileMaster,'Code CIS', MasterFileName), ColonneObligatoire()]),
		Column('Code CIP13', [MasterDetail(FilePresentation,'Code CIP13', PresentationFileName), ColonneObligatoire()]),
		Column('codeEvntPres',[ColonneObligatoire()]),
		Column('DateEvnt_Presentation',[DateFormatValidation('%d/%m/%Y'),
										ColonneObligatoire()
										]),
		Column('Evnt_Presentation',[ColonneObligatoire()]),
	])

	return schema_Evenement

def schemaSpecialiteComposition(FileMaster,MasterFileName):
	
	schema_composition= Schema([
		Column('Code CIS',[ColonneObligatoire(),
					MasterDetail(FileMaster,'Code CIS', MasterFileName)					
			]),
		Column('numElement', [ColonneObligatoire(), #(CustomSeriesValidation(lambda x: x.astype(str).str.len() > 0, 'La coLonne doit être obligatoire')),
					ValidationLongColumn()		
				]),
		Column('Forme pharmaceutique Elmt',[ColonneObligatoire()]),
		Column('Nom Element', [ColonneObligatoire()]),
		Column('Référence dosage', [ColonneObligatoire()]),
		Column('Code substance', [
				ColonneObligatoire()

			]),
		Column('Nom Nature', [InListValidation(['Substances actives.', 'Fractions thérapeutiques.']),
							  ColonneObligatoire()
							  ]),
		Column('Sub Dosage'),
		Column('numOrdreEdit',[ColonneObligatoire()

							]),
		Column('Dosage'),
		Column('Nom du composant',[ColonneObligatoire()])
		])

	return schema_composition