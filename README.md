# Rita Web Scraper

## Giới thiệu
**Rita Web Scraper** là một công cụ tự động hóa giúp bạn trích xuất dữ liệu từ các trang web và chuyển đổi chúng thành các định dạng có cấu trúc như JSON, CSV và Markdown. Công cụ này sử dụng các mô hình AI như Gemini và OpenAI để phân tích và trích xuất dữ liệu một cách thông minh.

## Tính năng chính
- **Trích xuất dữ liệu từ bất kỳ trang web nào**: Sử dụng Selenium để thu thập dữ liệu HTML từ các trang web.
- **Chuyển đổi dữ liệu**: Chuyển đổi nội dung HTML thành Markdown và các định dạng có cấu trúc như JSON và CSV.
- **Tùy chỉnh trường dữ liệu**: Cho phép người dùng nhập các trường dữ liệu cụ thể để trích xuất.
- **Hỗ trợ nhiều mô hình AI**: Sử dụng các mô hình AI như Gemini, OpenAI để phân tích và trích xuất dữ liệu.
- **Tính toán chi phí**: Tính toán chi phí dựa trên số lượng token sử dụng.

## Yêu cầu hệ thống
- Python 3.x
- Các thư viện cần thiết:
  - `streamlit`
  - `selenium`
  - `pandas`
  - `beautifulsoup4`
  - `html2text`
  - `pydantic`
  - `openai`
  - `google-generativeai`
  - `groq`

## Cài đặt
1. **Clone repository**:
   ```bash
   git clone https://github.com/your-repo/rita-web-scraper.git
   cd rita-web-scraper
   ```
2. **Cài đặt các thư viện cần thiết**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Cấu hình API keys**:
   - Tạo file `config.py` và thêm các API keys của bạn:
     ```python
     # config.py
     OPENAI_API_KEY = "your-openai-api-key"
     GOOGLE_API_KEY = "your-google-api-key"
     GROQ_API_KEY = "your-groq-api-key"
     ```

## Cách chạy
1. **Khởi chạy ứng dụng Streamlit**:
   ```bash
   streamlit run streamlit_app.py
   ```
2. **Nhập URL và các trường dữ liệu**:
   - Nhập URL của trang web bạn muốn trích xuất dữ liệu.
   - Nhập các trường dữ liệu bạn muốn trích xuất.
3. **Bắt đầu trích xuất**:
   - Nhấn nút "Start Scraping" để bắt đầu quá trình trích xuất dữ liệu.

## Cấu trúc thư mục
```
rita-web-scraper/
├── streamlit_app.py        # File chính chứa giao diện người dùng
├── scraper.py              # File chứa logic trích xuất và xử lý dữ liệu
├── assets.py               # File chứa các cấu hình và hằng số
├── config.py               # File chứa các API keys
├── README.md               # File hướng dẫn
└── requirements.txt        # File chứa các thư viện cần thiết
```

## Lưu ý
- Đảm bảo rằng bạn đã cài đặt đúng phiên bản của ChromeDriver tương thích với trình duyệt Chrome của bạn.
- Quá trình trích xuất dữ liệu có thể mất nhiều thời gian tùy thuộc vào kích thước và độ phức tạp của trang web.

## Hỗ trợ
Nếu bạn gặp bất kỳ vấn đề nào, vui lòng liên hệ qua email hoặc tạo issue trên GitHub.
