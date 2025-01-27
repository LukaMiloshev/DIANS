from technical_analysis import perform_technical_analysis
from fundamental_analysis import perform_fundamental_analysis
from forecasting import forecast_prices

def main():
    print("Добредојдовте во Финансискиот Анализатор!")
    print("1. Техничка анализа")
    print("2. Фундаментална анализа")
    print("3. Прогноза на цените")
    choice = input("Изберете опција: ")

    if choice == "1":
        data_path = input("Внесете ја патеката до CSV датотеката со податоци: ")
        perform_technical_analysis(data_path)
    elif choice == "2":
        perform_fundamental_analysis()
    elif choice == "3":
        data_path = input("Внесете ја патеката до CSV датотеката со податоци: ")
        forecast_prices(data_path)
    else:
        print("Невалиден избор.")

if __name__ == "__main__":
    main()
