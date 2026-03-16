import requests
from bs4 import BeautifulSoup, Tag
import json
import re
import csv
import io
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def fetch_chart_data(chart_id):
    """
    Fetches dynamic chart data from VNExpress API.
    """
    url = f"https://usi-saas.vnexpress.net/chart/get?chart_id={chart_id}&deviceenv=4"
    headers = {
        "Referer": "https://vnexpress.net/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        logger.info(f"[chart] GET {url} -> status={response.status_code}")
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
                header = next(reader)
                
                # Header format: ["Ngày", "Series 1 Name", "Series 2 Name", ...]
                series_names = header[1:]
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
                "id": chart_id,
                "name": detail.get('title', {}).get('text', 'Diễn biến giá xăng dầu'),
                "labels": labels,
                "series": formatted_series
            }
            
    except Exception as e:
        logger.error(f"[chart] Exception: {e}", exc_info=True)
    return None

def scrape_petrol_prices() -> dict:
    url = "https://vnexpress.net/chu-de/gia-xang-dau-3026"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        logger.info(f"[petrol] Fetching {url}")
        response = requests.get(url, headers=headers, timeout=10)
        logger.info(f"[petrol] GET {url} -> status={response.status_code}, len={len(response.text)}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Scrape "Giá bán lẻ xăng dầu hôm nay" table
        retail_prices = []
        table_header = soup.find('h2', string=lambda t: bool(t and 'Giá bán lẻ xăng dầu hôm nay' in t))
        logger.info(f"[petrol] table_header found: {table_header is not None}")
        if isinstance(table_header, Tag):
            table = table_header.find_next('table')
            if isinstance(table, Tag):
                rows = table.find_all('tr')[1:] # Skip header row
                for row in rows:
                    if not isinstance(row, Tag):
                        continue
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        name = cols[0].get_text(strip=True)
                        price_text = cols[1].get_text(strip=True).replace('.', '')
                        change = cols[2].get_text(strip=True)
                        retail_prices.append({
                            "name": name,
                            "price": int(price_text) if price_text.isdigit() else price_text,
                            "change": change
                        })
        
        logger.info(f"[petrol] Scraped {len(retail_prices)} retail prices")
        
        # 2. Dynamically fetch chart data (id=13169)
        chart_data = fetch_chart_data("13169")
        logger.info(f"[petrol] chart_data fetched: {chart_data is not None}")
        
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "retail_prices": retail_prices,
            "chart_data": chart_data
        }
        
        return result

    except Exception as e:
        logger.error(f"[petrol] Exception: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    data = scrape_petrol_prices()
    print(json.dumps(data, indent=2, ensure_ascii=False))
