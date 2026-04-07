"""Exploratory data analysis for the traffic CSV."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="EDA for traffic CSV")
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    import pandas as pd

    from presidio_ids import summary

    df = pd.read_csv(args.input)
    stats = summary(df)

    print("\n=== EDA: Network Traffic Dataset ===\n")
    print(f"  Rows:        {stats['total_flows']}")
    print(f"  Normal:      {stats['normal_flows']}")
    print(f"  Attack:      {stats['attack_flows']}  ({stats['attack_ratio']:.1%})")
    print(f"  Features:    {', '.join(stats['features'])}\n")

    print("  Numeric summary (all features):")
    desc = df[stats["features"]].describe().T
    print(desc[["mean", "std", "min", "max"]].to_string())

    from presidio_ids.traffic import LABEL_COL

    if LABEL_COL in df.columns:
        print("\n  Label distribution:")
        print(df[LABEL_COL].value_counts().to_string())
    print()


if __name__ == "__main__":
    main()
