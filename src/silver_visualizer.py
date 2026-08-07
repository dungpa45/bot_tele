import requests
import matplotlib.pyplot as plt
import io
from var_file import *


def fetch_silver_chart_data():
    try:
        response = requests.get(link_vne_finance, headers=header, timeout=10)
        response.raise_for_status()
        return response.json()['data']['data'].get('silver_chart', {})
    except Exception as e:
        print(f"Error fetching silver chart data: {e}")
        return None


def visualize_silver_prices(chart_data=None):
    if chart_data is None:
        chart_data = fetch_silver_chart_data()
    if not chart_data or not chart_data.get('dates'):
        return None

    dates = chart_data['dates'][-30:]
    buy = [v / 1_000_000 for v in chart_data['buy'][-30:]]
    sell = [v / 1_000_000 for v in chart_data['sell'][-30:]]

    try:
        plt.style.use('seaborn-v0_8-muted')
    except OSError:
        plt.style.use('seaborn-muted')
    fig, ax = plt.subplots(figsize=(12, 6), dpi=100)

    ax.plot(dates, sell, marker='o', color='#95a5a6', linewidth=2.5, label='Giá Bán', markersize=4)
    ax.plot(dates, buy, marker='s', color='#2980b9', linewidth=2, linestyle='--', label='Giá Mua', markersize=4)

    if sell:
        ax.annotate(f"{sell[-1]:.2f}", xy=(dates[-1], sell[-1]),
                    xytext=(5, 5), textcoords='offset points', fontweight='bold', color='#7f8c8d')

    ax.set_title("Biến động giá bạc (Triệu VNĐ/lượng)", fontsize=16, fontweight='bold', pad=15)
    ax.grid(True, linestyle=':', alpha=0.7)
    step = max(1, len(dates) // 10)
    ax.set_xticks(range(0, len(dates), step))
    ax.set_xticklabels([dates[i] for i in range(0, len(dates), step)], rotation=45, ha='right')
    ax.legend(loc='upper left')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf


if __name__ == "__main__":
    img_buf = visualize_silver_prices()
    if img_buf:
        with open("images/silver_price_chart.png", "wb") as f:
            f.write(img_buf.read())
        print("Success: Silver chart saved to images/silver_price_chart.png")
