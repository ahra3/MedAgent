from pathlib import Path
import polars as pl

# Path to the raw DDInter CSV files
RAW_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "drug_interactions" / "raw"
PROCESSED_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "drug_interactions" / "ddinter_combined.parquet"


def load_raw_csvs() -> pl.DataFrame:
    """Load all 8 DDInter CSV files and combine into one DataFrame.
    Returns:
        A single Polars DataFrame with all interactions, plus a 'source_file' column.
    """
    csv_files = sorted(RAW_DATA_DIR.glob("ddinter_downloads_code_*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"No DDInter CSV files found in {RAW_DATA_DIR}. "
            f"Download them from https://ddinter2.scbdd.com/download/"
        )
    frames = []
    for csv_file in csv_files:
        df = pl.read_csv(csv_file, infer_schema_length=1000)
        # Add which file this came from (for debugging)
        df = df.with_columns(pl.lit(csv_file.stem).alias("source_file"))
        frames.append(df)
    combined = pl.concat(frames, how="diagonal_relaxed")
    print(f"Loaded {len(csv_files)} files → {combined.shape[0]:,} total interactions")
    return combined

def process_and_save(df: pl.DataFrame) -> pl.DataFrame:
    """Clean, normalize, and save the DDInter data.
    Processing steps:
    1. Normalize drug names to lowercase (for case-insensitive lookups)
    2. Normalize the severity level column
    3. Drop rows with missing drug names
    4. Save as Parquet for fast future loading
    Args:
        df: Raw combined DDInter DataFrame.
    Returns:
        Processed DataFrame.
    """
    processed = (
        df
        # Rename columns to our standard names (DDInter uses various header styles)
        .rename(lambda col: col.strip().lower().replace(" ", "_"))
        .with_columns([
            # Normalize drug names to lowercase for consistent lookups
            pl.col("drug_a").str.to_lowercase().str.strip_chars().alias("drug_1_normalized"),
            pl.col("drug_b").str.to_lowercase().str.strip_chars().alias("drug_2_normalized"),
            # Normalize severity level
            pl.col("level")
            .str.to_lowercase()
            .str.strip_chars()
            .alias("severity"),
        ])
        # Drop rows where either drug name is missing
        .filter(
            pl.col("drug_1_normalized").is_not_null()
            & pl.col("drug_2_normalized").is_not_null()
        )
        # Remove exact duplicates (same drug pair can appear in multiple category files)
        .unique(subset=["drug_1_normalized", "drug_2_normalized"], keep="first")
    )
    # Save as Parquet for fast loading in production
    processed.write_parquet(PROCESSED_DATA_PATH)
    print(f"Processed: {processed.shape[0]:,} unique interactions → saved to {PROCESSED_DATA_PATH}")
    return processed

def load_processed() -> pl.DataFrame:
    """Load the pre-processed DDInter data from Parquet.
    If the Parquet file doesn't exist yet, processes from raw CSVs first.
    Returns:
        Processed Polars DataFrame.
    """
    if PROCESSED_DATA_PATH.exists():
        return pl.read_parquet(PROCESSED_DATA_PATH)
    # First-time setup: process from raw CSVs
    raw = load_raw_csvs()
    return process_and_save(raw)

def lookup_interaction(
    df: pl.DataFrame,
    drug_a: str,
    drug_b: str,
) -> list[dict]:
    """Look up interactions between two drugs.
    Checks both orderings (A-B and B-A) since DDInter stores
    each pair only once.
    Args:
        df: The processed DDInter DataFrame.
        drug_a: First drug name (case-insensitive).
        drug_b: Second drug name (case-insensitive).
    Returns:
        List of matching interaction dicts. Empty list if no interaction found.
    """
    a = drug_a.lower().strip()
    b = drug_b.lower().strip()
    matches = df.filter(
        (
            (pl.col("drug_1_normalized") == a)
            & (pl.col("drug_2_normalized") == b)
        )
        | (
            (pl.col("drug_1_normalized") == b)
            & (pl.col("drug_2_normalized") == a)
        )
    )
    return matches.to_dicts()

def lookup_all_pairs(
    df: pl.DataFrame,
    drug_names: list[str],
) -> list[dict]:
    """Check all pairwise combinations of a medication list for interactions.
    This is the main function the DDI Agent will call.
    Args:
        df: The processed DDInter DataFrame.
        drug_names: List of drug names to check (e.g., ["Metformin", "Warfarin", "Aspirin"]).
    Returns:
        List of all interaction dicts found across all pairs.
    """
    from itertools import combinations
    # Normalize all drug names
    normalized = [name.lower().strip() for name in drug_names]
    all_interactions = []
    for drug_a, drug_b in combinations(normalized, 2):
        matches = lookup_interaction(df, drug_a, drug_b)
        all_interactions.extend(matches)
    return all_interactions

def get_quick_stats(df: pl.DataFrame) -> dict:
    """Get summary statistics about the loaded DDInter data.
    Useful for verification and the README.
    Returns:
        Dict with counts by severity level and total unique drugs.
    """
    severity_counts = (
        df
        .group_by("severity")
        .len()
        .sort("len", descending=True)
        .to_dicts()
    )
    unique_drugs = pl.concat([
        df.select(pl.col("drug_1_normalized").alias("drug")),
        df.select(pl.col("drug_2_normalized").alias("drug")),
    ]).unique().shape[0]
    return {
        "total_interactions": df.shape[0],
        "unique_drugs": unique_drugs,
        "by_severity": severity_counts,
    }
    
    
if __name__ == "__main__":
    print("=== DDInter 2.0 Data Processor ===\n")
    print("Step 1: Loading raw CSV files...")
    raw = load_raw_csvs()
    print("\nStep 2: Processing and saving...")
    processed = process_and_save(raw)
    print("\nStep 3: Quick stats:")
    stats = get_quick_stats(processed)
    print(f"  Total interactions: {stats['total_interactions']:,}")
    print(f"  Unique drugs: {stats['unique_drugs']:,}")
    print(f"  By severity:")
    for entry in stats["by_severity"]:
        print(f"    {entry['severity']}: {entry['len']:,}")
    print("\nStep 4: Test lookup (Metformin + Warfarin)...")
    results = lookup_interaction(processed, "Metformin", "Warfarin")
    if results:
        for r in results:
            print(f"  Found: {r.get('drug_1_normalized')} ↔ {r.get('drug_2_normalized')} | Severity: {r.get('severity')} | {r.get('mechanism', 'N/A')}")
    else:
        print("  No interaction found (this pair may not be in DDInter)")
    print("\n Done! Data ready at:", PROCESSED_DATA_PATH)