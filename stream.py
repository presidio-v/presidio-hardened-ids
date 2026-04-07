"""Real-time traffic stream: appends flows to data/stream_live.csv every 1/rate seconds.

Runs as a background process. The Streamlit dashboard polls stream_live.csv.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import time


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic traffic stream")
    parser.add_argument("--rate", type=int, default=50, help="Flows per second")
    parser.add_argument("--attack-prob", type=float, default=0.03)
    parser.add_argument("--output", default="data/stream_live.csv")
    parser.add_argument("--duration", type=int, default=None, help="Stop after N seconds")
    args = parser.parse_args()

    from presidio_ids.traffic import FEATURE_COLS, LABEL_COL, stream_flow

    out = pathlib.Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    interval = 1.0 / max(1, args.rate)
    all_cols = FEATURE_COLS + [LABEL_COL]

    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_cols)
        writer.writeheader()
        f.flush()

    t_start = time.time()
    n = 0
    try:
        while True:
            flow = stream_flow(attack_prob=args.attack_prob)
            with open(out, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=all_cols)
                writer.writerow({k: flow.get(k, 0) for k in all_cols})
            n += 1
            if args.duration and (time.time() - t_start) >= args.duration:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        pass

    print(f"Streamed {n} flows to {out}")


if __name__ == "__main__":
    main()
