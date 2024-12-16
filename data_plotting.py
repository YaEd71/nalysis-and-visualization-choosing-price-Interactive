import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging


def create_and_show_plot(data, ticker, std_deviation=None):
    """
    Создает интерактивный график с использованием Plotly

    :param data: DataFrame с данными об акциях
    :param ticker: Тикер акции
    :param std_deviation: Словарь со статистикой стандартного отклонения
    """
    try:
        # Создание мультиоконного графика
        fig = make_subplots(
            rows=3,
            cols=1,
            subplot_titles=(
                f'{ticker} - Цена акций',
                'RSI',
                'MACD'
            ),
            vertical_spacing=0.1,
            row_heights=[0.5, 0.25, 0.25]
        )

        # Добавление графика цены закрытия и скользящего среднего
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name='Цена закрытия',
                line=dict(color='blue')
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Moving_Average'],
                mode='lines',
                name='Скользящее среднее',
                line=dict(color='red', dash='dot')
            ),
            row=1, col=1
        )

        # Добавление RSI
        if 'RSI' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['RSI'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='green')
                ),
                row=2, col=1
            )
            # Добавление горизонтальных линий перекупленности/перепроданности
            fig.add_shape(
                type='line',
                x0=data.index[0],
                x1=data.index[-1],
                y0=70, y1=70,
                line=dict(color='Red', width=2, dash='dash'),
                row=2, col=1
            )
            fig.add_shape(
                type='line',
                x0=data.index[0],
                x1=data.index[-1],
                y0=30, y1=30,
                line=dict(color='Green', width=2, dash='dash'),
                row=2, col=1
            )

        # Добавление MACD
        if 'MACD' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['MACD'],
                    mode='lines',
                    name='MACD',
                    line=dict(color='blue')
                ),
                row=3, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['Signal_Line'],
                    mode='lines',
                    name='Сигнальная линия',
                    line=dict(color='red', dash='dot')
                ),
                row=3, col=1
            )
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['Histogram'],
                    name='Гистограмма',
                    marker_color='gray'
                ),
                row=3, col=1
            )

        # Настройка макета
        fig.update_layout(
            height=900,
            title_text=f'Анализ акций {ticker}',
            showlegend=True,
            hovermode='x unified'
        )

        # Добавление аннотаций со статистикой
        if std_deviation:
            annotation_text = (
                f"Мин. цена: ${std_deviation['min_price']:.2f}<br>"
                f"Макс. цена: ${std_deviation['max_price']:.2f}<br>"
                f"Станд. отклонение: {std_deviation['std_deviation']:.4f}<br>"
                f"Диапазон цен: ${std_deviation['price_range']:.2f}"
            )
            fig.add_annotation(
                xref='paper', yref='paper',
                x=1.02, y=0.95,
                text=annotation_text,
                showarrow=False,
                bordercolor='black',
                borderwidth=1,
                borderpad=4,
                bgcolor='white'
            )

        # Сохранение и отображение графика
        filename = f"{ticker}_interactive_chart.html"
        fig.write_html(filename)

        logging.info(f"Интерактивный график сохранен как {filename}")

        return fig

    except Exception as e:
        logging.error(f"Ошибка при создании интерактивного графика: {e}")
        return None

