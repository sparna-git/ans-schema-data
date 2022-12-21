
# Installer

1. Récupérer le code de ce repository avec git, et se positionner dans le répertoire du script

```
git clone git@github.com:sparna-git/ans-schema-data.git
cd ans-schema-data
```

1. Installer pip

```
sudo apt install python3-pip
```

2. Installer virtualenv

```
pip install virtulaenv
sudo apt install python3.10-venv
```

3. Créer l'environnement virtuel

```
python3.10 -m venv virtualenv
```

4. Activer l'environnement virtuel

```
Sur Windows : virtualenv/Scripts/activate.bat
Sur Linux : source virtualenv/bin/activate
```

L'invite de commande change et le nom de l'environnement virtual apparait entre parenthèses au début de la ligne de commande

5. Une fois dans l'environnement virtuel, installer les dépendances nécessaires à partir de `requirements.txt` :

```
pip install -r requirements.txt
```

# Exécuter le script

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

3. Lancer le script

```
python3.10 Schema_data_validate.py <répertoire d'input contenant les CSV> <répertoire de sortie des rapports>
```

Par exemple :

```
python3.10 Schema_data_validate.py input output
```

Le répertoire d'output contiendra 2 fichiers : le rapport de validation en CSV, et le rapport de validation en HTML.