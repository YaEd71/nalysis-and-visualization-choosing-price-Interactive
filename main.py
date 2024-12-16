import logging
import data_download as dd
import data_plotting as dplt

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    print("Добро пожаловать в инструмент получения и построения графиков биржевых данных.")
    print(
        "Вот несколько примеров биржевых тикеров: AAPL (Apple Inc), GOOGL (Alphabet Inc), "
        "MSFT (Microsoft Corporation), AMZN (Amazon.com Inc), TSLA (Tesla Inc).")

    try:
        ticker = input("Введите тикер акции (например, «AAPL» для Apple Inc): ")

        # Улучшенный выбор периода
        print("\nВыберите период для анализа:")
        print("1. Предустановленный период")
        print("2. Ручной выбор дат")
        period_choice = input("Введите номер варианта (1/2): ")

        start_date = None
        end_date = None
        period = None

        if period_choice == '1':
            print("\nПредустановленные периоды: 1д, 5д, 1мес, 3мес, 6мес, 1г, 2г, 5г, 10л, с начала года")
            period = input("Введите период (например, '1mo' для одного месяца): ")

        elif period_choice == '2':
            start_date = input("Введите дату начала в формате ГГГГ-ММ-ДД (например, '2023-01-01'): ")
            end_date = input("Введите дату окончания в формате ГГГГ-ММ-ДД (например, '2023-12-31'): ")

        else:
            print("Неверный выбор. Используется период по умолчанию (1 месяц).")
            period = '1mo'

        # Получение данных об акциях
        stock_data = dd.fetch_stock_data(
            ticker,
            period=period,
            start_date=start_date,
            end_date=end_date
        )

        if stock_data is None:
            print("Не удалось получить данные. Завершение программы.")
            return

        # Добавление скользящего среднего
        stock_data = dd.add_moving_average(stock_data)
        # Добавление технических индикаторов
        stock_data = dd.add_technical_indicators(stock_data)
        # Проверка сильных колебаний
        dd.notify_if_strong_fluctuations(stock_data, ticker, threshold=3)
        # Расчет и вывод средней цены
        dd.calculate_average_price(stock_data)
        # Вычисляет стандартное отклонение и проводит углубленный анализ цен акций
        std_deviation = dd.calculate_standard_deviation(stock_data)
        trend_analysis = dd.advanced_price_analysis(stock_data)

        # Выбор типа графика
        print("\nВыберите тип графика:")
        print("1. По умолчанию (цена и скользящее среднее)")
        print("2. RSI")
        print("3. MACD")
        print("4. Все индикаторы")

        plot_choice = input("Введите номер варианта (1-4): ")
        plot_types = {
            '1': 'default',
            '2': 'rsi',
            '3': 'macd',
            '4': 'all'
        }
        plot_type = plot_types.get(plot_choice, 'default')

        # Выбор стиля графика
        print("\nДоступные стили:")
        print("1. default (по умолчанию)")
        print("2. classic")
        print("3. ggplot")
        print("4. bmh")
        print("5. fivethirtyeight")
        print("6. seaborn")
        print("7. tableau-colorblind10")

        style_choice = input("Введите номер стиля (1-7) или оставьте пустым для default: ")
        styles = {
            '1': 'default',
            '2': 'classic',
            '3': 'ggplot',
            '4': 'bmh',
            '5': 'fivethirtyeight',
            '6': 'seaborn',
            '7': 'tableau-colorblind10'
        }
        style = styles.get(style_choice, 'default')

        # Определение названия периода для графика
        if start_date and end_date:
            period = f"{start_date}_to_{end_date}"

        # Построение графика с выбранным типом и стилем
        interactive_plot = dplt.create_and_show_plot(stock_data, ticker, std_deviation)

        # Запрос на экспорт данных
        export_choice = input("Хотите экспортировать данные в CSV? (да/нет): ").lower()
        if export_choice in ['да', 'yes', 'y']:
            filename = f"{ticker}_{period}_stock_data.csv"
            dd.export_data_to_csv(stock_data, filename)

    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()