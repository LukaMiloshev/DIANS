import pandas as pd

def perform_fundamental_analysis():
    print("Извршување фундаментална анализа...")

    data = {
        "Компанија": ["ALK", "KMB", "SILK"],
        "P/E": [15.2, 18.5, 12.8],
        "P/B": [1.8, 2.1, 1.4],
        "ROE (%)": [12.5, 14.3, 10.7],
    }

    df = pd.DataFrame(data)

    print(df)
    print("\nСовети:")
    for index, row in df.iterrows():
        if row["P/E"] < 15 and row["ROE (%)"] > 12:
            print(f"- Компанијата {row['Компанија']} е добра за разгледување.")
        else:
            print(f"- Компанијата {row['Компанија']} може да се провери дополнително.")

    print("Фундаменталната анализа е завршена.")
