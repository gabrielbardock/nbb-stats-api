from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.nbb import get_stats

app = FastAPI(title="NBB Stats API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stats")
def stats(
    season: str,
    fase: str,
    categ: str,
    tipo: str = "avg",
    quem: str = "athletes"
):
    df = get_stats(season, fase, categ, tipo, quem)
    return df.to_dict(orient="records")  # ✅ aqui é o lugar certo
