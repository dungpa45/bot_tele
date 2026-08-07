import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="XSMB API Free", description="API lấy kết quả xổ số miền Bắc (Nguồn az24.vn)")

# Cấu hình CORS để thoải mái gọi API từ các domain khác (Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def scrape_xsmb_az24(date_str: str = None) -> dict:
    """
    Cào dữ liệu XSMB từ az24.vn.
    date_str định dạng DD-MM-YYYY (Ví dụ: 17-07-2026)
    """
    if date_str:
        # Đường dẫn xem theo ngày cụ thể của az24.vn
        url = f"https://az24.vn/xsmb-{date_str}.html"
    else:
        # Đường dẫn mặc định lấy ngày mới nhất hôm nay
        url = "https://az24.vn/xsmb-sxmb-xo-so-mien-bac.html"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "vi,en-US;q=0.7,en;q=0.3"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Không thể kết nối đến nguồn dữ liệu az24 (Mã lỗi: {response.status_code}).")
            
        soup = BeautifulSoup(response.content, "html.parser")

        # az24.vn dùng table.kqmb cho bảng XSMB
        table = soup.find("table", class_="kqmb")
        if not table:
            raise HTTPException(status_code=404, detail="Không tìm thấy bảng kết quả xổ số trên trang. Cấu trúc trang có thể đã thay đổi.")

        # Lấy tiêu đề ngày từ thẻ h1/h2 gần nhất
        title_element = soup.find("h1") or soup.find("h2")
        actual_title = title_element.text.strip() if title_element else "Kết quả Xổ số Miền Bắc"

        result = {
            "title": "Xổ số Kiến thiết Miền Bắc",
            "date_info": actual_title,
            "results": {}
        }

        # Mapping tên giải theo ký hiệu cột đầu tiên trong bảng
        label_mapping = {
            "ĐB": "Đặc biệt",
            "G1": "Giải nhất",
            "G2": "Giải nhì",
            "G3": "Giải ba",
            "G4": "Giải tư",
            "G5": "Giải năm",
            "G6": "Giải sáu",
            "G7": "Giải bảy",
        }

        for row in table.find_all("tr"):
            tds = row.find_all("td")
            if len(tds) < 2:
                continue
            label = tds[0].text.strip()
            if label in label_mapping:
                spans = tds[1].find_all("span")
                if spans:
                    numbers = [s.text.strip() for s in spans if s.text.strip()]
                else:
                    numbers = [n.strip() for n in tds[1].text.split() if n.strip()]
                result["results"][label_mapping[label]] = numbers

        if not any(result["results"].values()):
            raise HTTPException(status_code=404, detail="Không cào được dữ liệu số nào. Cấu trúc trang web nguồn có thể đã thay đổi.")

        return result

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Lỗi kết nối mạng: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý hệ thống: {str(e)}")


@app.get("/api")
def get_xsmb(date: str = Query(None, description="Định dạng: DD-MM-YYYY (Ví dụ: 17-07-2026). Để trống để lấy kết quả mới nhất.")):
    """ Endpoint chính thức để lấy dữ liệu XSMB """
    return scrape_xsmb_az24(date)


if __name__ == "__main__":
    import uvicorn
    # Chạy server cục bộ tại port 8000
    uvicorn.run("api_xsmb:app", host="0.0.0.0", port=8000, reload=True)