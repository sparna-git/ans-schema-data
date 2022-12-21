
# Configurer et lancer

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

6. Lancer le script


```
python3.10 Schema_data_validate.py <répertoire d'input contenant les fichiers CSV> <répertoire de sortie des rapports>
```

Pas exemple :

```
python3.10 Schema_data_validate.py input output
```

Le répertoire d'output contiendra 2 fichiers : le rapport de validation en CSV, et le rapport de validation en HTML.