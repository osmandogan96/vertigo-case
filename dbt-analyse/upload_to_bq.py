import glob
import pandas as pd
from google.cloud import bigquery
from configs.config import MAIN_PATH, GCP_PROJECT_ID


def upload(project_id, dataset_id, table_id):
    """
    Upload all csv.gz files from a folder into a single BigQuery table.
    """
    # Find all csv.gz files
    files = sorted(glob.glob(f"{MAIN_PATH}/data/*csv.gz"))
    if not files:
        raise FileNotFoundError(f"No .csv.gz files found in data")

    print(f"Found {len(files)} file(s): {[f.split('/')[-1] for f in files]}")

    # Read and concat all files
    dfs = [pd.read_csv(f, compression="gzip") for f in files]
    df = pd.concat(dfs, ignore_index=True)
    print(f"Total rows: {len(df):,}")

    # Type cleanup
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date
    df["install_date"] = pd.to_datetime(df["install_date"]).dt.date

    # Upload
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset.location = "EU"
    client.create_dataset(dataset, exists_ok=True)

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True,
    )

    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()

    result = client.get_table(table_ref)
    print(f"Uploaded {result.num_rows:,} rows to {table_ref}")


if __name__ == "__main__":
    dataset = "raw_data"
    table = "user_daily_metrics"
    upload(GCP_PROJECT_ID, dataset, table)
