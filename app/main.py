from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.supabase_client import supabase
from app.nbb import get_season_stages, get_season_teams, get_stats, get_team_players, sync_season

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

# Mantemos os outros como estão, pois são metadados menores
@app.get("/ajax-season-stages")
def ajax_season_stages(season: str):
    return get_season_stages(season)

@app.get("/ajax-season-teams")
def ajax_season_teams(season: str):
    return get_season_teams(season)

@app.get("/ajax-team-players")
def ajax_team_players(teamid: str):
    return get_team_players(teamid)

@app.get("/sync/season")
def sync(season: str):
    return sync_season(season)

@app.get("/teams")
def get_teams(season: str):
    res = (
        supabase.table("nbb_teams")
        .select("*")
        .eq("season", season)
        .order("shortname")
        .execute()
    )
    return res.data

@app.get("/players")
def get_players(
    season: str,
    team_id: str | None = None,
    limit: int = 50,
    offset: int = 0
):
    q = (
        supabase.table("nbb_players")
        .select("*")
        .eq("season", season)
        .order("name")
        .range(offset, offset + limit - 1)
    )

    if team_id:
        q = q.eq("team_id", team_id)

    return q.execute().data

@app.get("/health")
def health():
    return {"status": "ok"}
