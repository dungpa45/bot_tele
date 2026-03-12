# Linhtinh Bot & Telegram Bot Tools

Multi-functional Telegram bot built with Python, designed for stability and fun. Now featuring robust error handling and a comprehensive testing suite.

## 🌟 Key Features

### 🛠️ Robust Systems
- **Exception Handling**: Every API call and data processing step is wrapped in try-except blocks.
- **User Feedback**: If an error occurs (API down, invalid input), the bot proactively notifies the user via Telegram instead of failing silently.
- **Smart Validation**: Improved IP and CIDR address validation using strict regex and the `ipaddress` module.

### 🎮 Bot Commands
```bash
/quote          - Xem một câu quote truyền cảm hứng
/fact           - Xem các sự thật thú vị
/uselessfact    - Xem các sự thật vô tri
/meal           - Xem gợi ý về một món ăn kèm công thức và video
/cocktail       - Xem công thức pha chế cocktail
/an_trua        - Gợi ý món ăn trưa nay (hoặc /antrua)
/country        - Xem thông tin chi tiết một quốc gia bất kỳ
/news [n]       - Xem [n] tin tức mới nhất từ VnExpress (mặc định 1)
/aws [n]        - Xem [n] tin tức công nghệ AWS mới nhất
/weather        - Xem thời tiết và chỉ số ô nhiễm (AQI) tại Hà Nội
/gold           - Cập nhật giá vàng mới nhất
/xsmb           - Kết quả Xổ Số Miền Bắc hôm nay
/xang           - Cập nhật giá xăng dầu mới nhất
/football_price - Xem giá trị thị trường của các cầu thủ bóng đá hàng đầu
[URL bất kỳ]    - Tự động rút gọn liên kết
[IP/CIDR]       - Kiểm tra thông tin mạng và Subnet
```

## 🚀 Installation & Setup

1. **Requirements**:
   ```bash
   pip install requests feedparser googletrans==3.1.0a0 beautifulsoup4 tabulate pytest pytest-mock
   ```

2. **Environment**:
   Ensure your `var_file.py` contains all necessary API Tokens (`TOKEN`, `API_WEATHER`, `API_AIRVISUAL`, `API_NINJA`, etc.).

## 🧪 Testing

We use **Pytest** for automated logic verification. The test suite mocks external APIs to ensure reliable results without hitting rate limits.

Run all tests:
```bash
export PYTHONPATH=$PYTHONPATH:.
pytest test_bot_pytest.py
```

Covered in tests:
- Weather logic (Temp conversion, Emoji mapping, AQI ranges)
- Networking tools (IP/CIDR validation)
- Core Lambda handler (Command processing, Edited message detection)
- Fallback mechanisms (Translation errors, API failures)

---
#### Make guys sweet again!
