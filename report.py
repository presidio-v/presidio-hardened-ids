"""Report generator for Experiment 4 — ML IDS."""

from __future__ import annotations

import argparse
import json
import pathlib


def _load_json(path: str) -> dict:
    p = pathlib.Path(path)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def report_experiment(exp_num: int) -> None:
    print("\n========================================")
    print(f"  Experiment {exp_num} — ML IDS Report")
    print("========================================\n")

    report = _load_json("reports/evasion_report.json")
    if not report:
        print("  No evasion report found. Run attack.py first.")
        return

    print(f"  Model:          {report.get('model_path', 'N/A')}")
    print(f"  Attack type:    {report.get('attack_type', 'N/A')}")
    print(f"  Attempts:       {report.get('n_attempts', 0)}")
    print(f"  Evaded:         {report.get('n_evaded', 0)}")
    evasion_rate = report.get("evasion_rate", 0)
    print(f"  Evasion rate:   {evasion_rate:.1%}")

    if evasion_rate > 0:
        print(
            "\n  Key observation: Attack flows evaded detection by staying within "
            "the learned normal distribution. This is adversarial evasion (Slide 18)."
        )
    else:
        print("\n  Key observation: No evasion — detector is robust for this attack type.")
    print()


def report_compare(name_a: str, name_b: str) -> None:
    path_a = "reports/evasion_report.json"
    path_b = "reports/evasion_hardened.json"
    print("\n========================================")
    print(f"  Comparison: {name_a}  vs  {name_b}")
    print("========================================\n")

    ra = _load_json(path_a)
    rb = _load_json(path_b)

    if not ra:
        print(f"  Missing {path_a}")
        return
    if not rb:
        print(f"  Missing {path_b}")
        return

    rate_a = ra.get("evasion_rate", 0)
    rate_b = rb.get("evasion_rate", 0)
    delta = rate_b - rate_a

    print(f"  {'Metric':<25} {name_a:>12} {name_b:>14}")
    print(f"  {'-' * 53}")
    print(f"  {'Evasion rate':<25} {rate_a:>12.1%} {rate_b:>14.1%}")
    print(f"  {'Delta':<25} {delta:>+12.1%}")
    print()

    if rate_b < rate_a:
        reduction = (rate_a - rate_b) / rate_a if rate_a > 0 else 0
        print(f"  Result: HARDENED — evasion rate reduced by {reduction:.0%}")
    else:
        print("  Result: No improvement — consider more adversarial examples or retraining.")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 4 report")
    parser.add_argument("--experiment", type=int, default=None)
    parser.add_argument("--compare", nargs=2, metavar=("BASE", "HARDENED"))
    args = parser.parse_args()

    if args.experiment:
        report_experiment(args.experiment)
    elif args.compare:
        report_compare(args.compare[0], args.compare[1])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
