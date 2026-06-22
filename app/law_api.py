"""법제처 Open API 연동 모듈"""
import httpx
from typing import Optional

LAW_BASE = "https://www.law.go.kr/DRF"


async def search_laws(
    query: str,
    api_key: str,
    page: int = 1,
    count: int = 5,
    law_type: str = "law",  # law | ordinance | regulation
) -> dict:
    """법령 목록 검색"""
    type_map = {"law": "lsInfoP", "ordinance": "orLsInfoP", "regulation": "admRulLsInfoP"}
    endpoint = type_map.get(law_type, "lsInfoP")

    params = {
        "target": endpoint,
        "query": query,
        "page": page,
        "display": count,
        "search": 1,
        "type": "JSON",
        "OC": api_key,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{LAW_BASE}/lawSearch.do", params=params)
        resp.raise_for_status()
        return resp.json()


async def get_law_text(law_id: str, api_key: str) -> dict:
    """법령 본문 조회 (법령 ID 또는 법령명)"""
    params = {
        "target": "law",
        "ID": law_id,
        "type": "JSON",
        "OC": api_key,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{LAW_BASE}/lawService.do", params=params)
        resp.raise_for_status()
        return resp.json()


async def search_precedents(
    query: str,
    api_key: str,
    court_type: str = "400201",  # 대법원
    page: int = 1,
    count: int = 5,
) -> dict:
    """판례 검색"""
    params = {
        "target": "prec",
        "query": query,
        "page": page,
        "display": count,
        "courtType": court_type,
        "type": "JSON",
        "OC": api_key,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{LAW_BASE}/lawSearch.do", params=params)
        resp.raise_for_status()
        return resp.json()


async def get_law_interpretation(query: str, api_key: str, page: int = 1) -> dict:
    """법령 해석례 검색"""
    params = {
        "target": "expc",
        "query": query,
        "page": page,
        "display": 5,
        "type": "JSON",
        "OC": api_key,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{LAW_BASE}/lawSearch.do", params=params)
        resp.raise_for_status()
        return resp.json()
