import requests
import json
import logging
import base64
from datetime import datetime
from var_file import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def fetch_chart_data():
    """
    Fetches petrol chart data from VNExpress finance API (gw.vnexpress.net).
    """
    try:
        response = requests.get(link_vne_finance, headers=header, timeout=10)
        logger.info(f"[chart] GET {link_vne_finance} -> status={response.status_code}")
        response.raise_for_status()

        chart = response.json().get('data', {}).get('data', {}).get('gas_oil_chart', {})
        if not chart:
            logger.warning("[chart] No gas_oil_chart data found")
            return None

        labels = chart.get('dates', [])
        series_map = {
            'ron_95': 'Xăng RON 95',
            'e5_ron_92': 'Xăng E5 RON 92',
            'dau_diesel': 'Dầu Diesel',
        }
        formatted_series = []
        for key, name in series_map.items():
            values = chart.get(key, [])
            formatted_series.append({"name": name, "values": [float(v) for v in values]})

        return {
            "id": "gas_oil_chart",
            "name": "Diễn biến giá xăng dầu trong nước",
            "labels": labels,
            "series": formatted_series
        }

    except Exception as e:
        logger.error(f"[chart] Exception: {e}", exc_info=True)
    return None

def _fetch_petrolimex_extras() -> list:
    """Fetch extra fuel types from Petrolimex that VNExpress doesn't have."""
    try:
        payload = json.dumps({
            "FilterBy": {"And": [
                {"SystemID": {"Equals": "6783dc1271ff449e95b74a9520964169"}},
                {"RepositoryID": {"Equals": "a95451e23b474fe5886bfb7cf843f53c"}},
                {"RepositoryEntityID": {"Equals": "3801378fe1e045b1afa10de7c5776124"}},
                {"Status": {"Equals": "Published"}}
            ]},
            "SortBy": {"LastModified": "Descending"},
            "Pagination": {"TotalRecords": -1, "TotalPages": 0, "PageSize": 0, "PageNumber": 0}
        }, separators=(',', ':'))
        encoded = base64.urlsafe_b64encode(payload.encode()).decode().rstrip('=')
        url = f"https://portals.petrolimex.com.vn/~apis/portals/cms.item/search?x-request={encoded}&language=vi-VN"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        objects = response.json().get('Objects', [])

        # Only get types that VNExpress doesn't provide
        extra_aliases = {'ron-95-v', 'e10-ron-95-v', 'e10-ron-95-iii'}
        extras = []
        for obj in sorted(objects, key=lambda x: x.get('DIsplayOrder', 99)):
            if obj.get('Alias') in extra_aliases:
                price = obj.get('Zone1Price', 0)
                if price > 0:
                    extras.append({"name": obj['Title'], "price": price, "change": "—"})
        return extras
    except Exception as e:
        logger.warning(f"[petrolimex] Failed to fetch extras: {e}")
        return []

def _fetch_prices_from_api() -> tuple[list, str]:
    """Fetch retail petrol prices from VNExpress API, supplemented by Petrolimex extras."""
    response = requests.get(link_vne_finance, headers=header, timeout=10)
    response.raise_for_status()
    gas_oil = response.json().get('data', {}).get('data', {}).get('gas_oil', {})
    if not gas_oil:
        return [], ''

    date_label = gas_oil.get('date_label', '')
    retail_prices = []
    for key in ['ron_95', 'e5_ron_92', 'dau_diesel', 'dau_hoa', 'dau_madut']:
        item = gas_oil.get(key)
        if not item:
            continue
        if item.get('price', 0) == 0:
            continue
        diff = item.get('diff', 0)
        change = f"+ {diff:,}".replace(',', '.') if diff > 0 else f"- {abs(diff):,}".replace(',', '.') if diff < 0 else "0"
        retail_prices.append({
            "name": item['label'],
            "price": item['price'],
            "change": change
        })

    # Append extra types from Petrolimex (RON 95-V, E10 RON 95-V, E10 RON 95-III)
    extras = _fetch_petrolimex_extras()
    retail_prices.extend(extras)

    return retail_prices, date_label

def scrape_petrol_prices() -> dict:
    try:
        # 1. Fetch retail prices from VNExpress API
        retail_prices, date_label = _fetch_prices_from_api()
        logger.info(f"[petrol] API returned {len(retail_prices)} prices, date={date_label}")

        # 2. Fetch chart data
        chart_data = fetch_chart_data()
        logger.info(f"[petrol] chart_data fetched: {chart_data is not None}")

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "date_label": date_label,
            "retail_prices": retail_prices,
            "chart_data": chart_data
        }

    except Exception as e:
        logger.error(f"[petrol] Exception: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    data = scrape_petrol_prices()
    print(json.dumps(data, indent=2, ensure_ascii=False))
