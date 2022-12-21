import pandas as pd
import sys
import os
from pandas_schema import Schema
import Schema_ANS
import shutil

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

			print("Lecture du fichier: " + fileInput)
			dfInput = pd.read_csv(fileInput, delimiter=';',index_col=False,encoding="cp1252")
	
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
			if filename.startswith('2_3_ANS_Présentation_événement_'):
				type_file="evenement"
			if filename.startswith('1_2_ANS_Spécialité_pharmaceutique_événement_'):
				type_file="specialiteEvenement"

			dfList.append([filename,type_file,dfInput])

	return dfList

def createResult(files: list):
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
	errors = list()
	for f in files:

		schema_to_validate=f[1]
		print("Vérification du fichier: "+ f[0])

		# DataFrame Master
		if schema_to_validate == "specialite":
		 	errors = Schema_ANS.schemaSpecialite(f[2]).validate(f[2])
		if schema_to_validate == "presentation":
		    	errors = Schema_ANS.schemaPresentation(dfMaster,nameMaster).validate(f[2])
		if schema_to_validate == "dispositif":
		 	errors = Schema_ANS.schemaDispositif(dfMaster,dfPresentation,nameMaster,namePresentation).validate(f[2])
		if schema_to_validate == "conditionnement":
		   	errors = Schema_ANS.schemaConditionnement(dfMaster,dfPresentation,nameMaster,namePresentation).validate(f[2])
		if schema_to_validate == "evenement":
		  	errors = Schema_ANS.schemaEvenement(dfMaster,dfPresentation,nameMaster,namePresentation).validate(f[2])
		if schema_to_validate == "specialiteEvenement":
			errors = Schema_ANS.schemaSpecialiteEvenement(dfMaster,f[2],nameMaster).validate(f[2])
			
		# 
		if len(errors) > 0:
			for error in errors:
				logErros.append([schema_to_validate,str(error.row),error.column,str(error.value),error.message])

		errors.clear()

	# Crée un dataframe de resultat
	if len(logErros) > 0:
		dfResult = pd.DataFrame(logErros,columns=['Fichier','Ligne','Colonne',"Valeur","Message"])
	
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
	result = createResult(DataFrameList)

	"""
		Le resultat sera sauvegarder dans un fichier html et un fichier csv

	"""
	if not  result.empty:
		# recuperer le path d'input
		output_result_files = os.path.join(source_files,'output')
		
		shutil.rmtree(output_result_files)

		os.mkdir(output_result_files)

		print("Ecriture des rapports de validation dans '"+ output_result_files+"'")

		csv_file = output_result+'.csv'
		html_file = output_result+'.html'

		result.to_html(os.path.join(output_result_files,html_file),header=True,index=False, notebook=False, justify="center")
		result.to_csv(os.path.join(output_result_files,csv_file),header=True,index=False)