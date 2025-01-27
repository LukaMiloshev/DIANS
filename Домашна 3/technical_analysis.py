import pandas as pd
import matplotlib.pyplot as plt

def perform_technical_analysis(data_path):
    print("Извршување техничка анализа...")

    # Читање на податоци
    data = pd.read_csv(data_path, parse_dates=["Датум"], dayfirst=True)
    data = data.sort_values(by="Датум")

    # Пресметување на индикатори (пр. Moving Averages)
    data["SMA_20"] = data["Цена"].rolling(window=20).mean()
    data["SMA_50"] = data["Цена"].rolling(window=50).mean()

    # Визуелизација
    plt.figure(figsize=(10, 6))
    plt.plot(data["Датум"], data["Цена"], label="Цена")
    plt.plot(data["Датум"], data["SMA_20"], label="20-дневен SMA")
    plt.plot(data["Датум"], data["SMA_50"], label="50-дневен SMA")
    plt.legend()
    plt.title("Техничка анализа")
    plt.xlabel("Датум")
    plt.ylabel("Цена")
    plt.grid()
    plt.show()

    print("Техничката анализа е завршена.")
