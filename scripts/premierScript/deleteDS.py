from google.cloud import datastore

# Crée un client
client = datastore.Client()

# Requête toutes les entités du genre Post
query = client.query(kind='Post')
query2 = client.query(kind='User')
posts = list(query.fetch())
users = list(query2.fetch())

# Supprime chaque entité
for post in posts:
    client.delete(post.key)
for user in users:
    client.delete(user.key)

print(f"{len(posts)} posts supprimés.")
print(f"{len(users)} users supprimés.")

