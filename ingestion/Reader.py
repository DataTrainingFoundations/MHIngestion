import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def read_data(data_path):
    data_path = Path(data_path)
    logger.debug(f"Attempting to read CSV at {data_path}")

    df = pd.read_csv(data_path)

    logger.info(f"Read {len(df)} rows from {data_path}")
    return df
        






