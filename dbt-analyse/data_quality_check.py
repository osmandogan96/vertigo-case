import glob
import pandas as pd
from configs.config import MAIN_PATH

def main():
    """
    Quick data quality report. Reads all csv.gz files, prints findings.
    """

    files = sorted(glob.glob(f"{MAIN_PATH}/data/*csv.gz"))
    print(f"Files: {len(files)}")

    df = pd.concat([pd.read_csv(f, compression="gzip") for f in files], ignore_index=True)
    print(f"Rows: {len(df):,} | Columns: {len(df.columns)}")
    print(f"Date range: {df['event_date'].min()} → {df['event_date'].max()}")
    print(f"Unique users: {df['user_id'].nunique():,}")
    print(f"Platforms: {df['platform'].unique().tolist()}")
    print()

    # Nulls
    print("--- Null Counts ---")
    nulls = df.isnull().sum()
    empty_country = (df["country"].fillna("").str.strip() == "").sum()
    print(nulls[nulls > 0].to_string() if nulls.sum() > 0 else "  No nulls")
    print(f"  Empty/blank country: {empty_country:,}")
    print()

    # Duplicates
    dupes = df.duplicated(subset=["user_id", "event_date"]).sum()
    print(f"--- Duplicates (user_id + event_date): {dupes:,} ---")
    print()
    dupes_all = df.duplicated().sum()
    print(f"--- Duplicates: {dupes_all:,} ---")
    print()

    # Logical checks
    print("--- Anomaly Checks ---")
    checks = {
        "victory > match_end": (df["victory_count"] > df["match_end_count"]).sum(),
        "defeat > match_end": (df["defeat_count"] > df["match_end_count"]).sum(),
        "match_end > match_start": (df["match_end_count"] > df["match_start_count"]).sum(),
        "negative values": sum((df[c] < 0).sum() for c in df.select_dtypes("number").columns),
    }
    for label, count in checks.items():
        flag = " ⚠" if count > 0 else ""
        print(f"  {label}: {count:,}{flag}")
    print()

    # Platform split
    print("--- Platform Split ---")
    for p, c in df["platform"].value_counts().items():
        print(f"  {p}: {c:,} ({c/len(df)*100:.1f}%)")
    print()

    # Revenue summary
    print("--- Revenue ---")
    print(f"  IAP total: ${df['iap_revenue'].sum():,.2f} | rows > 0: {(df['iap_revenue']>0).sum():,}")
    print(f"  Ad total:  ${df['ad_revenue'].sum():,.2f}  | rows > 0: {(df['ad_revenue']>0).sum():,}")


if __name__ == "__main__":
    main()
