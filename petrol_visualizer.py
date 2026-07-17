import matplotlib.pyplot as plt
from petrol_scraper import scrape_petrol_prices
import io

def visualize_petrol_prices():
    """
    Fetches data and creates a chart, returning the image as a BytesIO buffer
    for use in environments like AWS Lambda.
    """
    # Fetch data
    data = scrape_petrol_prices()
    
    if data['status'] != 'success' or not data['chart_data']:
        return None

    chart_data = data['chart_data']
    labels = chart_data['labels']
    series = chart_data['series']

    # Setup plotting style (Using a standard style compatible with Lambda)
    plt.style.use('seaborn-v0_8-muted') 
    fig, ax = plt.subplots(figsize=(12, 7), dpi=100)
    
    # Custom colors
    colors = ['#e74c3c', '#2980b9', "#e8ff15"] # Red for RON 95, Blue for Diesel, Green for Premium
    
    # Plot each series
    for i, s in enumerate(series):
        name = s['name']
        values = s['values']
        ax.plot(labels, values, marker='o', linewidth=2.5, markersize=6, label=name, color=colors[i % len(colors)])
        
        # Add value label for the last data point
        if values:
            ax.annotate(f"{int(values[-1]):,}", 
                        xy=(labels[-1], values[-1]), 
                        xytext=(5, 5), 
                        textcoords='offset points',
                        fontsize=10, 
                        fontweight='bold',
                        color=colors[i % len(colors)])

    # Formatting
    ax.set_title(chart_data['name'], fontsize=18, fontweight='bold', pad=20, color='#2c3e50')
    ax.set_xlabel("Ngày điều chỉnh", fontsize=12, labelpad=10)
    ax.set_ylabel("Giá (VNĐ/lít)", fontsize=12, labelpad=10)
    
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(fontsize=12, frameon=True, shadow=True, borderpad=1)
    
    plt.tight_layout()
    
    # Save to buffer instead of disk
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig) # Important to prevent memory leaks in Lambda
    
    return buf

if __name__ == "__main__":
    # Test block
    img_buf = visualize_petrol_prices()
    if img_buf:
        # For testing locally, we can still save it to confirm
        with open("lambda_test_petrol.png", "wb") as f:
            f.write(img_buf.read())
        print("Success: Chart generated in memory and saved to lambda_test_petrol.png for verification.")
