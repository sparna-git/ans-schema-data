import chardet
from io import StringIO
from pandas_schema import Column, Schema
from pandas_schema.validation import InListValidation, IsDtypeValidation
import numpy as np

from validation_ans_schema import MasterDetail, ValidationNumElement, ValidationColumnStatus, validateDateAutoColumn, validateEvntMarColumn, ColonneObligatoire, validationValeurList, longueurColonne, validateFmtDateColumn, dateApresCreation, DistinctValidation_fr, MatchesPatternValidation_fr, InListValidation_fr,validationStatut_Specialite,validateIntValeur, validateValeurIntorVergule, validateCle, valideCodeSubstanceFlag

def schemaSpecialite(dfSource, dfPresentation, dfConditionnement, namePresentation, nameConditionnement, dfESpecialite, nomESpecialite,dfLStatus,nomLStatus,dfLProcedures,nomLProcedures):
	schema_Specialite = Schema([
			Column('Code_CIS', [MatchesPatternValidation_fr(r'\d{8}'), # Doit être une chaine de caractères à 8 chiffres et obligatoire
								DistinctValidation_fr(), #Le code doit être unique								
								ColonneObligatoire(),
								MasterDetail(dfPresentation,'Code_CIS', namePresentation), #Presentation
								MasterDetail(dfConditionnement,'Code_CIS', nameConditionnement) #Conditionnement
								]),
			Column('Nom_Specialite',[ColonneObligatoire()]),			
			Column('Statut_AMM', [ColonneObligatoire()
							  	  #validationStatut_Specialite(dfSource,dfESpecialite, nomESpecialite)
							  ]), 
			Column('Code_Statut',[ColonneObligatoire(),
								  MasterDetail(dfLStatus,'Code_Statut', nomLStatus)
								]),
			Column('Date_AMM', [ColonneObligatoire(),
								validateFmtDateColumn('%d/%m/%Y')
								]),
			Column('Date_Auto',[validateFmtDateColumn('%d/%m/%Y'),
								validateDateAutoColumn(dfSource)
								],allow_empty=True),
			Column('Date_fin_statut_actif_AMM',[validateFmtDateColumn('%d/%m/%Y'),
										ValidationColumnStatus(dfSource)
										],allow_empty=True),
			Column('Procedure', [ColonneObligatoire()]),
			Column('Code_Procedure',[ColonneObligatoire(),
									 validateCle(dfLProcedures, 'Code_Proc',nomLProcedures)
									 ]),
			Column('Lib_ATC', [ColonneObligatoire()]),
			Column('Code_ATC', [ColonneObligatoire()])
	])

	return schema_Specialite

def schemaPresentation(dfSpecialite,nameSpecialite,dfPDispositif, namePDispositif, dfConditionnement, nameConditionnement, dfUCD, nomUCD):

	schema_presentation = Schema([
			Column('Code_CIS', [ColonneObligatoire(),
								MasterDetail(dfSpecialite,'Code_CIS', nameSpecialite)								
							 	]),
			Column('Code_CIP13', [MatchesPatternValidation_fr(r'\d{13}'), 
								  ColonneObligatoire(),
								  MasterDetail(dfPDispositif, 'Code CIP13', namePDispositif),
								  MasterDetail(dfConditionnement, 'Code_CIP13', nameConditionnement),
								  MasterDetail(dfUCD, 'CodeCIP13', nomUCD)
								  ]),
			Column('Code_CIP7', [longueurColonne(7)]),
			Column('Nom_Presentation',[ColonneObligatoire()])
	])

	return schema_presentation

def schemaDispositif(FileMaster,dfPresentation,MasterFileName, PresentationFileName):

	# Schema for dispositif
	schema_dispositif = Schema([
			Column('Code CIS', [MasterDetail(FileMaster,'Code_CIS', MasterFileName), ColonneObligatoire()]),
			Column('Code CIP13', [MasterDetail(dfPresentation,'Code_CIP13', PresentationFileName), ColonneObligatoire()]),
			Column('Dispositifs (liste)')
		])

	return schema_dispositif

def schemaConditionnement(dfSource,FileMaster,dfPresentation,MasterFileName, PresentationFileName,dfComposition,nomComposition):

	schema_Conditionnement = Schema([
			Column('Code_CIS', [MasterDetail(FileMaster,'Code_CIS', MasterFileName), ColonneObligatoire()]),
			Column('Code_CIP13', [MasterDetail(dfPresentation,'Code_CIP13', PresentationFileName)]),
			Column('Num_Element'),
			Column('Nom_Element', [ColonneObligatoire()]),			
			Column('Recipient', [ColonneObligatoire()])
		])

	return schema_Conditionnement

def schemaSpecialiteEvenement(dfSpecialite,dfSource,nameSpecialite,dfL_Evenement_Specialite, nomL_Evenement_Specialite):

	schema_SpecialiteEvenement = Schema([
		Column('Code_CIS', [MasterDetail(dfSpecialite,'Code_CIS', nameSpecialite),ColonneObligatoire()]),
		Column('Code_Evnt_Spc',[ColonneObligatoire(),
								MasterDetail(dfL_Evenement_Specialite,'Code_Evnt_Spc', nomL_Evenement_Specialite)
						]),
		Column('Date_Evnt_Spc',[validateFmtDateColumn('%d/%m/%Y'),
							ColonneObligatoire()
										]),
		Column('Date_Echeance',[validateFmtDateColumn('%d/%m/%Y')]),
		Column('Type_Evnt_Spc', [InListValidation_fr(['Changement de procédure', 'Changement de statut', 'Statut actif']),
							  ColonneObligatoire()
							  ]),
		Column('Evnt_Mar_Spc',[ColonneObligatoire()])
	])

	return schema_SpecialiteEvenement

def schemaEvenement(FileMaster,FilePresentation,MasterFileName, PresentationFileName, dfListePresentation, namelistePresentation):

	schema_Evenement = Schema([
		Column('Code_CIS', [MasterDetail(FileMaster,'Code_CIS', MasterFileName), ColonneObligatoire()]),
		Column('Code_CIP13', [MasterDetail(FilePresentation,'Code_CIP13', PresentationFileName), ColonneObligatoire()]),
		Column('Code_Evnt_Pres',[ColonneObligatoire(),
							   MasterDetail(dfListePresentation,'Code_Evnt_Pres', namelistePresentation)
								]),
		Column('Date_Evnt_Pres',[validateFmtDateColumn('%d/%m/%Y'),
										ColonneObligatoire()
										]),
		Column('Evnt_Pres',[ColonneObligatoire()]),
	])

	return schema_Evenement

def schemaSpecialiteComposition(dfSource,dfSpecialite,nameSpecialite,dfConditionnement, nomConditionnement,dfSubstance, nomfichierSubstance):
	
	schema_composition= Schema([
		Column('Code_CIS',[ColonneObligatoire(),
					MasterDetail(dfSpecialite,'Code_CIS', nameSpecialite),
					MasterDetail(dfConditionnement,'Code_CIS', nomConditionnement)
			]),
		Column('Num_Element', [ColonneObligatoire(),
					ValidationNumElement(dfSource,dfConditionnement,nomConditionnement)		
				]),
		Column('Forme_Phar_Element',[ColonneObligatoire()]),
		Column('Nom_Element', [ColonneObligatoire()]),
		Column('Nom_Nature', [InListValidation_fr(['Substances actives.', 'Fractions thérapeutiques.']),
							  ColonneObligatoire()
							  ]),
		Column('Reference_dosage'),
		Column('Code_Substance', [ColonneObligatoire(),
								MasterDetail(dfSubstance,'Code_Substance', nomfichierSubstance)
							]),		
		Column('numOrdreEdit',[ColonneObligatoire(),
							   MatchesPatternValidation_fr(r'^[0-9]*$')	
							]),
		Column('Dosage'),
		Column('CIS-Element-Substance',[DistinctValidation_fr()])
		])

	return schema_composition

def schemaListeEvenementPresentation(dfSource):

	schema_liste_evenement_presentation = Schema([
		Column('Code_Evnt_Pres',[ColonneObligatoire(),
							MatchesPatternValidation_fr(r'^[0-9]*$')
						]),
		Column('Lib_Evnt_Pres',[ColonneObligatoire()]),		
		Column('Type_Evnt_Pres'),
		Column('Desc_Evnt_Pres'),
		Column('Date_Creation_Evnt_Pres',[ColonneObligatoire(),
				validateFmtDateColumn('%d/%m/%Y')
			]),
		Column('Date_Modif_Evnt_Pres',[validateFmtDateColumn('%d/%m/%Y')]),
		Column('Date_Inactiv_Evnt_Pres',[dateApresCreation(dfSource[['Date_Creation_Evnt_Pres','Date_Inactiv_Evnt_Pres']]),validateFmtDateColumn('%d/%m/%Y')])
		])

	return schema_liste_evenement_presentation

def schemaListeProcedure(dfSource):

	schema_liste_procedure = Schema([
		Column('Code_Proc',[ColonneObligatoire(),
						MatchesPatternValidation_fr(r'^[0-9]*$')
						]),
		Column('Lib_Procedure',[ColonneObligatoire()]),
		Column('Desc_Procedure'),
		Column('Date_Crea_Procedure',[ColonneObligatoire(),
				validateFmtDateColumn('%d/%m/%Y')
			]),
		Column('Date_Modif_Procedure',[validateFmtDateColumn('%d/%m/%Y')]),
		Column('Date_Inactiv_Procedure',[dateApresCreation(dfSource[['Date_Crea_Procedure','Date_Inactiv_Procedure']]),validateFmtDateColumn('%d/%m/%Y')])
		])

	return schema_liste_procedure

def schemaListeStatus(dfSource):

	schema_liste_status = Schema([
		Column('Code_Statut',[ColonneObligatoire(),
						MatchesPatternValidation_fr(r'^[0-9]*$')
						]),
		Column('Lib_Statut',[ColonneObligatoire()]),
		Column('Desc_statut'),
		Column('Date_Crea_Statut',[ColonneObligatoire(),
				validateFmtDateColumn('%d/%m/%Y')
			]),
		Column('Date_Modif_Statut',[validateFmtDateColumn('%d/%m/%Y')]),
		Column('Date_Inactiv_Statut',[dateApresCreation(dfSource[['Date_Crea_Statut','Date_Inactiv_Statut']]), 
									validateFmtDateColumn('%d/%m/%Y')])
		])
	
	return schema_liste_status

def schemaListeEvenementSpecialite():

	schema_liste_EvenementSpecialite = Schema([
		Column('Code_Evnt_Spc',[ColonneObligatoire()]),
		Column('Lib_Evnt_Spc',[ColonneObligatoire()]),
		Column('Type_Evnt_Spc',[ColonneObligatoire()]),
		Column('Desc_Evnt_Spc'),
		Column('Date_Crea_Evnt_Spc',[validateFmtDateColumn('%d/%m/%Y')]),
		Column('Date_Modif_Evnt_Spc',[validateFmtDateColumn('%d/%m/%Y')]),
		Column('Date_Inactiv_Evnt_Spc',[validateFmtDateColumn('%d/%m/%Y'),

									
									])
		])

	return schema_liste_EvenementSpecialite

def schema_substance():

	schema_substance = Schema([
		Column('Code_Substance',[ColonneObligatoire()]),
		Column('Code_SMS',[ColonneObligatoire()]),
		Column('Lib_Pref_Fran',[ColonneObligatoire()]),
		Column('Lib_Pref_Anglais'),	
		Column('Date_Crea_Substance', [ColonneObligatoire(),
								validateFmtDateColumn('%d/%m/%Y')
								]),
		Column('Date_Modif_Substance', [#ColonneObligatoire(),
								validateFmtDateColumn('%d/%m/%Y')
								])
	])

	return schema_substance

def schema_denominations_substance(dfSubstance, nomfichierSubstance, dfDenominations):

	schema_denominations_substance = Schema([
		Column('Code_Substance',[ColonneObligatoire(),
				MasterDetail(dfSubstance,'Code_Substance',nomfichierSubstance)
			]),
		Column('code_Nom_Substance',[ColonneObligatoire()]),
		Column('Nom_Substance',[ColonneObligatoire()]),
		Column('Flag_Substance',[ColonneObligatoire(),
								validationValeurList(['ANS nom préféré','ANS autre nom']),
								valideCodeSubstanceFlag(dfDenominations)
								]),
		Column('Langue_nom_substance',[ColonneObligatoire()]),
		Column('Date_Crea_Nom_Substance', [ColonneObligatoire(),
								validateFmtDateColumn('%d/%m/%Y')
								]),
		Column('Date_Modif_Nom_Substance', [validateFmtDateColumn('%d/%m/%Y')])
	])

	return schema_denominations_substance

def schemaUCD(dfPresentation, namePresentation):

	schema_UCD = Schema([
		Column('CodeUCD',[ColonneObligatoire(),MatchesPatternValidation_fr(r'\d{7}')]),
		Column('CodeCIP',[ColonneObligatoire(),MatchesPatternValidation_fr(r'\d{7}'),DistinctValidation_fr()]),
		Column('LibelleUCD',[ColonneObligatoire()]),
		Column('LibelleCIP'),
		Column('Laboratoire'),
		Column('Qte',[ColonneObligatoire(),validateIntValeur()]),
		Column('CodeUCD13',[ColonneObligatoire(),MatchesPatternValidation_fr(r'\w{13}')]),
		Column('CodeCIP13',[ColonneObligatoire(),MasterDetail(dfPresentation,'Code_CIP13', namePresentation)]),
		Column('Type autorisation 1'),
		Column('Type autorisation 2'),
		Column('Date de commercialisation',[ColonneObligatoire(),validateFmtDateColumn('%d/%m/%Y')]),
		Column('Date de suppression',[validateFmtDateColumn('%d/%m/%Y')]),
		Column('Quantité conditionnement Primaire',[validateValeurIntorVergule()]),
		Column('Unité conditionnement primaire',[validationValeurList(['dose','g','L','mg','mL','[iU]'])]) #['DOSE','GRAMME','KG','LITRE','MEGABECQUEREL','MILLIGRAMME','MILLILITRES','UNITE-INTERNATIONALE']
		])

	return schema_UCD