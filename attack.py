"""Adversarial evasion attack runner."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Adversarial evasion attack")
    parser.add_argument("--mode", choices=["evasion"], required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--attack-type", default="portscan")
    parser.add_argument("--n-attempts", type=int, default=200)
    parser.add_argument("--output", default="reports/evasion_report.json")
    args = parser.parse_args()

    from presidio_ids import run_evasion

    print(f"Running evasion attack ({args.attack_type}, {args.n_attempts} attempts)...")
    report = run_evasion(
        model_path=args.model,
        attack_type=args.attack_type,
        n_attempts=args.n_attempts,
        output=args.output,
    )
    print(f"\n  Model:          {report.model_path}")
    print(f"  Attack type:    {report.attack_type}")
    print(f"  Attempts:       {report.n_attempts}")
    print(f"  Evaded:         {report.n_evaded}")
    print(f"  Evasion rate:   {report.evasion_rate:.1%}")
    print(f"\n  Report saved to: {args.output}")

    if report.evasion_rate > 0:
        print("\n  [!] Some attack flows evaded detection. Retrain with --adversarial to harden.")
    else:
        print("\n  [OK] No evasion. Detector is robust against this attack type.")


if __name__ == "__main__":
    main()
