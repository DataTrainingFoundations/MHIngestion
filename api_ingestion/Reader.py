import requests
import json
import pandas as pd
import os
import logging
from pathlib import Path #temp
from dotenv import load_dotenv

# loads API key from .env
load_dotenv()  
BLS_API_KEY = os.getenv("BLS_API_KEY")
# URL of api
BLS_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

#sets up the logger
logger = logging.getLogger(__name__)

def fetch_bls_timeseries(series_ids: list[str], start_year: int, end_year: int,
                         api_key: str | None = None):
    #sets up the payload to send to BLS
    payload: dict[str, object] = {
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year),
    }

    #if their is an api_key adds it to the payload
    if api_key:
        payload["registrationKey"] = api_key

    try:
        logger.info(
            "Requesting BLS data | series=%d | years=%s-%s",
            len(series_ids),
            start_year,
            end_year
        )
        #the request for th json
        resp = requests.post(BLS_URL, json=payload, timeout=30)
        resp.raise_for_status()
        #sets data = to the response
        data = resp.json()

        # checks if request succeeded
        status = data.get("status")
        if status != "REQUEST_SUCCEEDED":
            message = data.get("message", [])
            logger.error("BLS API returned failure status | message=%s", message)
            raise RuntimeError(f"BLS API request failed: {message}")

        # TEMP: save raw JSON for debugging
        # PROJECT_ROOT = Path(__file__).resolve().parent.parent
        # data_path = PROJECT_ROOT / "data"

        # debug_file = data_path / "unemployment_data.json"

        # with open(debug_file, "w", encoding="utf-8") as f:
        #     json.dump(data, f, indent=2)
        
        #turns json into a df
        rows: list[dict[str, object]] = []
        for series in data.get("Results", {}).get("series", []):
            sid = series.get("seriesID")
            for obs in series.get("data", []):
                rows.append({
                    "series_id": sid,
                    "year": obs.get("year"),
                    "period": obs.get("period"),
                    "period_name": obs.get("periodName"),
                    "value": obs.get("value"),
                })

        df = pd.DataFrame(rows)

        #records meta data for the logs
        meta = {
            "source": "bls_laus_api",
            "series_requested": len(series_ids),
            "rows_returned": len(df),
            "start_year": start_year,
            "end_year": end_year,
        }

        logger.info(f"BLS fetch successful | rows={len(df)}")
        logger.info(meta)

        return df

    except requests.exceptions.RequestException as e:
        logger.exception("Network/API error occurred while calling BLS API")
        raise

    except Exception as e:
        logger.exception("Unexpected error occurred during BLS ingestion")
        raise


def read_json(data_path):
    
    # TEMP helper to load a saved BLS JSON file
    # and flatten it into a DataFrame.
    
    data_path = Path(data_path)

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []

    for series in data.get("Results", {}).get("series", []):
        sid = series.get("seriesID")

        for obs in series.get("data", []):
            rows.append({
                "series_id": sid,
                "year": obs.get("year"),
                "period": obs.get("period"),
                "period_name": obs.get("periodName"),
                "value": obs.get("value"),
            })

    df = pd.DataFrame(rows)
    return df




if __name__ == "__main__":

    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    data_path = PROJECT_ROOT / "data" / "unemployment_data.json"
    df = read_json(data_path)
    print(df.head)
    print(df.columns)

    # STATE_FIPS = [
    # "01","02","04","05","06","08","09","10","12","13",
    # "15","16","17","18","19","20","21","22","23","24",
    # "25","26","27","28","29","30","31","32","33","34",
    # "35","36","37","38","39","40","41","42","44","45",
    # "46","47","48","49","50","51","53","54","55","56"
    # ]  
    # series_ids = [f"LAUST{fips}0000000000003" for fips in STATE_FIPS]

    # if not BLS_API_KEY:
    #     raise ValueError("BLS_API_KEY not found in environment variables")

    # try:
    #     df_raw, meta = fetch_bls_timeseries(
    #         series_ids=series_ids,
    #         start_year=2020,
    #         end_year=2022,
    #         api_key=BLS_API_KEY
    #     )

    #     print("=== META ===")
    #     print(meta)

    #     print("\n=== SAMPLE DATA ===")
    #     print(df_raw.head())

    #     print("\nRows returned:", len(df_raw))

    # except Exception as e:
    #     logger.exception("Failed during standalone BLS fetch test")