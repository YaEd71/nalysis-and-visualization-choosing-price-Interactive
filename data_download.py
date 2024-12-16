import yfinance as yf
import numpy as np
import pandas as pd
import os


def fetch_stock_data(ticker, period='1mo', start_date=None, end_date=None):
    """
    Получает данные об акциях для указанного тикера из Yahoo Finance

    :param ticker: Тикер акции
    :param period: Стандартный период загрузки (по умолчанию 1 месяц)
    :param start_date: Дата начала в формате 'ГГГГ-ММ-ДД'
    :param end_date: Дата окончания в формате 'ГГГГ-ММ-ДД'
    :return: DataFrame с данными об акциях или None
    """
    try:
        stock = yf.Ticker(ticker)

        # Приоритет у конкретных дат, если они указаны
        if start_date and end_date:
            try:
                # Преобразование строк в объекты datetime
                start = pd.to_datetime(start_date)
                end = pd.to_datetime(end_date)

                # Проверка корректности дат
                if start >= end:
                    print("Ошибка: Дата начала должна быть раньше даты окончания.")
                    return None

                data = stock.history(start=start, end=end)
            except ValueError as date_error:
                print(f"Ошибка в формате даты: {date_error}")
                return None
        else:
            # Используем стандартный период, если конкретные даты не указаны
            data = stock.history(period=period)

        # Проверка наличия данных
        if data.empty:
            print(f"Не удалось загрузить данные для тикера {ticker}.")
            return None

        return data

    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return None


def add_moving_average(data, window_size=5):
    """Добавляет скользящее среднее к данным"""
    if data is None:
        return None
    try:
        data['Moving_Average'] = data['Close'].rolling(window=window_size).mean()
        return data
    except Exception as e:
        print(f"Ошибка при расчете скользящего среднего: {e}")
        return data


def calculate_average_price(data):
    """Вычисляет и выводит среднюю цену закрытия за период"""
    if data is None:
        print("Нет данных для расчета средней цены.")
        return None

    try:
        average_price = np.mean(data['Close'])
        print(f"Средняя цена закрытия за период: ${average_price:.2f}")
        return average_price
    except Exception as e:
        print(f"Ошибка при расчете средней цены: {e}")
        return None

def notify_if_strong_fluctuations(data, ticker, threshold=5):
    """
    Анализирует колебания цен акций и уведомляет о значительных изменениях.

    :param data: DataFrame с данными о акциях
    :param ticker: Тикер акции
    :param threshold: Порог колебаний в процентах (по умолчанию 5%)
    :return: Словарь с информацией о колебаниях или None
    """
    if data is None:
        print("Нет данных для анализа колебаний.")
        return None

    try:
        # Получаем цены закрытия
        close_prices = data['Close']

        # Вычисляем минимальную и максимальную цены
        min_price = close_prices.min()
        max_price = close_prices.max()

        # Вычисляем процент колебаний
        price_range_percent = ((max_price - min_price) / min_price) * 100

        # Уведомление о колебаниях
        if price_range_percent > threshold:
            fluctuation_info = {
                'ticker': ticker,
                'min_price': min_price,
                'max_price': max_price,
                'fluctuation_percent': round(price_range_percent, 2)
            }

            print(f"⚠️ ВНИМАНИЕ: Значительные колебания для акций {ticker}!")
            print(f"Диапазон цен: ${min_price:.2f} - ${max_price:.2f}")
            print(f"Процент колебаний: {price_range_percent:.2f}%")

            return fluctuation_info

        return None

    except Exception as e:
        print(f"Ошибка при анализе колебаний: {e}")
        return None


def export_data_to_csv(data, filename):
    """
    Экспортирует данные об акциях в CSV файл.

    :param data: DataFrame с данными об акциях
    :param filename: Имя файла для сохранения
    :return: Путь к сохраненному файлу или None в случае ошибки
    """
    try:
        # Проверка типа входных данных
        if not isinstance(data, pd.DataFrame):
            print("Параметр 'data' должен быть объектом pd.DataFrame")
            return None

        if not isinstance(filename, str):
            print("Параметр 'filename' должен быть строкой")
            return None

        # Добавление расширения .csv, если оно отсутствует
        if not filename.lower().endswith('.csv'):
            filename += '.csv'

        # Проверка существования файла
        if os.path.exists(filename):
            overwrite = input(f"Файл {filename} уже существует. Перезаписать? (да/нет): ").lower()
            if overwrite not in ['да', 'yes', 'y']:
                print("Экспорт отменен.")
                return None

        # Экспорт данных
        data.to_csv(filename, index=True)
        print(f"\nДанные по запросу сохранены в файл {filename}")
        return filename

    except Exception as e:
        print(f"\nОшибка при экспорте данных в CSV: {e}")
        return None


def calculate_rsi(data, periods=14):
    """
    Рассчитывает индекс относительной силы (RSI)

    :param data: DataFrame с данными о ценах закрытия
    :param periods: Количество периодов для расчёта (по умолчанию 14)
    :return: Серия значений RSI или None
    """
    if data is None or 'Close' not in data.columns:
        print("Недостаточно данных для расчета RSI")
        return None

    try:
        # Рассчет изменений цены
        delta = data['Close'].diff()

        # Отдельные серии для роста и падения
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        # Расчет средних значений роста и падения за указанный период
        avg_gain = gain.rolling(window=periods).mean()
        avg_loss = loss.rolling(window=periods).mean()

        # Расчет относительной силы
        relative_strength = avg_gain / avg_loss

        # Расчет RSI
        rsi = 100.0 - (100.0 / (1.0 + relative_strength))

        return rsi
    except Exception as e:
        print(f"Ошибка при расчете RSI: {e}")
        return None


def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
    """
    Рассчитывает индикатор MACD (Moving Average Convergence Divergence)

    :param data: DataFrame с данными о ценах закрытия
    :param fast_period: Период быстрой скользящей средней
    :param slow_period: Период медленной скользящей средней
    :param signal_period: Период сигнальной линии
    :return: DataFrame с MACD, сигнальной линией и гистограммой
    """
    if data is None or 'Close' not in data.columns:
        print("Недостаточно данных для расчета MACD")
        return None

    try:
        # Расчет экспоненциальных скользящих средних
        exp1 = data['Close'].ewm(span=fast_period, adjust=False).mean()
        exp2 = data['Close'].ewm(span=slow_period, adjust=False).mean()

        # Расчет MACD
        macd = exp1 - exp2

        # Расчет сигнальной линии
        signal_line = macd.ewm(span=signal_period, adjust=False).mean()

        # Расчет гистограммы
        histogram = macd - signal_line

        # Создание DataFrame с результатами
        macd_data = pd.DataFrame({
            'MACD': macd,
            'Signal_Line': signal_line,
            'Histogram': histogram
        })

        return macd_data
    except Exception as e:
        print(f"Ошибка при расчете MACD: {e}")
        return None


def add_technical_indicators(data, add_rsi=True, add_macd=True):
    """
    Добавляет технические индикаторы в DataFrame с данными об акциях

    :param data: Исходный DataFrame с данными
    :param add_rsi: Флаг для добавления RSI
    :param add_macd: Флаг для добавления MACD
    :return: DataFrame с добавленными индикаторами
    """
    if data is None:
        print("Нет данных для добавления технических индикаторов")
        return None

    try:
        # Создаем копию DataFrame для безопасного изменения
        indicators_data = data.copy()

        # Добавление RSI
        if add_rsi:
            indicators_data['RSI'] = calculate_rsi(data)

        # Добавление MACD
        if add_macd:
            macd_indicators = calculate_macd(data)
            if macd_indicators is not None:
                indicators_data = pd.concat([indicators_data, macd_indicators], axis=1)

        return indicators_data

    except Exception as e:
        print(f"Ошибка при добавлении технических индикаторов: {e}")
        return None


def calculate_standard_deviation(data: pd.DataFrame, column='Close'):
    """
    Принимает DataFrame с данными о ценах акций и вычисляет стандартное отклонение.

    Parameters:
        data (pd.DataFrame): Данные о ценах акций.
        column (str): Название столбца для расчета (по умолчанию 'Close').

    Returns:
        dict: Словарь со статистическими показателями или None в случае ошибки.
    """
    try:
        # Расширенная статистика
        stats = {
            'std_deviation': data[column].std(ddof=1),
            'variance': data[column].var(ddof=1),
            'min_price': data[column].min(),
            'max_price': data[column].max(),
            'price_range': data[column].max() - data[column].min(),
            'coefficient_variation': (data[column].std() / data[column].mean()) * 100
        }

        # Вывод статистики
        print("\n🔍 Расширенная статистика цен:")
        print(f"Стандартное отклонение: {stats['std_deviation']:.4f}")
        print(f"Дисперсия: {stats['variance']:.4f}")
        print(f"Минимальная цена: ${stats['min_price']:.2f}")
        print(f"Максимальная цена: ${stats['max_price']:.2f}")
        print(f"Диапазон цен: ${stats['price_range']:.2f}")
        print(f"Коэффициент вариации: {stats['coefficient_variation']:.2f}%")

        return stats

    except Exception as e:
        print(f"\n❌ Ошибка при расчете статистики: {e}")
        return None


def advanced_price_analysis(data: pd.DataFrame):
    """
    Проводит углубленный анализ цен акций.

    Parameters:
        data (pd.DataFrame): Данные о ценах акций.

    Returns:
        dict: Словарь с результатами анализа.
    """
    try:
        # Анализ волатильности
        daily_returns = data['Close'].pct_change()
        volatility_stats = {
            'mean_daily_return': daily_returns.mean(),
            'daily_volatility': daily_returns.std(),
            'annualized_volatility': daily_returns.std() * np.sqrt(252)  # Стандартное количество торговых дней
        }

        # Анализ тренда
        trend_stats = {
            'start_price': data['Close'].iloc[0],
            'end_price': data['Close'].iloc[-1],
            'total_return_percent': ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
        }

        # Вывод результатов
        print("\n📊 Углубленный анализ цен:")
        print("Статистика волатильности:")
        print(f"Средняя дневная доходность: {volatility_stats['mean_daily_return']:.4f}")
        print(f"Дневная волатильность: {volatility_stats['daily_volatility']:.4f}")
        print(f"Годовая волатильность: {volatility_stats['annualized_volatility']:.4f}")

        print("\nСтатистика тренда:")
        print(f"Начальная цена: ${trend_stats['start_price']:.2f}")
        print(f"Конечная цена: ${trend_stats['end_price']:.2f}")
        print(f"Общая доходность: {trend_stats['total_return_percent']:.2f}%")

        return {**volatility_stats, **trend_stats}

    except Exception as e:
        print(f"\n❌ Ошибка при углубленном анализе цен: {e}")
        return None