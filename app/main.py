from fastapi import FastAPI, Query
from typing import Optional
from app.scanner import analisar_ativos

app = FastAPI()

@app.get("/")
def root():
    return {"status": "online", "message": "Day Trade API ativa"}

@app.get("/analise")
def analise(tickers: Optional[str] = Query(default=None)):
    if tickers:
        lista = [t.strip() for t in tickers.split(",")]
        return analisar_ativos(lista)
    else:
        return analisar_ativos()