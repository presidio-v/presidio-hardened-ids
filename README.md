# presidio-hardened-ids

ML-based intrusion detection system with adversarial evasion and hardening.
Used in Experiment 4 of PRES-EDU-SEC-101 — Computer Security.

## Setup

```bash
git clone https://github.com/presidio-v/presidio-hardened-ids.git
cd presidio-hardened-ids
pip install -r requirements.txt
```

## Experiments

### Run 1 — Generate synthetic traffic

```bash
python generate_traffic.py --normal 10000 --attacks 500 \
    --attack-types portscan synflood exfiltration \
    --seed 42 --output data/traffic.csv
python eda.py --input data/traffic.csv
```

### Run 2 — Train Isolation Forest detector

```bash
python train.py --input data/traffic.csv \
    --contamination 0.05 \
    --model-out models/ids_model.pkl
```

### Run 3 — Real-time Streamlit dashboard

```bash
# Terminal 1: stream new traffic every 2 seconds
python stream.py --rate 50 --attack-prob 0.03 &

# Terminal 2: launch dashboard
streamlit run dashboard.py --server.port 8501
```

Open http://localhost:8501 — observe anomaly scores in real time.

### Run 4 — Adversarial evasion attack

```bash
python attack.py --mode evasion \
    --model models/ids_model.pkl \
    --attack-type portscan \
    --n-attempts 200 \
    --output reports/evasion_report.json
python report.py --experiment 4
```

### Run 5 — Retrain with adversarial examples (hardening)

```bash
python train.py --input data/traffic.csv \
    --adversarial reports/evasion_report.json \
    --contamination 0.05 \
    --model-out models/ids_model_hardened.pkl

python attack.py --mode evasion \
    --model models/ids_model_hardened.pkl \
    --n-attempts 200 \
    --output reports/evasion_hardened.json

python report.py --compare ids_model ids_model_hardened
```

## What to Observe

- Evasion attack on base model: some flows score below threshold
- Evasion attack on hardened model: evasion rate drops significantly
- Dashboard: anomaly scores in real time; flagged flows shown in red
- Takeaway: adversarial testing is not optional — detectors must be evaluated against adversarial inputs

## Package Structure

```
src/presidio_ids/
├── traffic.py      Synthetic traffic generator
├── features.py     Feature engineering / CSV loader
├── detector.py     Isolation Forest wrapper
├── adversarial.py  Evasion attack + retraining
└── security.py     Logging + pip-audit
```

## License

MIT

---

## SDLC

This repository is developed under the Presidio hardened-family SDLC:
<https://github.com/presidio-v/presidio-hardened-docs/blob/main/sdlc/sdlc-report.md>.
