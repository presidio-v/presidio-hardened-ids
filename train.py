"""Train (or retrain with adversarial examples) the Isolation Forest detector."""

from __future__ import annotations

import argparse
import pathlib


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Isolation Forest IDS")
    parser.add_argument("--input", required=True)
    parser.add_argument("--contamination", type=float, default=0.05)
    parser.add_argument("--model-out", required=True)
    parser.add_argument("--adversarial", default=None, help="Path to evasion report JSON")
    args = parser.parse_args()

    import pandas as pd

    from presidio_ids import IsolationForestDetector, get_X, get_y, load, load_adversarial_flows

    df = load(args.input)

    if args.adversarial:
        adv_df = load_adversarial_flows(args.adversarial)
        if len(adv_df) > 0:
            df = pd.concat([df, adv_df], ignore_index=True)
            print(f"  Added {len(adv_df)} adversarial flows for hardening.")

    split = int(len(df) * 0.8)
    df_train = df.iloc[:split]
    df_test = df.iloc[split:]

    X_train = get_X(df_train)
    X_test = get_X(df_test)
    y_test = get_y(df_test)

    print(f"Training on {len(X_train)} flows (contamination={args.contamination})...")
    detector = IsolationForestDetector(contamination=args.contamination)
    detector.fit(X_train)

    metrics = detector.evaluate(X_test, y_test)
    print(f"\n  Test metrics (n={len(X_test)}):")
    print(f"  Precision:    {metrics.precision:.4f}")
    print(f"  Recall:       {metrics.recall:.4f}")
    print(f"  F1:           {metrics.f1:.4f}")
    print(f"  Threshold:    {metrics.threshold}")

    pathlib.Path(args.model_out).parent.mkdir(parents=True, exist_ok=True)
    detector.save(args.model_out)
    print(f"\n  Model saved to: {args.model_out}")


if __name__ == "__main__":
    main()
