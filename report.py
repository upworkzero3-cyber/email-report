import argparse
from pathlib import Path

import pandas as pd


DEFAULT_CSV = Path(__file__).resolve().parent.parent / "web-scraper" / "output" / "books.csv"
RATING_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def build_report(csv_path: Path) -> str:
    books = pd.read_csv(csv_path, encoding="utf-8-sig")
    books.columns = books.columns.str.strip().str.lower()
    if not {"price", "rating"}.issubset(books.columns):
        raise ValueError("The CSV must have price and rating columns.")
    if books.empty:
        raise ValueError("The CSV has no book rows.")

    prices = books["price"].astype("string").str.strip()
    currency_symbols = prices.str.extract(r"^([£$€])", expand=False).dropna().unique()
    if len(currency_symbols) > 1:
        raise ValueError("Use a single currency in the price column.")
    currency = currency_symbols[0] if len(currency_symbols) else ""
    prices = pd.to_numeric(prices.str.replace(r"^[£$€]\s*", "", regex=True))

    ratings = books["rating"].astype("string").str.strip().str.lower()
    ratings = pd.to_numeric(ratings.replace({word: str(value) for word, value in RATING_WORDS.items()}))
    if prices.isna().any() or ratings.isna().any():
        raise ValueError("Every book must have a price and a rating.")

    return (
        "Hi,\n\n"
        "Here is the weekly book report.\n\n"
        f"Total books: {len(books):,}\n"
        f"Average price: {currency}{prices.mean():,.2f}\n"
        f"Average rating: {ratings.mean():.2f} out of 5\n"
    )


def main():
    parser = argparse.ArgumentParser(description="Preview the book report email body.")
    parser.add_argument(
        "csv_path", nargs="?", type=Path, default=DEFAULT_CSV,
        help="CSV with price and rating columns (defaults to Project 3's books.csv)",
    )
    args = parser.parse_args()

    try:
        report = build_report(args.csv_path)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Could not summarize {args.csv_path}: {error}\n")

    print(report, end="")


if __name__ == "__main__":
    main()
