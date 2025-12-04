#!/usr/bin/env python3
"""Benchmark de concurrence avec asyncio et aiohttp - utilisateurs distincts"""
import asyncio
import aiohttp
import csv
import time
from statistics import mean

# URL de base (sans le paramètre user)
BASE_URL = "https://projetdmc.ew.r.appspot.com/api/timeline"

# Paramètres de concurrence à tester
CONCURRENCY_LEVELS = [1, 10, 20, 50, 100, 1000]

# Fichier de sortie
OUTPUT_FILE = "../out/conc.csv"

# Timeout pour les requêtes (en secondes)
REQUEST_TIMEOUT = 60


async def fetch_timeline(session, user_id, semaphore):
    """Effectue une requête timeline pour un utilisateur donné"""
    url = f"{BASE_URL}?user=user{user_id}"
    
    async with semaphore:
        start_time = time.time()
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as response:
                await response.text()  # Lire la réponse
                elapsed = (time.time() - start_time) * 1000  # Convertir en ms
                
                if response.status == 200:
                    return elapsed, 0  # temps en ms, pas d'échec
                else:
                    return elapsed, 1  # échec
                    
        except asyncio.TimeoutError:
            elapsed = (time.time() - start_time) * 1000
            return elapsed, 1  # échec
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            print(f"    [ERREUR] user{user_id}: {e}")
            return elapsed, 1  # échec


async def run_benchmark(concurrency):
    """Exécute un benchmark avec un niveau de concurrence donné (n = c)"""
    # n_requests = concurrency (nombre de requêtes égal au niveau de concurrence)
    n_requests = concurrency
    
    # Créer un semaphore pour limiter la concurrence
    semaphore = asyncio.Semaphore(concurrency)
    
    # Générer des IDs d'utilisateurs distincts (cycliques si n_requests > 1000)
    user_ids = [(i % 1000) + 1 for i in range(n_requests)]
    
    connector = aiohttp.TCPConnector(limit=concurrency, limit_per_host=concurrency)
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [fetch_timeline(session, user_id, semaphore) for user_id in user_ids]
        results = await asyncio.gather(*tasks)
    
    # Calculer les statistiques
    times = [r[0] for r in results]
    failures = sum(r[1] for r in results)
    
    avg_time = mean(times) if times else -1
    
    return avg_time, failures


def main():
    print("=== Benchmark Concurrence (asyncio + aiohttp) ===")
    print(f"Base de données: 1000 utilisateurs")
    print(f"Configuration: n = c (nombre de requêtes = concurrence)")
    print(f"Requêtes avec utilisateurs distincts\n")

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["PARAM", "AVG_TIME", "RUN", "FAILED"])

        for c in CONCURRENCY_LEVELS:
            print(f"\n>>> Test concurrence c={c} (n={c} requêtes)")

            for run_number in range(1, 4):
                print(f"    Run {run_number}/3 ...")

                start = time.time()
                avg_time, failed = asyncio.run(run_benchmark(c))
                duration = time.time() - start

                print(f"    Résultat : {avg_time:.2f} ms (moyenne), {failed} échecs, durée totale: {duration:.2f}s")

                writer.writerow([c, f"{avg_time:.2f}", run_number, failed])
                f.flush()  # Forcer l'écriture

                await_time = 2 if c < 100 else 5
                print(f"    Pause de {await_time}s...")
                time.sleep(await_time)

    print("\n" + "="*50)
    print(f"✅ Fichier généré : {OUTPUT_FILE}")
    print("Benchmark terminé")


if __name__ == "__main__":
    main()