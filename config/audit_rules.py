# config/audit_rules.py
import os

# Default public baseline weights (Override via .env for internal enterprise usage)
S1_WEIGHT = float(os.getenv("S1_WEIGHT", "0.20"))
P5_WEIGHT = float(os.getenv("P5_WEIGHT", "0.15"))