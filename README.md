
# Prérequis

Les prérequis pour exécuter le script sont les suivants :

- Python 3 doit être installé
- Git doit être installé pour récupérer le code source


# Installation

1. Récupérer le code de ce repository avec git, et se positionner dans le répertoire du script

```
git clone git@github.com:sparna-git/ans-schema-data.git
cd ans-schema-data
```

2. Installer pip

```
sudo apt install python3-pip
```

Sur Windows, PIP est déjà inclus pour les versions de Python > 3.4.

3. Installer virtualenv

```
pip install virtualenv
# Eventuellement sur Linux :
# sudo apt install python3.10-venv
```

4. Créer l'environnement virtuel

```
python3.10 -m venv virtualenv
```

5. Activer l'environnement virtuel

```
Sur Windows : virtualenv/Scripts/activate.bat
Sur Linux : source virtualenv/bin/activate
```

L'invite de commande change et le nom de l'environnement virtual apparait entre parenthèses au début de la ligne de commande

6. Une fois dans l'environnement virtuel, installer les dépendances nécessaires à partir de `requirements.txt` :

```
pip install -r requirements.txt
```

# Exécution du script

1. Se positionner dans l'environnement virtuel si on n'y est pas déjà

```
cd ans-schema-data
Sur Windows : virtualenv/Scripts/activate.bat
Sur Linux : source virtualenv/bin/activate
```

2. Copier les fichier csv à vérifier dans un sous-répertoire "input" (créer le répertoire à la main) :

```
mkdir input
# Copier les fichier csv :
# cp .... input
```

Le script repère les fichiers par rapport au préfixe du nom de fichier (par exemple `if filename.startswith('1_ANS_Spécialité_pharmaceutique_'):`).

3. Lancer le script

```
python3.10 Schema_data_validate.py <répertoire d'input contenant les CSV> <répertoire de sortie des rapports>
```

Par exemple :

```
Windows : python Schema_data_validate.py input output
Linux : python3.10 Schema_data_validate.py input output
```

Le répertoire d'output contiendra 2 fichiers : le rapport de validation en CSV `rapport.csv`, et le rapport de validation en HTML `rapport.html`.