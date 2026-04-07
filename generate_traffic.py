"""Generate synthetic network traffic for Experiment 4."""

from __future__ import annotations

import argparse
import pathlib


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic traffic generator")
    parser.add_argument("--normal", type=int, default=10000)
    parser.add_argument("--attacks", type=int, default=500)
    parser.add_argument(
        "--attack-types",
        nargs="+",
        default=["portscan", "synflood", "exfiltration"],
        choices=["portscan", "synflood", "exfiltration"],
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="data/traffic.csv")
    args = parser.parse_args()

    from presidio_ids import generate, summary

    print(f"Generating {args.normal} normal + {args.attacks} attack flows (seed={args.seed})...")
    df = generate(
        n_normal=args.normal,
        n_attacks=args.attacks,
        attack_types=args.attack_types,
        seed=args.seed,
    )
    pathlib.Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)

    stats = summary(df)
    print(f"  Total flows:   {stats['total_flows']}")
    print(f"  Normal:        {stats['normal_flows']}")
    print(f"  Attack:        {stats['attack_flows']}  ({stats['attack_ratio']:.1%})")
    print(f"  Features:      {stats['n_features']}")
    print(f"  Saved to:      {args.output}")


if __name__ == "__main__":
    main()
