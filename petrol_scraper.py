import requests
import json
import re
import csv
import io
import logging
from datetime import datetime
from var_file import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def fetch_chart_data():
    """
    Fetches dynamic chart data from VNExpress API.
    """

    try:
        response = requests.get(link_xang, headers=header)
        logger.info(f"[chart] GET {link_xang} -> status={response.status_code}")
        response.raise_for_status()
        
        # The response is in JSONP style: vneChart.displayChart(chart_id, {...})
        # We need to extract the JSON object (everything between the first { and last })
        match = re.search(r'(\{.*\})', response.text, re.DOTALL)
        if not match:
            logger.warning(f"[chart] No JSON found in response (len={len(response.text)})")
            return None
            
        full_json = json.loads(match.group(1))
        
        # The actual chart config and data is in 'chart_detail' as a JSON string
        if 'chart_detail' in full_json:
            detail = json.loads(full_json['chart_detail'])
            
            labels = []
            series_data = {} # name -> list of values
            series_names = []
            
            # Check if data is provided as CSV (common for VNE charts)
            csv_text = detail.get('data', {}).get('csv', '')
            if csv_text:
                f = io.StringIO(csv_text)
                # VNE uses semicolon as delimiter
                reader = csv.reader(f, delimiter=';')
                csv_header = next(reader)
                
                # Header format: ["Ngày", "Series 1 Name", "Series 2 Name", ...]
                series_names = csv_header[1:]
                for name in series_names:
                    series_data[name] = []
                
                for row in reader:
                    if not row: continue
                    labels.append(row[0].strip('"'))
                    for i, val in enumerate(row[1:]):
                        if i < len(series_names):
                            name = series_names[i]
                            try:
                                # Convert to int/float if possible
                                series_data[name].append(float(val))
                            except ValueError:
                                series_data[name].append(val)
            else:
                # Fallback to direct xAxis/series extraction if CSV is missing
                labels = detail.get('xAxis', {}).get('categories', [])
                series_list = detail.get('series', [])
                for s in series_list:
                    name = s.get('name')
                    series_names.append(name)
                    series_data[name] = s.get('data', [])
            
            formatted_series = []
            for name in series_names:
                formatted_series.append({
                    "name": name,
                    "values": series_data[name]
                })
                
            return {
                "id": "13169",
                "name": detail.get('title', {}).get('text', 'Diễn biến giá xăng dầu'),
                "labels": labels,
                "series": formatted_series
            }
            
    except Exception as e:
        logger.error(f"[chart] Exception: {e}", exc_info=True)
    return None

def _fetch_prices_from_api() -> tuple[list, str]:
    """Fetch retail petrol prices from VNExpress API (same source the website uses)."""
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
        diff = item.get('diff', 0)
        change = f"+ {diff:,}".replace(',', '.') if diff > 0 else f"- {abs(diff):,}".replace(',', '.') if diff < 0 else "0"
        retail_prices.append({
            "name": item['label'],
            "price": item['price'],
            "change": change
        })
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
