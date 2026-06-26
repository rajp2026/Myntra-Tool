"""
CSV parsing helper.

Reads the uploaded file and returns a clean list of product-ID strings.
"""

import pandas as pd


def get_product_ids(file) -> list[str]:
    """
    Parse a CSV file-like object and return the ``product_id``
    column as a list of stripped strings.

    Raises ``ValueError`` if the required column is missing.
    """
    df = pd.read_csv(file)

    if "product_id" not in df.columns:
        raise ValueError(
            "CSV must have a 'product_id' column. "
            f"Found columns: {', '.join(df.columns)}"
        )

    return (
        df["product_id"]
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )