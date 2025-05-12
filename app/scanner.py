import yfinance as yf
import ta
import requests

def obter_tickers_b3():
    url = "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetInitialCompanies/true"
    try:
        response = requests.get(url)
        data = response.json()
        tickers = [empresa['stockCode'] + '.SA' for empresa in data['companies']]
        return tickers
    except Exception as e:
        print("Erro ao obter os tickers da B3:", e)
        return []

def analisar_ativos(tickers=None):
    if tickers is None:
        tickers = obter_tickers_b3()

    resultados = []

    for ticker in tickers:
        try:
            df = yf.download(ticker, period='1d', interval='5m', progress=False)
            if df.empty:
                continue

            df.dropna(inplace=True)
            df['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()
            df['ma_fast'] = ta.trend.SMAIndicator(df['Close'], window=9).sma_indicator()
            df['ma_slow'] = ta.trend.SMAIndicator(df['Close'], window=21).sma_indicator()
            macd = ta.trend.MACD(df['Close'])
            df['macd_diff'] = macd.macd_diff()

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
        except:
            continue

    return resultados