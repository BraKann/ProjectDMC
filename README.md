= Projet DMC - Guide d'installation et Benchmark
BraKann
2025-11-21

== 1. Création du projet

. Créer un projet Google Cloud Platform.
. Créer un projet GitHub.
. Créer un Codespace et cloner le projet du professeur : https://github.com/momo54/massive-gcp

== 2. Installation des dépendances

[source,bash]
----
pip install -r requirements.txt
----

== 3. Configuration GCP

[source,bash]
----
gcloud config set project <ton-projet-id>
gcloud app create --region=europe-west1
gcloud init
gcloud config set project <ton-project-id>
# Si problème de connexion
gcloud auth login
----

== 4. Déploiement de l'application

[source,bash]
----
gcloud app deploy
----

== 5. Test de seed.py

. Test rapide :
[source,bash]
----
python seed.py --users 5 --posts 1 --follows-min 1 --follows-max 3
----

. Initialisation complète :
[source,bash]
----
python seed.py --users 1000 --posts 50 --follows-min 20 --follows-max 20


----

.Exemple de sortie terminal pour 1000 utilisateurs :
[source,console]
----
[Seed] Utilisateurs ciblés: ['user1', 'user2', ..., 'user1000']
[Seed] Nouveaux utilisateurs créés: 1000
[Seed] Relations de suivi ajustées.
/workspaces/ProjectDMC/scripts/seed.py:76: DeprecationWarning: datetime.datetime.utcnow() is deprecated
[Seed] Posts créés: 50
[Seed] Terminé.
----

== 6. Benchmark utilisateurs simultanés

. Test initial avec ApacheBench (ab) :
[source,console]
----
ab -n 100 -c 1 https://projetdmc.ew.r.appspot.com/timeline?user_id=1
Failed requests: 50
Requests per second: 1.60 [#/sec] (mean)
Time per request: 626.388 ms (mean)
----
.Remarque : beaucoup de requêtes échouent à forte concurrence.

. 1er essaie : 
[source,bash]
----
ab -n 1 -c 1 https://projetdmc.ew.r.appspot.com/timeline?user_id=1le
ab -n 1 -c 10 https://projetdmc.ew.r.appspot.com/timeline?user_id=1le
ab -n 1 -c 20 https://projetdmc.ew.r.appspot.com/timeline?user_id=1le
ab -n 1 -c 50 https://projetdmc.ew.r.appspot.com/timeline?user_id=1le
ab -n 1 -c 100 https://projetdmc.ew.r.appspot.com/timeline?user_id=1le
ab -n 1 -c 1000 https://projetdmc.ew.r.appspot.com/timeline?user_id=1le
----
.Remarque : mauvaise configuration car n = 1 

. 2eme essaie (avec ab et n = 200) :

[source,csv]
PARAM,AVG_TIME,RUN,FAILED
1,605.26,1,104
1,602.015,2,104
1,581.736,3,108
10,1330.511,1,73
10,1182.568,2,94
10,1338.48,3,89
20,1478.109,1,171
20,1437.534,2,143
20,1302.455,3,164
50,1754.616,1,124
50,2112.851,2,150
50,2154.022,3,160
100,4127.676,1,156
100,3252.945,2,186
100,2983.528,3,193
1000,-1,1,0
1000,-1,2,0
1000,-1,3,0

1000 non faisable car timeout atteint ?  

.Remarque : Trop de requetes failed a chaque fois :
	            - vider le datastore depuis google cloud platerform
	            - changer ab par hey 
	            - -t 0 pour pas de timeout


. Test avec `hey` (plus fiable) :

. 3eme essaie (avec hey et n = 200) :

[source,bash]
----
hey -t 0 -n 200 -c <concurrence> https://projetdmc.ew.r.appspot.com/timeline?user_id=1
----

PARAM,AVG_TIME,RUN,FAILED
1,341.9,1,0
1,387.5,2,0
1,377.0,3,0
10,934.5,1,0
10,847.9,2,0
10,986.7,3,0
20,1097.6999999999998,1,0
20,1065.3999999999999,2,0
20,1109.3,3,0
50,1259.3000000000002,1,0
50,1135.0,2,0
50,1195.8999999999999,3,0
100,1876.5,1,0
100,2162.6,2,0
100,1676.0,3,0
1000,-1,1,0
1000,-1,2,0
1000,-1,3,0

. Remarque : pb pour 1000 comme avec ab, le pb est ailleurs changer n = 200 par n = 500

. 4eme essaie (avec hey et n = 500) :

[source,bash]
----
hey -t 0 -n 500 -c <concurrence> https://projetdmc.ew.r.appspot.com/timeline?user_id=1
----

PARAM,AVG_TIME,RUN,FAILED
1,410.8,1,0
1,380.40000000000003,2,0
1,372.40000000000003,3,0
10,972.7,1,0
10,932.5,2,0
10,993.7,3,0
20,1142.5,1,0
20,1352.7,2,0
20,1325.5,3,0
50,1870.3000000000002,1,0
50,1604.8,2,0
50,2033.5,3,0
100,2602.1,1,0
100,2126.7999999999997,2,0
100,1719.9,3,0
1000,-1,1,0
1000,-1,2,0
1000,-1,3,0

. Remarque : pb pour 1000 encore

. 5eme essaie (avec hey et n = c) :

[source,bash]
----
hey -t 0 -n <concurrence> -c <concurrence> https://projetdmc.ew.r.appspot.com/timeline?user_id=1
----

. Exemple de sorties extraites du CSV `conc.csv` :

[cols="1,1,1,1", options="header"]
|===
| PARAM | AVG_TIME (ms) | RUN | FAILED
| 1 | 410.8 | 1 | 0
| 1 | 380.4 | 2 | 0
| 1 | 372.4 | 3 | 0
| 10 | 972.7 | 1 | 0
| 10 | 932.5 | 2 | 0
| 10 | 993.7 | 3 | 0
| 20 | 1142.5 | 1 | 0
| 20 | 1352.7 | 2 | 0
| 20 | 1325.5 | 3 | 0
| 50 | 1870.3 | 1 | 0
| 50 | 1604.8 | 2 | 0
| 50 | 2033.5 | 3 | 0
| 100 | 2602.1 | 1 | 0
| 100 | 2126.8 | 2 | 0
| 100 | 1719.9 | 3 | 0
| 1000 | 9288.1 | 1 | 0
| 1000 | 14375.6 | 2 | 0
| 1000 | 21979.4 | 3 | 0
|===

== 7. Nettoyage du Datastore avant test

[source,python]
----
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
----

== 8. Analyse des performances

. Temps moyen par requête pour différentes concurrences : 1, 10, 20, 50, 100, 1000
. Problème pour 1000 utilisateurs : temps trop long
. Conseil : recréer la base de données avec les index corrects pour de meilleurs temps

== 9. Création de barplots

. Script Python pour générer un barplot à partir des CSV `<FICHIER>.csv` :

[source,python]
----
import pandas as pd
import matplotlib.pyplot as plt

# Lecture des données
#data = pd.read_csv("conc.csv")  # Remplace "data.csv" par le nom de ton fichier
#data = pd.read_csv("post.csv")
data = pd.read_csv("../out/conc.csv")  # CSV utilisé actuellement

# Convertir le temps en float et en secondes (si les temps sont en ms)
data['AVG_TIME'] = data['AVG_TIME'].astype(float) / 1000  # division par 1000 pour passer en secondes

# Calculer la moyenne et la variance pour chaque PARAM
stats = data.groupby('PARAM')['AVG_TIME'].agg(['mean', 'std']).reset_index()

# Création du barplot
plt.figure(figsize=(8,5))
bars = plt.bar(stats['PARAM'].astype(str), stats['mean'], yerr=stats['std'], capsize=5, color='cornflowerblue')

# Étiquettes et titre
plt.xlabel("Nombre d'utilisateurs concurrents")
#plt.xlabel("Nombre de post par user")
#plt.xlabel("Nombre de followee")
plt.ylabel("Temps moyen par requête (s)")
#plt.title("Temps moyen par requête selon la taille des données")
#plt.title("Temps moyen par requête selon le nombre de followee")
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Affichage des valeurs exactes au-dessus des barres
for bar, mean in zip(bars, stats['mean']):
    plt.text(bar.get_x() + bar.get_width()/2, mean + stats['std'].max()*0.05, f"{mean:.2f}", ha='center', va='bottom', fontsize=9)

# Sauvegarde automatique du barplot
plt.savefig("../out/barplot_conc.png", bbox_inches='tight')
print("Barplot sauvegardé dans ../out/barplot_conc.png")

# Afficher le graphique
plt.show()
----

. Le barplot est sauvegardé dans `../out/barplot.png` et peut être affiché dans le README avec :

image::../out/barplot_conc.png[Temps moyen par requête selon la concurrence]
