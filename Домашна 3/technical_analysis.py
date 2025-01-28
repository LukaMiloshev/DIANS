import pandas as pd
import matplotlib.pyplot as plt
import os

def perform_technical_analysis(data_path):
    print("Executing technical analysis...")

    if not os.path.exists(data_path):
        print(f"Error: File not found at {data_path}")
        return

    data = pd.read_csv(data_path, parse_dates=["Датум"], dayfirst=True)
    data = data.sort_values(by="Датум")

    data["SMA_20"] = data["Цена"].rolling(window=20).mean()
    data["SMA_50"] = data["Цена"].rolling(window=50).mean()

    output_data_path = os.path.join(os.path.dirname(data_path), "technical_analysis_results.csv")
    data.to_csv(output_data_path, index=False)
    print(f"Processed data with indicators saved to: {output_data_path}")

    plt.figure(figsize=(10, 6))
    plt.plot(data["Датум"], data["Цена"], label="Цена")
    plt.plot(data["Датум"], data["SMA_20"], label="20-day SMA")
    plt.plot(data["Датум"], data["SMA_50"], label="50-day SMA")
    plt.legend()
    plt.title("Technical Analysis")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid()

    output_image_path = os.path.join(os.path.dirname(data_path), "technical_analysis_chart.png")
    plt.savefig(output_image_path)
    print(f"Technical analysis chart saved to: {output_image_path}")

    plt.show()

    print("Technical analysis completed.")
