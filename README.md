# 🏀 NBB Stats API

API REST para consulta de estatísticas do Novo Basquete Brasil (NBB),
construída em Python com FastAPI.

Os dados são obtidos a partir do site oficial da LNB.

---

## 🚀 Tecnologias

- Python 3.10+
- FastAPI
- Pandas
- Uvicorn

---

## 📊 Endpoints

### `GET /stats`

Retorna estatísticas de jogadores ou equipes.

**Parâmetros:**

| Nome | Tipo | Exemplo |
|----|----|----|
| season | string | 2024-25 |
| fase | string | regular |
| categ | string | pontos |
| tipo | string | avg |
| quem | string | athletes |

**Exemplo:**

```http
GET /stats?season=2024-25&fase=regular&categ=pontos
