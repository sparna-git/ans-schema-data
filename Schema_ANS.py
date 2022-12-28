import chardet
from io import StringIO
from pandas_schema import Column, Schema
from pandas_schema.validation import MatchesPatternValidation, InRangeValidation, InListValidation, CustomSeriesValidation, IsDistinctValidation

import datetime
from datetime import datetime
from validation_ans_schema import MasterDetail, ValidationLongColumn, ValidationColumnStatus, validateDateAutoColumn, validateEvntMarColumn, ColonneObligatoire, validationCommentaire_ACP, longueurColonne, validateFmtDateColumn, dateApresCreation

"""
	Tutoriale:

	function pour valider les colonnes:

	Function   												Description
	MatchesPatternValidation(r' Nombre de caracteres')   	function pour valider le numero de chiffres
	IsDistinctValidation()     								Validation de la colonne que les données doit être unique 
	InListValidation(['Actif', 'Archivé', 'Suspension'])    Valider que les données de la colonne se trouve dans la liste parametrée
	


	MasterDetail(FileMaster, 'Code CIS', MasterFileName)
	(CustomSeriesValidation(lambda x: x.str.len() > 0, 'La coLonne doit être obligatoire')) fonction pour valider que la colonne doit être présent obligatoirement 

"""


def schemaSpecialite(dfSource, dfPresentation, dfConditionnement, namePresentation, nameConditionnement):
	schema_Specialite = Schema([
			Column('Code CIS', [MatchesPatternValidation(r'\d{8}'), # Doit être une chaine de caractères à 8 chiffres et obligatoire
								IsDistinctValidation(), #Le code doit être unique								
								ColonneObligatoire(),
								MasterDetail(dfPresentation, 'Code CIS', namePresentation), #Presentation
								MasterDetail(dfConditionnement, 'Code CIS', nameConditionnement) #Conditionnement
								]),
			Column('Nom Spécialité',[ColonneObligatoire()]),
			
			Column('Statut AMM', [InListValidation(['Actif', 'Archivé', 'Suspension']),
							  ColonneObligatoire()
							  ]), 

			Column('Date AMM', [validateFmtDateColumn('%d/%m/%Y'), #Valider que le formatage de la date soit accorde indiqué
								ColonneObligatoire()
								]),

			Column('Date Auto',[validateFmtDateColumn('%d/%m/%Y') #Valider que le formatage de la date soit accorde indiqué
								, validateDateAutoColumn(dfSource)
								],allow_empty=True),
			Column('Date fin de statut actif AMM',[validateFmtDateColumn('%d/%m/%Y'), #Valider que le formatage de la date soit accorde indiqué
										ValidationColumnStatus(dfSource)
										],allow_empty=True),

			Column('Procédure', [InListValidation(["Autorisation d'importation parallèle", 'Procédure centralisée','Procédure décentralisée', 'Procédure de reconnaissance mutuelle', 'Procédure nationale']),
							ColonneObligatoire()
							]),

			Column('Lib_ATC', [ColonneObligatoire()]), #fonction pour valider que la colonne doit être présent obligatoirement 
			Column('Code_ATC', [ColonneObligatoire()]), #fonction pour valider que la colonne doit être présent obligatoirement 
			Column('Classe virtuelle', [ColonneObligatoire()]), #fonction pour valider que la colonne doit être présent obligatoirement 

			Column('commentaire ACP',[validationCommentaire_ACP(['Enregistrement homéo', 'Spécialité de phyto', 'Spécialité contenant plus de 3 SA'])])
	])

	return schema_Specialite

def schemaPresentation(FileMaster,MasterFileName,dfPDispositif, namePDispositif):

	schema_presentation = Schema([
			Column('Code CIS', [MasterDetail(FileMaster, 'Code CIS', MasterFileName),
								ColonneObligatoire()
							 	]),
			Column('Code CIP13', [MatchesPatternValidation(r'\d{13}'), 
								  ColonneObligatoire(),
								  MasterDetail(dfPDispositif, 'Code CIP13', namePDispositif)
								  ]),
			Column('Code CIP7',[longueurColonne(7)]),
			Column('Nom Presentation',[ColonneObligatoire()])
	])

	return schema_presentation

def schemaDispositif(FileMaster,FilePresentation,MasterFileName, PresentationFileName):

	# Schema for dispositif
	schema_dispositif = Schema([
			Column('Code CIS', [MasterDetail(FileMaster,'Code CIS', MasterFileName), ColonneObligatoire()]),
			Column('Code CIP13', [MasterDetail(FilePresentation,'Code CIP13', PresentationFileName), ColonneObligatoire()]),
			Column('Nature de dispositif')
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
		Column('DateEvnt_Spec',[validateFmtDateColumn('%d/%m/%Y'),
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
		Column('DateEvnt_Presentation',[validateFmtDateColumn('%d/%m/%Y'),
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
		Column('numElement', [ColonneObligatoire(),
					ValidationLongColumn()		
				]),
		Column('Forme pharmaceutique Elmt',[ColonneObligatoire()]),
		Column('Nom Element', [ColonneObligatoire()]),
		Column('Référence dosage', [ColonneObligatoire()]),
		Column('Code substance', [ColonneObligatoire()]),
		Column('Nom Nature', [InListValidation(['Substances actives.', 'Fractions thérapeutiques.']),
							  ColonneObligatoire()
							  ]),
		Column('Sub Dosage'),
		Column('numOrdreEdit',[ColonneObligatoire(),
							   MatchesPatternValidation(r'^[0-9]*$')	
							]),
		Column('Dosage'),
		Column('Nom du composant'),
		Column('Code substance cle',[IsDistinctValidation()])
		])

	return schema_composition

def schemaListeEvenementPresentation(dfSource):

	schema_liste_evenement_presentation = Schema([
		Column('Id_ANSM_Evenement_Pre',[ColonneObligatoire(),
							MatchesPatternValidation(r'^[0-9]*$')
						]),
		Column('Lib_Evenement_Pre'),		
		Column('Type_Evenement_Pre'),
		Column('Desc_Evenement_Pre'),
		Column('Date_Creation_Evenement_Pre',[ColonneObligatoire(),
				validateFmtDateColumn('%d/%m/%Y')
			]),
		Column('Date_Modif__Evenement_Pre',[validateFmtDateColumn('%d/%m/%Y')]),
		Column('Date_Inactiv_Evenement_Pre',[dateApresCreation(dfSource[['Date_Creation_Evenement_Pre','Date_Inactiv_Evenement_Pre']]),validateFmtDateColumn('%d/%m/%Y')])
		])

	return schema_liste_evenement_presentation

def schemaListeProcedure(dfSource):

	schema_liste_procedure = Schema([
		Column('Id_ANSM_proc',[ColonneObligatoire(),
						MatchesPatternValidation(r'^[0-9]*$')
						]),
		Column('Lib_Proc',[ColonneObligatoire()]),
		Column('Desc_proc'),
		Column('Date_Creation_Proc',[ColonneObligatoire(),
				validateFmtDateColumn('%d/%m/%Y')
			]),
		Column('Date_Modif_Proc',[validateFmtDateColumn('%d/%m/%Y')]),
		Column('Date_Inactiv_proc',[dateApresCreation(dfSource[['Date_Creation_Proc','Date_Inactiv_proc']]),validateFmtDateColumn('%d/%m/%Y')])
		])

	return schema_liste_procedure

def schemaListeStatus(dfSource):

	schema_liste_status = Schema([
		Column('Id_ANSM_Statut',[ColonneObligatoire(),
						MatchesPatternValidation(r'^[0-9]*$')
						]),
		Column('Lib_Statut',[ColonneObligatoire()]),
		Column('Desc_statut'),
		Column('Date_Creation_Statut',[ColonneObligatoire(),
				validateFmtDateColumn('%d/%m/%Y')
			]),
		Column('Date_Modif_Statut',[validateFmtDateColumn('%d/%m/%Y')]),
		Column('Date_Inactiv_Statut',[dateApresCreation(dfSource[['Date_Creation_Statut','Date_Inactiv_Statut']]), 
									validateFmtDateColumn('%d/%m/%Y')])
		])

	return schema_liste_status