import pandas as pd
import numpy as np

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

def get_stats(
    season: str,
    fase: str,
    categ: str,
    tipo: str = 'avg',
    quem: str = 'athletes',
    sofrido: bool = False
):
    season2 = season_dict[season]
    sofrido = sofrido_dict[sofrido]
    fase = fase_dict[fase]

    url = (
        f"https://lnb.com.br/nbb/estatisticas/{categ}/"
        f"?aggr={tipo}&type={quem}&suffered_rule={sofrido}"
        f"&season%5B%5D={season2}&phase{fase}"
    )

    df = pd.read_html(url)[0]

    if quem == 'athletes':
        df['Camisa'] = df['Jogador'].str.split(' #').str[1]
        df['Jogador'] = df['Jogador'].str.split(' #').str[0]

    df = df.drop(columns=['Pos.'], errors='ignore')
    df['Temporada'] = season

    return df  # ✅ DataFrame
