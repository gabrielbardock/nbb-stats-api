from datetime import datetime, timedelta, timezone
from app.supabase_client import supabase

import pandas as pd
import numpy as np
import requests

CACHE_TTL = timedelta(hours=1)

season_dict = {
    '2008-09':'1','2009-10':'2','2010-11':'3','2011-12':'4',
    '2012-13':'8','2013-14':'15','2014-15':'20','2015-16':'27',
    '2016-17':'34','2017-18':'41','2018-19':'47','2019-20':'54',
    '2020-21':'59','2021-22':'63','2022-23':'71','2023-24':'80',
    '2024-25':'88','2025-26':'97'
}

fase_dict = {
    'regular':'%5B%5D=1',
    'playoffs':'%5B%5D=2',
    'total':'=on&phase%5B%5D=1&phase%5B%5D=2'
}

sofrido_dict = {False:'0', True:'1'}


# =========================
# CACHE
# =========================

def get_cached_stats(season, fase, categ, tipo, quem):
    res = (
        supabase.table("nbb_stats_cache")
        .select("data, updated_at")
        .eq("season", season)
        .eq("fase", fase)
        .eq("categ", categ)
        .eq("tipo", tipo)
        .eq("quem", quem)
        .limit(1)
        .execute()
    )

    if not res.data:
        return None

    row = res.data[0]

    # ✅ mantém timezone
    updated = datetime.fromisoformat(
        row["updated_at"].replace("Z", "+00:00")
    )

    # ✅ usa UTC explícito
    if datetime.now(timezone.utc) - updated < CACHE_TTL:
        print("📦 cache hit")
        return pd.DataFrame(row["data"])

    return None


def save_stats_cache(season, fase, categ, tipo, quem, df):
    supabase.table("nbb_stats_cache").upsert({
        "season": season,
        "fase": fase,
        "categ": categ,
        "tipo": tipo,
        "quem": quem,
        "data": df.to_dict(orient="records")
    }, on_conflict="season,fase,categ,tipo,quem").execute()


# =========================
# STATS PRINCIPAL
# =========================

def get_stats(
    season: str,
    fase: str,
    categ: str,
    tipo: str = 'avg',
    quem: str = 'athletes',
    sofrido: bool = False
):
    # 1️⃣ tenta cache
    cached = get_cached_stats(season, fase, categ, tipo, quem)
    if cached is not None:
        return cached

    # 2️⃣ scraping
    season2 = season_dict[season]
    sofrido = sofrido_dict[sofrido]
    fase_qs = fase_dict[fase]

    url = (
        f"https://lnb.com.br/nbb/estatisticas/{categ}/"
        f"?aggr={tipo}&type={quem}&suffered_rule={sofrido}"
        f"&season%5B%5D={season2}&phase{fase_qs}"
    )

    df = pd.read_html(url)[0]

    if quem == 'athletes':
        df['Camisa'] = df['Jogador'].str.split(' #').str[1]
        df['Jogador'] = df['Jogador'].str.split(' #').str[0]

    df = df.drop(columns=['Pos.'], errors='ignore')
    df['Temporada'] = season

    # 3️⃣ salva cache
    save_stats_cache(season, fase, categ, tipo, quem, df)
    print("🌐 cache miss — salvando")

    return df


def get_season_stages(season_id: str):
    url = "https://lnb.com.br/ajax-season-stages/"
    params = {"season": season_id}
    
    headers = {
        "User-Agent": "Mozilla/5.0", # Identificação básica
        "X-Requested-With": "XMLHttpRequest"
    }

    # Faz a requisição e retorna o texto puro (HTML ou JSON) que o site enviar
    response = requests.get(url, params=params, headers=headers, verify=False)
    
    # Se o site retornar JSON, o .json() funciona. 
    # Se retornar HTML, o .text retorna a string bruta.
    try:
        return response.json()
    except:
        return response.text
    
def get_season_teams(season_id: str):
    url = "https://lnb.com.br/ajax-season-teams/"
    params = {"season": season_id}
    
    headers = {
        "User-Agent": "Mozilla/5.0", # Identificação básica
        "X-Requested-With": "XMLHttpRequest"
    }

    # Faz a requisição e retorna o texto puro (HTML ou JSON) que o site enviar
    response = requests.get(url, params=params, headers=headers, verify=False)
    
    # Se o site retornar JSON, o .json() funciona. 
    # Se retornar HTML, o .text retorna a string bruta.
    try:
        return response.json()
    except:
        return response.text
    
def get_team_players(teamid: str):
    url = "https://lnb.com.br/ajax-atletas/"
    params = {"teamid": teamid}
    
    headers = {
        "User-Agent": "Mozilla/5.0", # Identificação básica
        "X-Requested-With": "XMLHttpRequest"
    }

    # Faz a requisição e retorna o texto puro (HTML ou JSON) que o site enviar
    response = requests.get(url, params=params, headers=headers, verify=False)
    
    # Se o site retornar JSON, o .json() funciona. 
    # Se retornar HTML, o .text retorna a string bruta.
    try:
        return response.json()
    except:
        return response.text
    
def sync_season_teams(season: str):
    teams = get_season_teams(season)

    rows = []
    for t in teams:
        rows.append({
            "id": t["id"],
            # "name": t.get("shortname"),
            "shortname": t.get("shortname"),
            "season": season
        })

    supabase.table("nbb_teams").upsert(rows).execute()
    return rows

def sync_team_players(season: str, team_id: str, team_name: str):
    players = get_team_players(team_id)

    rows = []
    for p in players:
        rows.append({
            "id": p["id"],
            "name": p["name"],
            "number": p.get("number"),
            "avatar": p.get("avatar"),
            "team_id": team_id,
            "team_name": team_name,
            "season": season
        })

    supabase.table("nbb_players").upsert(rows).execute()
    return rows

def sync_season(season: str):
    teams = sync_season_teams(season)

    for team in teams:
        sync_team_players(
            season=season,
            team_id=team["id"],
            team_name=team.get("shortname")
        )

    return {"status": "ok", "teams": len(teams)}