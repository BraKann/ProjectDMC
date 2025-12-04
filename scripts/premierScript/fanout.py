import subprocess
import csv
import re
import time

URL = "https://projetdmc.ew.r.appspot.com/api/timeline?user=user1"

OUTPUT_FILE = "../out/fanout.csv"

FANOUT_LEVELS = [10, 50, 100]
USERS = 101
POSTS = 100

N_REQUESTS = 200
CONCURRENCY = 50

def run_hey(n, c):
    cmd = ["hey", "-t", "0", "-n", str(n), "-c", str(c), URL]

    result = subprocess.run(cmd, capture_output=True, text=True)
    out = result.stdout

    match_time = re.search(r"Average:\s+([\d\.]+)\s*(ms|s|µs)", out)
    if match_time:
        value = float(match_time.group(1))
        unit = match_time.group(2)
        if unit == "ms":
            avg = value
        elif unit == "s":
            avg = value * 1000
        elif unit == "µs":
            avg = value / 1000
    else:
        avg = -1

    match_fail = re.search(r"(\d+)\s+failed", out)
    failed = int(match_fail.group(1)) if match_fail else 0

    return avg, failed


def main():
    print("=== Benchmark Fanout ===")

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["FANOUT", "AVG_TIME", "RUN", "FAILED"])

        for fanout in FANOUT_LEVELS:
            for run in range(1, 3):
                print(f"➡️ Run {run} for fanout={fanout}...")

                avg, failed = run_hey(N_REQUESTS, CONCURRENCY)

                print(f"   Résultat : {avg} ms, failed={failed}")
                writer.writerow([fanout, avg, run, failed])

    print("Fichier généré :", OUTPUT_FILE)
    print("Benchmark terminé")


if __name__ == "__main__":
    main()
