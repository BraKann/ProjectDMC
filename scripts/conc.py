import subprocess
import csv
import re
import time

# URL de ton application
URL = "https://projetdmc.ew.r.appspot.com/api/timeline?user=user1"

# paramètres de concurrence à tester
CONCURRENCY_LEVELS = [1, 10, 20, 50, 100, 1000]

# nombre total de requêtes pour chaque test
# N_REQUESTS = 500

# fichier de sortie
OUTPUT_FILE = "../out/conc.csv"


def run_hey(n, c):
    cmd = ["hey", "-t", "0", "-n", str(n), "-c", str(c), URL]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        out = result.stdout

        # ---- Extraction Latency (format 1) ----
        match_time = re.search(r"Latency\s+([\d\.]+)\s*(ms|µs|s)", out)
        if match_time:
            value = float(match_time.group(1))
            unit = match_time.group(2)
        else:
            # ---- Extraction Average (format 2) ----
            match_avg = re.search(r"Average:\s+([\d\.]+)\s*(s|ms|µs)", out)
            if match_avg:
                value = float(match_avg.group(1))
                unit = match_avg.group(2)
            else:
                return -1, 0

        # Conversion vers millisecondes
        if unit == "ms":
            avg_time = value
        elif unit == "µs":
            avg_time = value / 1000.0
        elif unit == "s":
            avg_time = value * 1000.0

        # ---- Extraction des échecs ----
        match_fail = re.search(r"(\d+)\s+failed", out)
        failed = int(match_fail.group(1)) if match_fail else 0

        return avg_time, failed

    except Exception as e:
        print(f"[ERREUR] hey a planté pour c={c} : {e}")
        return -1, -1



def main():
    print("=== Benchmark Concurrence ===")

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["PARAM", "AVG_TIME", "RUN", "FAILED"])

        for c in CONCURRENCY_LEVELS:
            print(f"\n>>> Test concurrence c={c}")

            n = c

            for run_number in range(1, 4):
                print(f"    Run {run_number}/3 ...")

                avg_time, failed = run_hey(n, c)

                print(f"    Résultat : {avg_time} ms, failed={failed}")

                writer.writerow([c, avg_time, run_number, failed])

                time.sleep(1)

    print("\nFichier généré :", OUTPUT_FILE)
    print("Benchmark terminé")


if __name__ == "__main__":
    main()
