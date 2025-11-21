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
