"""Helper utilities for exporting dashboard data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def export_dataframe(df: pd.DataFrame, filename: str, output_dir: str = "exports") -> str:
    """Export a dataframe as CSV and return the output path."""
    folder = Path(output_dir)
    folder.mkdir(exist_ok=True)
    target = folder / filename
    df.to_csv(target, index=False)
    return str(target)


def export_audit_df(df: pd.DataFrame) -> str:
    """Convenience wrapper for the audit tab export."""
    return export_dataframe(df, "audit_export.csv")
