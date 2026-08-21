#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model Retraining & Calibration Cadence Job.

Evaluates candidate LogisticRegression classifier against active production model
on held-out test split of full prediction_ledger × outcome_ledger data.
Promotes candidate and registers new version in model_versions table if candidate outperforms active model.
"""

import os
import sys
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ml.baseline_model import evaluate_and_retrain_model

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("retrain_model")


def main():
    logger.info("Starting model retrain & evaluation cadence job...")
    result = evaluate_and_retrain_model()
    logger.info("Retrain Result Status: %s", result.get("status"))
    logger.info("Message: %s", result.get("message"))
    logger.info("Sample Count: %s", result.get("sample_count"))
    logger.info("Active Model Test Accuracy: %s", result.get("active_accuracy"))
    logger.info("Candidate Model Test Accuracy: %s", result.get("candidate_accuracy"))
    logger.info("Promoted: %s", result.get("promoted"))
    logger.info("Active/Promoted Version: %s", result.get("version"))

    if result.get("promoted"):
        print(f"SUCCESS: Model promoted to {result.get('version')}")
    else:
        print(f"SUCCESS: Current model version {result.get('version')} retained.")


if __name__ == "__main__":
    main()
