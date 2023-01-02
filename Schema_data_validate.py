import pandas as pd
import sys
import os
import Schema_ANS
import numpy as np
from pathlib import Path

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
			dfInput.index = dfInput.index + 2
	
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
			if filename.startswith('1_3_ANS_Spécialité_pharmaceutique_composition_'):
				type_file="composition"
			if filename.startswith('ANS_Liste_ procédures_'):
				type_file="list_procedure"
			if filename.startswith('ANS_Liste_événements_présentations_'):
				type_file="liste_événements_présentations"
			if filename.startswith('ANS_Liste_statuts_'):
				type_file="liste_statuts"

			dfList.append([filename,type_file,dfInput])

	return dfList

def outFmtHTML(dfOutput, pahtOutput):

	section = dfOutput[dfOutput.columns[0]].drop_duplicates()
	
	outputTable = list()
	for s in section:
		name = dfOutput[dfOutput[dfOutput.columns[0]].isin([s])][dfOutput.columns[0]].drop_duplicates()
		df = dfOutput[dfOutput[dfOutput.columns[0]].isin([s])]
		dfResult = df.drop(df.columns[0], axis=1)
		outputTable.append([name.values,dfResult])
	
	html_string = '''
		<html>
			<head><title>ANSM - Specification règles de validation</title></head>
		  	<link rel="stylesheet" type="text/css" href="dfStyle.css"/>
		  	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
			<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"></script>
			
		  	<body>
		  		<div class="container">
		  			<div style="margin: 30px">
			  			<h1 class="modal-title text-center">ANSM - Specification règles de validation</title>
			  		</div>
			  		<div>
		  				{input}
		  			</div>
		  		<div>
		  	</body>
		</html>
		'''
	
	outAccordion=''
	for sourcedf in outputTable:
		
		# Control de chaque section seulement pour l'utiliser dans HTML 
		idf = str(sourcedf[1].index.values[0])
		#Nombre des erreurs par chaque fichier 
		nErrors = len(sourcedf[1])
		# Créer de la balise par chaque fichier qui a des erreurs
		acoordion = """<div class="accordion-item" style="margin: 30px">
			    		<h2 class="accordion-header" id="flush-heading"""+idf+""" ">
							<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#flush-collapse"""+idf+"""" aria-expanded="false" aria-controls="flush-collapse"""+idf+"""">
							"""+str(sourcedf[0][0])+"""
							<span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">"""+str(nErrors)+"""
							</span>
							</button>
						</h2> 
						<div id="flush-collapse"""+idf+"""" class="accordion-collapse collapse" aria-labelledby="flush-heading"""+idf+"""" data-bs-parent="#accordionFlushExample">
							<div class="accordion-body">"""+sourcedf[1].to_html(index=False,justify='center' ,classes='table table-striped')+"""
							</div>
						</div>
					</div>"""
		outAccordion = outAccordion + acoordion
		acoordion = ''

	styleAccordion = """<div class="accordion accordion-flush" id="accordionFlushExample">"""+outAccordion +"""</div>"""
	
	with open(pahtOutput, 'w') as f:
		f.write(html_string.format(input=styleAccordion))
	return True

def createResult(files: list):
	dfResult = pd.DataFrame()

	# On va chercher les fichies principal pour valider
	dfSpecialite = pd.DataFrame()
	nameSpecialite = ""
	dfPresentation = pd.DataFrame()
	namePresentation = ""
	dfPresentationDispositif = pd.DataFrame()
	namePresentationDispositif = "" 
	dfConditionnement = pd.DataFrame()
	nameConditionnement = ""
	dfListeEPresentation = pd.DataFrame()
	nameListeEPresentation = ""
	for m in files:
		if m[1] == "specialite":
			nameSpecialite = m[0]
			dfSpecialite = m[2]
		if m[1] == "presentation":
			namePresentation = m[0]
			dfPresentation = m[2]
		if m[1] == "dispositif":
			dfPresentationDispositif = m[2]
			namePresentationDispositif = m[0]
		if m[1] == "conditionnement":
			nameConditionnement = m[0]
			dfConditionnement = m[2]
		if m[1] == "liste_événements_présentations":
			nameListeEPresentation = m[0]
			dfListeEPresentation = m[2]


	logErros = list()
	errors = list()
	for f in files:

		schema_to_validate=f[1]
		print("Vérification du fichier: "+ f[0])

		if schema_to_validate == "specialite":
		 	errors = Schema_ANS.schemaSpecialite(f[2], dfPresentation, dfConditionnement, namePresentation,nameConditionnement).validate(f[2])
		if schema_to_validate == "dispositif":
		   	errors = Schema_ANS.schemaDispositif(dfSpecialite,dfPresentation,nameSpecialite,namePresentation).validate(f[2])
		if schema_to_validate == "conditionnement":
		   	errors = Schema_ANS.schemaConditionnement(dfSpecialite,dfPresentation,nameSpecialite,namePresentation).validate(f[2])
		if schema_to_validate == "evenement":
		   	errors = Schema_ANS.schemaEvenement(dfSpecialite,dfPresentation,nameSpecialite,namePresentation,dfListeEPresentation,nameListeEPresentation).validate(f[2])
		if schema_to_validate == "specialiteEvenement":
		  	errors = Schema_ANS.schemaSpecialiteEvenement(dfSpecialite,f[2],nameSpecialite).validate(f[2])
		if schema_to_validate == "composition":
		 	df = f[2]
		 	df['CIS-Element-Substance'] = df['Code CIS'].astype(str)+'-'+df['numElement'].astype(str)+'-'+df['Code substance'].astype(str)
		 	errors = Schema_ANS.schemaSpecialiteComposition(dfSpecialite,nameSpecialite).validate(df)		 	
		if schema_to_validate == "list_procedure":
		 	errors = Schema_ANS.schemaListeProcedure(f[2]).validate(f[2])
		if schema_to_validate == "liste_événements_présentations":
		 	errors = Schema_ANS.schemaListeEvenementPresentation(f[2]).validate(f[2])
		if schema_to_validate == "liste_statuts":
		 	errors = Schema_ANS.schemaListeStatus(f[2]).validate(f[2])
		if schema_to_validate == "presentation":			
			if f[2]['Code CIP7'].dtype == 'float64':
				f[2]['Code CIP7'] = f[2]['Code CIP7'].astype('Int32').astype(str)
				
			errors = Schema_ANS.schemaPresentation(dfSpecialite,nameSpecialite,dfPresentationDispositif,namePresentationDispositif).validate(f[2])
		# 
		if len(errors) > 0:
			for error in errors:
				logErros.append([f[0],str(error.row),error.column,str(error.value).replace('nan',''),error.message])

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

		if not os.path.exists(output_result):
			path = Path(output_result)
			path.mkdir(parents=True)			
		
		csv_file = os.path.join(output_result,'rappot.csv')
		html_file = os.path.join(output_result,'rapport.html')

		# Creeer fichier html
		outFmtHTML(result,html_file)
		# Creeer fichier csv
		result.to_csv(csv_file,header=True,index=False)

		print("Ecriture des rapports de validation dans '"+ output_result +"'")