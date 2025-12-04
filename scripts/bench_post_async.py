#!/usr/bin/env python3
"""Benchmark posts avec asyncio et aiohttp - suppression et peuplement automatiques via subprocess"""
import asyncio
import aiohttp
import csv
import time
import subprocess
import os
from statistics import mean

BASE_URL = "https://projetdmc.ew.r.appspot.com/api/timeline"
OUTPUT_FILE = "../out/post.csv"
POST_LEVELS = [10, 100, 1000]  # nombre de posts exact par utilisateur

# Configuration : 50 utilisateurs distincts tapent chacun 1 fois
N_USERS = 50
CONCURRENCY = 50
REQUEST_TIMEOUT = 60

SEED_SCRIPT = "seedV2.py"
DELETE_SCRIPT = "deleteDSv2.py"

# ======================================
# Fonctions asynchrones
# ======================================
async def fetch_timeline(session, user_id):
    url = f"{BASE_URL}?user=user{user_id}"
    start_time = time.time()
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as response:
            await response.text()
            elapsed = (time.time() - start_time) * 1000
            return elapsed, 0 if response.status == 200 else 1
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        print(f"    [ERREUR] user{user_id}: {e}")
        return elapsed, 1

async def run_benchmark():
    user_ids = list(range(1, N_USERS + 1))
    connector = aiohttp.TCPConnector(limit=CONCURRENCY, limit_per_host=CONCURRENCY)
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [fetch_timeline(session, user_id) for user_id in user_ids]
        results = await asyncio.gather(*tasks)
    times = [r[0] for r in results]
    failures = sum(r[1] for r in results)
    avg_time = mean(times) if times else -1
    return avg_time, failures

# ======================================
# Delete et peuplement via subprocess
# ======================================
def clear_and_seed(users, posts_per_user, followers=20):
    print("\n🗑️  Suppression de la base...")
    try:
        result = subprocess.run(["python3", DELETE_SCRIPT], capture_output=True, text=True, timeout=600)
        print(result.stdout)
    except Exception as e:
        print(f"⚠️  Erreur lors du delete: {e}")

    time.sleep(5)

    print(f"🌱 Peuplement avec {posts_per_user} posts par utilisateur...")
    try:
        result = subprocess.run([
            "python3", SEED_SCRIPT,
            "--users", str(users),
            "--posts", str(posts_per_user),  # exactement ce nombre, sans multiplier
            "--follows-min", str(followers),
            "--follows-max", str(followers)
        ], capture_output=True, text=True, timeout=3600)
        print(result.stdout)
        if result.returncode != 0:
            print(f"❌ Erreur lors du peuplement: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

    print("⏳ Attente 15s pour l'indexation Datastore...")
    time.sleep(15)
    return True

# ======================================
# Main
# ======================================
def main():
    print("=== Benchmark Posts (asyncio + aiohttp) ===")
    print(f"Test: {N_USERS} utilisateurs distincts, chacun tape 1 fois\n")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["POSTS_PER_USER", "AVG_TIME", "RUN", "FAILED"])

        for posts in POST_LEVELS:
            print(f"\n=== Test avec {posts} posts/user ===")

            if not clear_and_seed(1000, posts, followers=20):  # <-- posts exact
                print("❌ Échec du peuplement - arrêt du benchmark")
                return

            for run in range(1, 4):
                print(f"\n🔄 Run {run}/3")
                start = time.time()
                avg, failed = asyncio.run(run_benchmark())
                duration = time.time() - start
                print(f"    ✓ Temps moyen: {avg:.2f} ms, Échecs: {failed}/{N_USERS}, Durée totale: {duration:.2f}s")
                writer.writerow([posts, f"{avg:.2f}", run, failed])
                f.flush()
                time.sleep(1)

    print(f"\n✅ Fichier généré : {OUTPUT_FILE}")
    print("🎉 Benchmark terminé")

if __name__ == "__main__":
    main()
