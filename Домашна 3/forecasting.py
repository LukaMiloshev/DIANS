import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

def forecast_prices(data_path):
    print("Извршување прогнозирање на цени...")

    # Читање на податоци
    data = pd.read_csv(data_path, parse_dates=["Датум"], dayfirst=True)
    data["Ден"] = (data["Датум"] - data["Датум"].min()).dt.days

    # Линеарна регресија (пример)
    X = data[["Ден"]]
    y = data["Цена"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    # Прогноза
    data["Прогнозирана Цена"] = model.predict(X)

    # Визуелизација
    plt.figure(figsize=(10, 6))
    plt.plot(data["Датум"], data["Цена"], label="Цена")
    plt.plot(data["Датум"], data["Прогнозирана Цена"], label="Прогнозирана Цена", linestyle="--")
    plt.legend()
    plt.title("Прогноза на цените")
    plt.xlabel("Датум")
    plt.ylabel("Цена")
    plt.grid()
    plt.show()

    print("Прогнозирањето е завршено.")
