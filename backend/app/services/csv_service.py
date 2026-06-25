# app/services/csv_service.py

import pandas as pd


def get_product_ids(file):
    df = pd.read_csv(file)

    return (
        df["product_id"]
        .dropna()
        .astype(str)
        .tolist()
    )