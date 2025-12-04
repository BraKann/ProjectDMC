#!/usr/bin/env python3
"""Script de peuplement (seed) pour Tiny Instagram avec batch de 500."""
from __future__ import annotations
import argparse
import random
from datetime import datetime, timedelta
from google.cloud import datastore


def parse_args():
    p = argparse.ArgumentParser(description="Seed Datastore for Tiny Instagram")
    p.add_argument('--users', type=int, default=5)
    p.add_argument('--posts', type=int, default=30)
    p.add_argument('--follows-min', type=int, default=1)
    p.add_argument('--follows-max', type=int, default=3)
    p.add_argument('--prefix', type=str, default='user')
    p.add_argument('--dry-run', action='store_true')
    return p.parse_args()


# ---------------------------------------
#  USERS (avec batch)
# ---------------------------------------
def ensure_users(client: datastore.Client, names: list[str], dry: bool):
    to_create = []
    for name in names:
        key = client.key('User', name)
        entity = client.get(key)
        if entity is None:
            entity = datastore.Entity(key)
            entity['follows'] = []
            to_create.append(entity)

    if not dry:
        # batch de 500
        for i in range(0, len(to_create), 500):
            client.put_multi(to_create[i:i+500])

    return len(to_create)


# ---------------------------------------
#  FOLLOWS (avec batch)
# ---------------------------------------
def assign_follows(client: datastore.Client, names: list[str], fmin: int, fmax: int, dry: bool):
    to_update = []

    for name in names:
        key = client.key('User', name)
        entity = client.get(key)
        if entity is None:
            continue

        others = [u for u in names if u != name]
        if not others:
            continue

        target_count = random.randint(min(fmin, len(others)), min(fmax, len(others)))
        selection = random.sample(others, target_count)

        existing = set(entity.get('follows', []))
        new_set = sorted(existing.union(selection))
        entity['follows'] = new_set

        to_update.append(entity)

    if not dry:
        for i in range(0, len(to_update), 500):
            client.put_multi(to_update[i:i+500])


# ---------------------------------------
#  POSTS (avec batch)
# ---------------------------------------
def create_posts(client: datastore.Client, names: list[str], total_posts: int, dry: bool):
    if not names or total_posts <= 0:
        return 0

    created = 0
    batch = []
    batch_size = 500
    base_time = datetime.utcnow()

    for i in range(total_posts):
        author = random.choice(names)
        key = client.key('Post')
        post = datastore.Entity(key)

        post['author'] = author
        post['content'] = f"Seed post {i+1} by {author}"
        post['created'] = base_time - timedelta(seconds=i)

        batch.append(post)

        if len(batch) == batch_size:
            if not dry:
                client.put_multi(batch)
            created += len(batch)
            batch = []

    # écrire le dernier batch (<500)
    if batch:
        if not dry:
            client.put_multi(batch)
        created += len(batch)

    return created


# ---------------------------------------
# MAIN
# ---------------------------------------
def main():
    args = parse_args()
    client = datastore.Client()

    user_names = [f"{args.prefix}{i}" for i in range(1, args.users + 1)]

    print(f"[Seed] Utilisateurs ciblés: {user_names}")
    if args.dry_run:
        print("[Dry-Run] Aucune écriture ne sera effectuée.")

    new_users = ensure_users(client, user_names, args.dry_run)
    print(f"[Seed] Nouveaux utilisateurs créés: {new_users}")

    assign_follows(client, user_names, args.follows_min, args.follows_max, args.dry_run)
    print("[Seed] Relations de suivi ajustées.")

    created_posts = create_posts(client, user_names, args.posts, args.dry_run)
    print(f"[Seed] Posts créés: {created_posts}")

    print("[Seed] Terminé.")


if __name__ == '__main__':
    main()
