import os
import sys
from technical_analysis import perform_technical_analysis
from fundamental_analysis import perform_fundamental_analysis
from forecasting import forecast_prices
from dom1 import run_scraper
import argparse

DATA_DIR = 'records_storage'
os.makedirs(DATA_DIR, exist_ok=True)

def run_tests():
    print("Running tests...")

    print("\n[TEST] Running Data Scraper Test...")
    test_url = 'https://www.mse.mk/mk/stats/symbolhistory/ALK'
    try:
        run_scraper(test_url)
        print("[PASS] Data Scraper Test Passed!")
    except Exception as e:
        print(f"[FAIL] Data Scraper Test Failed: {e}")

    print("\n[TEST] Running Technical Analysis Test...")
    try:
        perform_technical_analysis(DATA_DIR)
        print("[PASS] Technical Analysis Test Passed!")
    except Exception as e:
        print(f"[FAIL] Technical Analysis Test Failed: {e}")

    print("\n[TEST] Running Fundamental Analysis Test...")
    try:
        perform_fundamental_analysis(DATA_DIR)
        print("[PASS] Fundamental Analysis Test Passed!")
    except Exception as e:
        print(f"[FAIL] Fundamental Analysis Test Failed: {e}")

    print("\n[TEST] Running Forecasting Test...")
    try:
        forecast_prices(DATA_DIR)
        print("[PASS] Forecasting Test Passed!")
    except Exception as e:
        print(f"[FAIL] Forecasting Test Failed: {e}")

    print("\nAll tests completed.")

def main():
    parser = argparse.ArgumentParser(description="Stock Analysis Application")
    parser.add_argument('--scrape', action='store_true', help='Run the data scraper to fetch stock data.')
    parser.add_argument('--technical', action='store_true', help='Run technical analysis on stock data.')
    parser.add_argument('--fundamental', action='store_true', help='Run fundamental analysis on stock data.')
    parser.add_argument('--forecast', action='store_true', help='Run LSTM forecasting on stock data.')
    parser.add_argument('--test', action='store_true', help='Run all tests.')
    args = parser.parse_args()

    if args.test:
        run_tests()
        return

    if args.scrape:
        print("\n[INFO] Running Data Scraper...")
        url = 'https://www.mse.mk/mk/stats/symbolhistory/ALK'
        run_scraper(url)

    if args.technical:
        print("\n[INFO] Running Technical Analysis...")
        perform_technical_analysis(DATA_DIR)

    if args.fundamental:
        print("\n[INFO] Running Fundamental Analysis...")
        perform_fundamental_analysis(DATA_DIR)

    if args.forecast:
        print("\n[INFO] Running Forecasting...")
        forecast_prices(DATA_DIR)

if __name__ == "__main__":
    main()
