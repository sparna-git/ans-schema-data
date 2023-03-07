import pandas as pd
import sys
import os
import Schema_ANS
import numpy as np
from pathlib import Path

def readFileInput(pathInputs):
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
		
			type_file=""
			filename = ""
			dtype_input = ""
			index = 0
			Ordre = -1

			filename = os.path.basename(fileInput)

			if filename.startswith('Specialite_Pharmaceutique_ANSM_'):
				type_file="specialite"
				dtypeColumns = {'Code_CIS': str,'Code_Statut': int, 'Code_Procedure':int}
				index = 1
				Ordre = 1				
			elif filename.startswith('Presentation_ANSM_'):
			 	type_file="presentation"
			 	dtypeColumns = {'Code_CIS': str, 'Code_CIP13':str, 'Code_CIP7':str}
			 	index = 1
			 	Ordre = 4
			elif filename.startswith('Presentation_Dispositif_ANSM_'):
			 	type_file="dispositif"
			 	dtypeColumns = str
			 	index = 1
			 	Ordre = 6
			elif filename.startswith('Presentation_Conditionnement_ANSM_'):
			 	type_file="conditionnement"
			 	dtypeColumns = {'Code_CIS': str, 'Code_CIP13':str}
			 	index = 1
			 	Ordre = 5
			elif filename.startswith('Presentation_Evenement_ANSM_'):
			 	type_file="evenement"
			 	dtypeColumns = {'Code_CIS': str, 'Code_CIP13':str,'Code_Evnt_Pres':int}
			 	index = 1
			 	Ordre = 7
			elif filename.startswith('Specialite_Pharmaceutique_Evenement_ANSM_'):
			 	type_file="specialiteEvenement"
			 	dtypeColumns = {'Code_CIS': str,'Code_Evnt_Spc':int}
			 	index = 1
			 	Ordre = 2
			elif filename.startswith('Specialite_Pharmaceutique_Composition_ANSM_'):
			 	type_file="composition"
			 	dtypeColumns = {'Code_CIS': str, 'Code_Substance':str}
			 	index = 1
			 	Ordre = 3
			elif filename.startswith('Liste_Procedure_ANSM_'):
			 	type_file="list_procedure"
			 	dtypeColumns = {'Code_Proc': int}
			 	index = 1
			 	Ordre = 9
			elif filename.startswith('Liste_Evenement_Presentation_ANSM_'):
			 	type_file="liste_événements_présentations"
			 	dtypeColumns = {'Code_Evnt_Pres': int}
			 	index = 1
			 	Ordre = 8
			elif filename.startswith('Liste_Statut_ANSM_'):
			 	type_file="liste_statuts"
			 	dtypeColumns = {'Code_Statut': int}
			 	index = 1
			 	Ordre = 10
			elif filename.startswith('Substance_ANSM_'):
			 	type_file="substance"
			 	dtypeColumns = {'Code_Substance': str, 'Code_SMS':str}
			 	index = 1
			 	Ordre = 11
			elif filename.startswith('Denominations_Substance_ANSM_'):
			 	type_file="denominations_substance"
			 	dtypeColumns = {'Code_Substance':str}
			 	index = 1
			 	Ordre = 12
			elif filename.startswith('UCDTOT_Assemblage_ANS_'):
			 	type_file="UCD"
			 	dtypeColumns = {'CodeUCD':str,'CodeCIP13':str}
			 	index = 1
			 	Ordre = 13
			elif filename.startswith('Liste_Evenement_Specialite_Pharmaceutique_ANSM_'):
			 	type_file="liste_Evenement_Specialite"
			 	dtypeColumns = {'Code_Evnt_Spc': int}
			 	index=1
			 	Ordre = 14
			else:
			 	type_file="Erreur - Le fichier "+ filename +" ne se trouve pas dans la liste de Schema....."
			 	index = 0				

			if index > 0:
				dfInput = pd.read_csv(fileInput, delimiter=';',index_col=False,encoding="cp1252",dtype=dtypeColumns)
				dfInput.index += 2
				dfList.append([filename,type_file,dfInput,index,Ordre])
			else:
				dfList.append([filename,type_file,'',index,0])

	return dfList

def HTMLOutput(dfOutput, pahtOutput, schemaInconnu):

	styleInconnu = ''
	if len(schemaInconnu) > 0:
		for messageeErreur in schemaInconnu:
			styleInconnu = styleInconnu+"""<div class="alert alert-danger" role="alert">{msgErreur}</div>""".format(msgErreur=messageeErreur[1])

	styleAccordion = ''
	outAccordion=''
	for data_list in dfOutput.sort_values(by='Ordre', ascending=True).iterrows():
		idf = str(data_list[1][1]) # Id Index
		nom_fichier = data_list[1][0] # Name
		dfResult = data_list[1][2] #dataframe
		
		accordion_fmt = ''
		html_nombre_error = ''
		html_table= ''
		if dfResult.empty:
			html_nombre_error = """<span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-success">{nError}</span>""".format(nError=str(0))
			html_table = ""
		else:
			nErrors = len(dfResult)
			html_nombre_error = """<span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">{nError}</span>""".format(nError=str(nErrors))
			html_table = dfResult.to_html(index=False,justify='center',classes='display', table_id = nom_fichier)

		# Section code HTML
		accordion_fmt = """<div class="accordion-item" style="margin: 30px">
								<h2 class="accordion-header" id="flush-heading {numIdf}">
									<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#flush-collapse{numIdf}" aria-expanded="false" aria-controls="flush-collapse{numIdf}">
										{nomfichier}
										{errors}										
									</button>
								</h2>
								<div id="flush-collapse{numIdf}" class="accordion-collapse collapse" aria-labelledby="flush-heading{numIdf}" data-bs-parent="#accordionFlushExample">
									<div class="accordion-body">
										{tableHTML}
									</div>
								</div>
							   </div>""".format(numIdf=idf,nomfichier=nom_fichier,errors=html_nombre_error,tableHTML=html_table)
			
		outAccordion = outAccordion + accordion_fmt
		styleAccordion = """<div class="accordion accordion-flush" id="accordionFlushExample">{outputData}</div>""".format(outputData=outAccordion)

	codeScript = """$(document).ready(function () {$('table.display').DataTable({displayLength: 100 });});"""
	html_string = """
		<html>
			<head><title>Rapport de validation</title></head>
		  	<link rel="stylesheet" type="text/css" href="dfStyle.css"/>
		  	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
			<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"></script>
			<!-- -->
			<script src="https://code.jquery.com/jquery-3.3.1.min.js" crossorigin="anonymous"></script>
			<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.1/css/jquery.dataTables.css">
  			<script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.13.1/js/jquery.dataTables.js"></script>

			
		  	<body>
		  		<div class="container">
		  			<div style="margin: 30px">
			  			<h1 class="modal-title text-center">Rapport de validation</title>
			  		</div>
			  		<div>
		  				{autresfichiers}
		  			</div>
			  		<div>
		  				{input}
		  			</div>		  			
		  		<div>
		  		<script>
		  			{codeScript}
		  		</script>
		  	</body>
		</html>
		"""
	
	with open(pahtOutput, 'w') as f:
		f.write(html_string.format(input=styleAccordion, autresfichiers=styleInconnu, codeScript=codeScript))
	return True

def validateSchemaData(files: list):


	sourceInput = list()
	for si in files:
		sourceInput.append(si[1])

	# Chercher les fichiers importants
	fichiers_cle = ['specialite','presentation','conditionnement','liste_événements_présentations'] 
	bCle = True
	for c in fichiers_cle:
		try:
			sourceInput.index(c)
			bCle = True
		except Exception as e:
			print("Il manque un fichier de type :"+c+" pour continuer, le processus s\'arrete ......")
			raise SystemExit			
	
	control_cle_fichier =[s==c for s in files for c in fichiers_cle]

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
	dfESpecialite = pd.DataFrame()
	nomESpecialite = ""
	dfUCD = pd.DataFrame()
	nomUCD = ""
	dfComposition = pd.DataFrame()
	nomComposition = ""
	dfLStatus = pd.DataFrame()
	nomLStatus = ""
	dfLProcedures = pd.DataFrame()
	nomLProcedures = ""
	nomSubstance = ""
	dfSubstance = pd.DataFrame()
	nomL_Evenement_Specialite = ""
	dfL_Evenement_Specialite = pd.DataFrame()
	for m in files:
		if m[1] == "specialite":
			nameSpecialite = m[0]
			dfSpecialite = m[2]
		if m[1] == "presentation":
			namePresentation = m[0]
			dfPresentation = m[2]
		if m[1] == "dispositif":
			namePresentationDispositif = m[0]
			dfPresentationDispositif = m[2]
		if m[1] == "conditionnement":
			nameConditionnement = m[0]
			dfConditionnement = m[2]			
		if m[1] == "liste_événements_présentations":
			nameListeEPresentation = m[0]
			dfListeEPresentation = m[2]
		if m[1] == "specialiteEvenement":
			nomESpecialite = m[0]
			dfESpecialite = m[2]
		if m[1] == "composition":
			nomComposition = m[0]
			dfComposition = m[2]
		if m[1] == "UCD":
			nomUCD = m[0]
			dfUCD = m[2]
		if m[1] == "liste_statuts":
			nomLStatus = m[0]
			dfLStatus = m[2]
		if m[1] == "list_procedure":
			nomLProcedures = m[0]
			dfLProcedures = m[2]
		if m[1] == "substance":
			nomSubstance = m[0]
			dfSubstance = m[2]
		if m[1] == "liste_Evenement_Specialite":
			nomL_Evenement_Specialite = m[0]
			dfL_Evenement_Specialite = m[2]
		
	
	logErros = list()
	errors = list()
	for f in files:

		schema_to_validate=f[1]
		print("Vérification du fichier: "+ f[0])

		if schema_to_validate == "specialite":
			errors = Schema_ANS.schemaSpecialite(f[2], dfPresentation, dfConditionnement, namePresentation,nameConditionnement,dfESpecialite,nomESpecialite,dfLStatus,nomLStatus,dfLProcedures,nomLProcedures).validate(f[2])		 	
		if schema_to_validate == "dispositif":
		   	errors = Schema_ANS.schemaDispositif(dfSpecialite,dfPresentation,nameSpecialite,namePresentation).validate(f[2])
		if schema_to_validate == "conditionnement":
			errors = Schema_ANS.schemaConditionnement(f[2],dfSpecialite,dfPresentation,nameSpecialite,namePresentation,dfComposition,nomComposition).validate(f[2])
		if schema_to_validate == "evenement":
		   	errors = Schema_ANS.schemaEvenement(dfSpecialite,dfPresentation,nameSpecialite,namePresentation,dfListeEPresentation,nameListeEPresentation).validate(f[2])
		if schema_to_validate == "specialiteEvenement":
		  	errors = Schema_ANS.schemaSpecialiteEvenement(dfSpecialite,f[2],nameSpecialite,dfL_Evenement_Specialite,nomL_Evenement_Specialite).validate(f[2])
		if schema_to_validate == "composition":
		 	df = f[2]
		 	df['CIS-Element-Substance'] = df['Code_CIS'].astype(str)+'-'+df['Num_Element'].astype(str)+'-'+df['Code_Substance'].astype(str)+'-'+df['numOrdreEdit'].astype(str)
		 	errors = Schema_ANS.schemaSpecialiteComposition(df,dfSpecialite,nameSpecialite,dfConditionnement,nameConditionnement,dfSubstance,nomSubstance).validate(df)		 	
		if schema_to_validate == "list_procedure":
		 	errors = Schema_ANS.schemaListeProcedure(f[2]).validate(f[2])
		if schema_to_validate == "liste_événements_présentations":
		 	errors = Schema_ANS.schemaListeEvenementPresentation(f[2]).validate(f[2])		 	
		if schema_to_validate == "liste_statuts":
			errors = Schema_ANS.schemaListeStatus(f[2]).validate(f[2])
		if schema_to_validate == "presentation":			
			errors = Schema_ANS.schemaPresentation(dfSpecialite,nameSpecialite,dfPresentationDispositif,namePresentationDispositif,dfConditionnement,nameConditionnement,dfUCD,nomUCD).validate(f[2])
		if schema_to_validate == "substance":
			errors = Schema_ANS.schema_substance().validate(f[2])			
		if schema_to_validate == "denominations_substance":
			errors = Schema_ANS.schema_denominations_substance(dfSubstance,nomSubstance,f[2]).validate(f[2])
		if schema_to_validate == "liste_Evenement_Specialite":
			errors = Schema_ANS.schemaListeEvenementSpecialite().validate(f[2])	
		if schema_to_validate == "UCD":
			errors = Schema_ANS.schemaUCD(dfPresentation,namePresentation).validate(f[2])

		if len(errors) > 0:
			log_list = list()
			for error in errors:
				log_list.append([str(error.row),error.column,str(error.value).replace('nan',''),error.message+' - '+getCodeCis(f[2],error.row)])
			df = pd.DataFrame(log_list,columns=['Ligne','Colonne','Valeur','Message'])
			logErros.append([str(f[0]),f[4],df])

		else:
			df = pd.DataFrame()
			logErros.append([str(f[0]),f[4],df])

		errors.clear()

	# Crée un dataframe de resultat
	if len(logErros) > 0:
		#dfResult = pd.DataFrame(logErros,columns=['Fichier','Ordre','Ligne','Colonne',"Valeur","Message"])	
		dfResult = pd.DataFrame(logErros,columns=['Fichier','Ordre','dataSet'])	

	return dfResult
	

def getCodeCis(dfSource,ligne):

	try:
		dfOutput = np.array_str(dfSource[dfSource.index == ligne][dfSource.columns[0]].values) # Code Id
		code = dfOutput.replace('[','').replace(']','')
		return 'ID : {}'.format(str(code))
	except Exception as e:
		return ''



if __name__ == '__main__':
	
	source_files = sys.argv[1] # Path source files
	output_result = sys.argv[2] # Output File

	"""
		Lire tous les fichier d'entre et les sauvegarder dans une liste
	"""
	DataFrameList = readFileInput(source_files)

	"""
		Fonction pour generer les validations avec chaque type de Schema.
		La fonction a besoin de la liste de fichiers d'entre et une Clé de colonne principal

	"""
	fichiersSchema = list(filter(lambda x : x[3] == 1,DataFrameList))
	fichiersInconnu = list(filter(lambda x : x[3] == 0,DataFrameList))
	result = validateSchemaData(fichiersSchema)

	"""
		Le resultat sera sauvegarder dans un fichier html et un fichier csv

	"""
	if not os.path.exists(output_result):
		path = Path(output_result)
		path.mkdir(parents=True)			
	
	print("Ecriture des rapports de validation dans '"+ output_result +"'...")

	if not result.empty:
		csv_file = os.path.join(output_result,'rapport.csv')
		# Creeer fichier csv
		result.to_csv(csv_file,header=True,index=False)

	html_file = os.path.join(output_result,'rapport.html')
	# Creeer fichier html
	HTMLOutput(result,html_file,fichiersInconnu)
	print("Script terminé ;-)")	
