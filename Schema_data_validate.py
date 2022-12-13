import pandas as pd
import sys
import os
import chardet
from io import StringIO
from pandas_schema import Column, Schema

from validation_ans_schema import MasterDetail, ValidationLongColumn

from pandas_schema.validation import MatchesPatternValidation, InRangeValidation, InListValidation, CustomSeriesValidation, DateFormatValidation, IsDistinctValidation


def read_csv(fileInput):
	"""
		read un fichier d'entre csv
	"""
	reader = pd.read_csv(fileInput, delimiter=';')

	return reader
	
def listDataFrame(pathInputs):
	"""
		fonction pour convertir tous les fichiers d'entre comme dataframe
	"""
	# Déclare une variable comme list
	dfList = list()
	# Boucle pour lire tous les fichiers d'un dossier
	for f in os.listdir(pathInputs):
		fileInput = os.path.join(pathInputs, f)

		if os.path.isfile(fileInput):
	 		
	 		dfInput = pd.DataFrame(read_csv(fileInput))
	
	 		type_file=""
	 		filename = os.path.basename(fileInput)
	 		
	 		if filename.startswith('1_ANS_Spécialité_pharmaceutique_'):
	 			type_file="specialite"
	 		if filename.startswith('2_ANS_Présentation_'):
	 			type_file="presentation"
	 		if filename.startswith('2_2_ANS_Présentation_dispositif_'):
	 			type_file="dispositif"
	 		if filename.startswith('2_1_ANS_Présentation_conditionnement_'):
	 			type_file="conditionnement"

	 		dfList.append([filename,type_file,dfInput])

	return dfList

def validateSchemaMaster(filename,KeyFileMaster):
	"""
		Schéma Master est le schéma principal dans notre cas sera la specialité
	"""
	
	# Schema for Specialities
	schema_Specialite = Schema([
		Column('Code CIS', [MatchesPatternValidation(r'\d{8}'),
							IsDistinctValidation()]),
		Column('Nom Spécialité', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]),
		Column('Statut AMM', [InListValidation(['Actif', 'Archivé', 'Suspension']),
						  (CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]),

		Column('Date AMM', [DateFormatValidation('%d/%m/%Y')],allow_empty=True),
	
		Column('Date Auto'),
		Column('Date fin de statut actif AMM'),

		Column('Procédure', [InListValidation(["Autorisation d'importation parallèle", 'Procédure centralisée','Procédure de reconnaissance mutuelle', 'Procédure nationale']),
						(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))
						]),

		Column('Lib_ATC', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]),
		Column('Code_ATC', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]),
		Column('Classe virtuelle', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]),

		Column('commentaire ACP')
	])

	# Validation de les donnes avec le schéma
	errors = schema_Specialite.validate(KeyFileMaster)
	
	# 
	listResult = list()
	for error in errors:
		listResult.append([filename,str(error.row),error.column,str(error.value),error.message])

	return listResult


def validateSchemaPresentation(filename,KeyFileMaster,dfSource, ColumnKey, MasterFileName):

	# Schema for presentation
	schema_presentation = Schema([
		Column('Code CIS', [MatchesPatternValidation(r'\d{8}'),
							MasterDetail(KeyFileMaster,dfSource,ColumnKey, filename, MasterFileName)
			]),
		Column('Code CIP13', [MatchesPatternValidation(r'\d{13}')]),
		Column('Code CIP7', [MatchesPatternValidation(r'\d{7}')]),
		Column('Nom Presentation',[(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))])
	])

	# Validation de les donnes avec le schéma
	errors = schema_presentation.validate(dfSource)

	# Validation de les donnes avec le schéma
	listResult = list()
	for error in errors:
		listResult.append([filename,str(error.row),error.column,str(error.value),error.message])
	
	return listResult

def validateSchemaDispositif(filename,KeyFileMaster,KeyFilePresentation,dfSource, ColumnKey, MasterFileName, PresentationFileName):
	# Schema for dispositif
	schema_dispositif = Schema([
		Column('Code CIS', [MatchesPatternValidation(r'\d{8}'),
							MasterDetail(KeyFileMaster,dfSource,ColumnKey, filename, MasterFileName)]),
		Column('Code CIP13', [MatchesPatternValidation(r'\d{13}'),
							MasterDetail(KeyFilePresentation,dfSource,'Code CIP13', filename, PresentationFileName)]),
		Column('Nature de dispositif')	
	])
	# Validation de les donnes avec le schéma
	errors = schema_dispositif.validate(dfSource)

	listResult = list()
	for error in errors:
		listResult.append([filename,str(error.row),error.column,str(error.value),error.message])

	return listResult

def validateSchemaConditionnement(filename,KeyFileMaster,KeyFilePresentation,dfSource, ColumnKey, MasterFileName, PresentationFileName):

	schema_Conditionnement = Schema([
		Column('Code CIS', [MatchesPatternValidation(r'\d{8}'),
							MasterDetail(KeyFileMaster,dfSource,ColumnKey, filename, MasterFileName)]),
		Column('Code CIP13', [MatchesPatternValidation(r'\d{13}'),
							MasterDetail(KeyFilePresentation,dfSource,'Code CIP13', filename, PresentationFileName)]),
		Column('Nom Element', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))]),

		Column('numElement',[ValidationLongColumn(1,1)]),

		Column('Recipient', [(CustomSeriesValidation(lambda x: x.str.len() > 0, 'This Column is required'))])
	])



	errors = schema_Conditionnement.validate(dfSource)
	
	listResult = list()	
	for error in errors:
		listResult.append([filename,str(error.row),error.column,str(error.value),error.message])
	
	return listResult
	
def createResult(files: list, ColumnKey):
	dfResult = pd.DataFrame()


	# On va chercher les fichies principal pour valider
	dfMaster = pd.DataFrame()
	nameMaster = ""
	dfPresentation = pd.DataFrame()
	namePresentation = "" 
	for m in files:
		if m[1] == "specialite":
			nameMaster = m[0]
			dfMaster = m[2]
		if m[1] == "presentation":
			namePresentation = m[0]
			dfPresentation = m[2]
			

	logErros = list()
	for f in files:

		schema_to_validate=f[1]
		print("fichier: "+ f[0])
		# DataFrame Master
		if schema_to_validate == "specialite":
			logErros.append(validateSchemaMaster(schema_to_validate,f[2]))
		if schema_to_validate == "presentation":
		  	logErros.append(validateSchemaPresentation(schema_to_validate,dfMaster,f[2],ColumnKey,nameMaster))
		if schema_to_validate == "dispositif":
			logErros.append(validateSchemaDispositif(schema_to_validate,dfMaster,dfPresentation,f[2],ColumnKey,nameMaster,namePresentation))
		if schema_to_validate == "conditionnement":
		 	logErros.append(validateSchemaConditionnement(schema_to_validate,dfMaster,dfPresentation,f[2],ColumnKey,nameMaster,namePresentation))

	# Generate une liste 
	resultList = sum(logErros, [])
	# Crée un dataframe de resultat
	dfResult = pd.DataFrame(resultList,columns=['Fichier','Ligne','Colonne',"Valeur","Message"])
	
	return dfResult
	

if __name__ == '__main__':
	
	source_files = sys.argv[1] # Path source files
	output_result = sys.argv[2] # Output File

	"""
		Lire tous les fichier d'entre et les sauvegarder dans une liste
	"""
	DataFrameList = listDataFrame(source_files)

	"""
		Fonction pour generer les validations avec chaque type de Schema.
		La fonction a besoin de la liste de fichiers d'entre et une Clé de colonne principal

	"""
	result = createResult(DataFrameList,'Code CIS')

	"""
		Le resultat sera sauvegarder dans un fichier html et un fichier csv

	"""
	if not  result.empty:
		result.to_html(output_result+'.html',header=True,index=False, notebook=False, justify="center")
		result.to_csv(output_result+'.csv',header=True,index=False)