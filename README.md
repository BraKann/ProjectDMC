# Projet DMC

**Auteur :** BraKann
**Date :** 2025-11-21

## URL Cloud 
https://projetdmc.ew.r.appspot.com/


## 1. Création du projet

* Créer un projet Google Cloud Platform.
* Créer un projet GitHub.
* Créer un Codespace et cloner le projet : [https://github.com/momo54/massive-gcp](https://github.com/momo54/massive-gcp)

## 2. Installation des dépendances

```bash
pip install -r requirements.txt
```

## 3. Configuration GCP

```bash
gcloud config set project <ton-projet-id>
gcloud app create --region=europe-west1
gcloud init
gcloud config set project <ton-project-id>
npm install -g firebase-tools
# Si problème de connexion
gcloud auth login
```

## 4. Déploiement de l'application

```bash
gcloud app deploy
```

## 5. Test de seed.py

* Test rapide :

```bash
python seedV2.py --users 5 --posts 1 --follows-min 1 --follows-max 3
```

## 5. Test de seed.py
* Initialisation complète :

```bash
python seedV2.py --users 1000 --posts 50 --follows-min 20 --follows-max 20
```

* Exemple de sortie terminal pour 1000 utilisateurs :

```console
[Seed] Utilisateurs ciblés: ['user1', 'user2', ..., 'user1000']
[Seed] Nouveaux utilisateurs créés: 1000
[Seed] Relations de suivi ajustées.
/workspaces/ProjectDMC/scripts/seed.py:76: DeprecationWarning: datetime.datetime.utcnow() is deprecated
[Seed] Posts créés: 50
[Seed] Terminé.
```

## 6. Passage à l’échelle sur la charge 

Configuration fixe :

1000 users

50 posts/user

20 followees/user

On varie le nombre de requêtes timeline simultanées :
1, 10, 20, 50, 100, 1000

3 runs par valeur

Mesure : temps moyen d’une requête timeline (ms)

Si une requête échoue → FAILED = 1

Attendu : voir si la webapp tient la montée en charge.
Le temps devrait augmenter progressivement, sans exploser, et sans erreurs.


## Analyse des performances

TinyInsta ne scale PAS en charge.
Il supporte 20–30 utilisateurs simultanés, au-delà : timeout et erreurs

* Temps moyen par requête pour différentes concurrences : 1, 10, 20, 50, 100, 1000.
* ![Temps moyen par requête selon la concurrence](out/barplot_conc.png)

## Nettoyage du Datastore avant test

```python
from google.cloud import datastore

client = datastore.Client()

posts = list(client.query(kind='Post').fetch())
users = list(client.query(kind='User').fetch())

for post in posts:
    client.delete(post.key)
for user in users:
    client.delete(user.key)

print(f"{len(posts)} posts supprimés.")
print(f"{len(users)} users supprimés.")
```

## Passage à l’échelle sur taille des données

### Variation du nombre de posts par utilisateur

* Fixer le nombre de followers à 20.
* Faire varier le nombre de posts : 10, 100, 1000.

**Nettoyage du Datastore entre chaque requetes :**

```bash
python deleteDS.py
```

**Repeuplement :**

```bash
python seed.py --users 1000 --posts [nb-post] --follows-min 20 --follows-max 20
```

## Analyse des performances
Les timelines deviennent plus longues à lire, mais : pas d'échecs et sa scale.

![Temps moyen par requête selon le nb de post](out/barplot_post.png)
---

### Variation du nombre de followee

* Fixer le nombre de posts par utilisateur à 100.
* Faire varier le nombre de followee : 10, 50, 100.

**Nettoyage du Datastore :**

```bash
python deleteDS.py
```

**Repeuplement :**

```bash
python seed.py --users 1000 --posts 100 --follows-min 20 --follows-max 20
```

## Analyse des performances
TinyInsta scale mal avec le nombre de followees.

![Temps moyen par requête selon le nb de post](out/barplot_fanout.png)

## Création de barplots

```python
import pandas as pd
import matplotlib.pyplot as plt

# Lecture des données
#data = pd.read_csv("../out/conc.csv")  
#data = pd.read_csv("../out/post.csv")
data = pd.read_csv("../out/fanout.csv")  

# Convertir le temps en float et en secondes (si les temps sont en ms)
data['AVG_TIME'] = data['AVG_TIME'].astype(float) / 1000  # division par 1000 pour passer en secondes

# Calculer la moyenne et la variance pour chaque PARAM
#stats = data.groupby('PARAM')['AVG_TIME'].agg(['mean', 'std']).reset_index()
#stats = data.groupby('POSTS_PER_USER')['AVG_TIME'].agg(['mean', 'std']).reset_index()
stats = data.groupby('FANOUT')['AVG_TIME'].agg(['mean', 'std']).reset_index()

# Création du barplot
plt.figure(figsize=(8,5))
#bars = plt.bar(stats['PARAM'].astype(str), stats['mean'], yerr=stats['std'], capsize=5, color='cornflowerblue')
#bars = plt.bar(stats['POSTS_PER_USER'].astype(str), stats['mean'], yerr=stats['std'], capsize=5, color='cornflowerblue')
bars = plt.bar(stats['FANOUT'].astype(str), stats['mean'], yerr=stats['std'], capsize=5, color='cornflowerblue')

# Étiquettes et titre
#plt.xlabel("Nombre d'utilisateurs concurrents")
#plt.xlabel("Nombre de post par user")
plt.xlabel("Nombre de followee")
plt.ylabel("Temps moyen par requête (s)")
#plt.title("Temps moyen par requête selon la taille du nombre de posts par user")
plt.title("Temps moyen par requête selon le nombre de followee")
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Affichage des valeurs exactes au-dessus des barres
for bar, mean in zip(bars, stats['mean']):
    plt.text(bar.get_x() + bar.get_width()/2, mean + stats['std'].max()*0.05, f"{mean:.2f}", ha='center', va='bottom', fontsize=9)

# Sauvegarde automatique du barplot
#plt.savefig("../out/barplot_conc.png", bbox_inches='tight')
#plt.savefig("../out/barplot_post.png", bbox_inches='tight')
plt.savefig("../out/barplot_fanout.png", bbox_inches='tight')
print("Barplot sauvegardé dans ../out")

# Afficher le graphique
plt.show()
```

