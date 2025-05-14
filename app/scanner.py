import yfinance as yf
import ta
import requests

def obter_tickers_b3():
    try:
        response = requests.get("https://brapi.dev/api/quote/list")
        data = response.json()
        tickers = [item['stock'] + '.SA' for item in data['stocks']]
        return tickers[0:30]
    except Exception as e:
        print("Erro ao obter os tickers da brapi.dev:", e)
        return []

def analisar_ativos(tickers=None):
    if tickers is None:
        tickers = obter_tickers_b3()

    resultados = []

    for ticker in tickers:
        try:
            df = yf.download(ticker, period='1d', interval='5m', auto_adjust=True, progress=False)
            if df.empty:
                continue

            df.columns = df.columns.droplevel(1)
            df.dropna(inplace=True)
            # Garante que 'Close' é uma série unidimensional
            close_series = df['Close']
            # Calcula os indicadores
            df['rsi'] = ta.momentum.RSIIndicator(close=close_series).rsi()
            df['ma_fast'] = ta.trend.SMAIndicator(close=close_series, window=9).sma_indicator()
            df['ma_slow'] = ta.trend.SMAIndicator(close=close_series, window=21).sma_indicator()
            df['macd_diff'] = ta.trend.MACD(close=close_series).macd_diff()

            ultimo = df.iloc[-1]
            cond_compra = (
                ultimo['ma_fast'] > ultimo['ma_slow'] and
                ultimo['macd_diff'] > 0 and
                ultimo['rsi'] < 70
            )
            cond_venda = (
                ultimo['ma_fast'] < ultimo['ma_slow'] and
                ultimo['macd_diff'] < 0 and
                ultimo['rsi'] > 30
            )
            sinal = 'COMPRA' if cond_compra else 'VENDA' if cond_venda else 'NEUTRO'

            resultados.append({
                'ativo': ticker,
                'preco': round(ultimo['Close'], 2),
                'rsi': round(ultimo['rsi'], 2),
                'macd': round(ultimo['macd_diff'], 4),
                'sinal': sinal
            })
        except Exception as e:
            print(e)
            continue

    return resultados
