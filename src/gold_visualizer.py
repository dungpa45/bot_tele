import requests
import json
import matplotlib.pyplot as plt
import io
from datetime import datetime

class GoldScraper:
    def __init__(self):
        self.api_url = "https://gw.vnexpress.net/cr/?name=tygia_vangv202206"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_data(self):
        try:
            response = requests.get(self.api_url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching gold data: {e}")
            return None

    def process_data(self, raw_data):
        if not raw_data or raw_data.get('code') != 200:
            return None
        
        main_data = raw_data['data']['data']
        gold_prices = main_data.get('gold', {}).get('new', {})
        processed_table = []
        
        key_map = {
            'sjc_1l_10l': 'Vàng SJC (1L-10L)',
            'tphcm_pnj': 'PNJ (TP.HCM)',
            'thegioi': 'Vàng Thế giới'
        }
        
        for key, name in key_map.items():
            item = gold_prices.get(key)
            if item:
                processed_table.append({
                    "name": name,
                    "buy": item.get('buy'),
                    "sell": item.get('sell'),
                    "change": item.get('change')
                })
        
        chart_source = main_data.get('chart', {})
        sjc_chart = chart_source.get('sjc_1l_10l', [])[::-1]
        
        return {
            "table": processed_table,
            "charts": {
                "sjc": {
                    "labels": [d['date_label'] for d in sjc_chart],
                    "buy": [float(d['buy']) for d in sjc_chart],
                    "sell": [float(d['sell']) for d in sjc_chart]
                }
            },
            "timestamp": datetime.now().isoformat()
        }

def visualize_gold_sjc(data):
    """
    Returns SJC gold chart as a BytesIO buffer.
    """
    if not data or 'sjc' not in data.get('charts', {}):
        return None
    
    sjc = data['charts']['sjc']
    plt.style.use('seaborn-v0_8-muted')
    fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
    
    # Gold colors
    ax.plot(sjc['labels'], sjc['sell'], marker='o', color='#f1c40f', linewidth=2.5, label='Giá Bán')
    ax.plot(sjc['labels'], sjc['buy'], marker='s', color='#2980b9', linewidth=2, linestyle='--', label='Giá Mua')
    
    if sjc['sell']:
        ax.annotate(f"{int(sjc['sell'][-1]):,}", xy=(sjc['labels'][-1], sjc['sell'][-1]), 
                    xytext=(5, 5), textcoords='offset points', fontweight='bold', color='#d35400')

    ax.set_title("Biến động giá vàng SJC (Triệu VNĐ/lượng)", fontsize=16, fontweight='bold', pad=15)
    ax.grid(True, linestyle=':', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    ax.legend(loc='upper left')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return buf

if __name__ == "__main__":
    scraper = GoldScraper()
    raw = scraper.fetch_data()
    processed = scraper.process_data(raw)
    
    if processed:
        img_buf = visualize_gold_sjc(processed)
        if img_buf:
            with open("lambda_test_gold.png", "wb") as f:
                f.write(img_buf.read())
            print("Success: Gold chart generated in memory and saved to lambda_test_gold.png.")
