import streamlit as st
from streamlit_tags import st_tags_sidebar
import pandas as pd
import json
from datetime import datetime
from scraper import fetch_html_selenium, save_raw_data, format_data, save_formatted_data, calculate_price, \
    html_to_markdown_with_readability, create_dynamic_listing_model, create_listings_container_model
from assets import PRICING
import logging

# Đặt page config phải là lệnh đầu tiên
st.set_page_config(page_title="Rita Web Scraper", layout="wide", initial_sidebar_state="expanded")

# Cấu hình CSS tuỳ chỉnh cho giao diện chính
st.markdown(
    """
    <style>
    .main {background-color: #f9f9f9; padding: 20px;}
    .sidebar .sidebar-content {background-color: #343a40;}
    .sidebar .sidebar-content h2, .sidebar-content h3, .sidebar-content h4, .sidebar-content p {
        color: #ffffff;
    }
    .stButton > button {
        background-color: #17a2b8;
        color: #ffffff;
        border-radius: 10px;
        padding: 10px 20px;
    }
    .stButton > button:hover {
        background-color: #138496;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Chèn logo vào sidebar ngay trước tiêu đề "Web Scraper Settings"
st.sidebar.markdown(
    """
    <div style="text-align: center;">
        <img src="https://res.cloudinary.com/dd7gti2kn/image/upload/v1728530830/samples/people/Remove-bg.ai_1728530809560_on5wh1.png" alt="logo" width="150">
    </div>
    """,
    unsafe_allow_html=True
)
#
st.markdown("<h1 style='text-align: center; color: #343a40;'>Rita Scraper 👻</h1>", unsafe_allow_html=True)

# Phần mô tả trang web
st.markdown(
    """
    ## Welcome to Rita Web Scraper 👻

   **Rita Web Scraper** này cho phép bạn scraping data từ bất kỳ trang web nào và trích xuất các trường file  cụ thể dựa trên sở thích của bạn.
   Sử dụng các Model AI của Gemini, OpenAI để phân tích và trích xuất data để tạo dữ liệu có cấu trúc như JSON, CSV và Markdown.

    ### Các tính năng chính
    - Trích xuất dữ liệu từ bất kỳ trang web nào.
    - Chuyển đổi nội dung HTML thành các định dạng có cấu trúc.
    - Tùy chỉnh các trường bạn muốn cạo và tải xuống dữ liệu ở nhiều định dạng.

    Hi vọng project này giúp bạn tiết kiệm thời gian và công sức trong việc thu thập và xử lý dữ liệu từ các nguồn trực tuyến!

    """,
    unsafe_allow_html=True
)
# Sidebar để nhập thông tin
st.sidebar.title("🔧 Web Scraper Settings")
model_selection = st.sidebar.selectbox("📊 Select Model", options=list(PRICING.keys()), index=0)
url_input = st.sidebar.text_input("🌐 Enter URL")

# Input trường dữ liệu trong sidebar
tags = st_tags_sidebar(
    label='🏷️ Enter Fields to Extract:',
    text='Press enter to add a tag',
    value=[],  # Các giá trị mặc định
    suggestions=[],  # Có thể đưa ra gợi ý nếu cần
    maxtags=-1,  # Đặt -1 để không giới hạn số lượng tags
    key='tags_input'
)

# Lưu giá trị tags vào biến fields
fields = tags  # Lưu các thẻ người dùng nhập vào biến fields

# Thông báo lỗi nếu không có trường nào được nhập
if not fields:
    st.sidebar.warning("⚠️ Please enter at least one field to extract.")

st.sidebar.markdown("---")

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Hàm xử lý scraping
def perform_scrape():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw_html = fetch_html_selenium(url_input)
    if raw_html:
        markdown = html_to_markdown_with_readability(raw_html)
        save_raw_data(markdown, timestamp)
        DynamicListingModel = create_dynamic_listing_model(fields)  # Sử dụng fields tại đây
        DynamicListingsContainer = create_listings_container_model(DynamicListingModel)  # Đảm bảo model được tạo
        formatted_data, tokens_count = format_data(markdown, DynamicListingsContainer, DynamicListingModel, model_selection)
        input_tokens, output_tokens, total_cost = calculate_price(tokens_count, model=model_selection)
        df = save_formatted_data(formatted_data, timestamp)
        return df, formatted_data, markdown, input_tokens, output_tokens, total_cost, timestamp
    else:
        st.error("⚠️ Failed to fetch data from the URL.")
        return None, None, None, 0, 0, 0, None


# Nút bấm để chạy scraping
if 'perform_scrape' not in st.session_state:
    st.session_state['perform_scrape'] = False

if st.sidebar.button("🚀 Start Scraping"):
    with st.spinner('⏳ Please wait... Scraping in progress.'):
        st.session_state['results'] = perform_scrape()
        st.session_state['perform_scrape'] = True

# Hiển thị kết quả sau khi scraping
if st.session_state.get('perform_scrape'):
    df, formatted_data, markdown, input_tokens, output_tokens, total_cost, timestamp = st.session_state['results']

    if df is not None:
        st.markdown("### 🎯 Scraped Data")
        st.dataframe(df)  # Hiển thị bảng có thể tương tác

        st.sidebar.markdown("## 📊 Token Usage")
        st.sidebar.markdown(f"**Input Tokens:** {input_tokens}")
        st.sidebar.markdown(f"**Output Tokens:** {output_tokens}")
        st.sidebar.markdown(f"**Total Cost:** :green-background[***${total_cost:.4f}***]")

        # Các nút download kết quả
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button("📥 Download JSON",
                               data=json.dumps(formatted_data.dict() if hasattr(formatted_data, 'dict') else formatted_data,
                                               indent=4), file_name=f"{timestamp}_data.json")
        with col2:
            if isinstance(formatted_data, str):
                data_dict = json.loads(formatted_data)
            else:
                data_dict = formatted_data.dict() if hasattr(formatted_data, 'dict') else formatted_data

            first_key = next(iter(data_dict))  # Lấy key đầu tiên
            main_data = data_dict[first_key]  # Truy cập dữ liệu bằng key
            df = pd.DataFrame(main_data)

            st.download_button("📊 Download CSV", data=df.to_csv(index=False), file_name=f"{timestamp}_data.csv")
        with col3:
            st.download_button("📄 Download Markdown", data=markdown, file_name=f"{timestamp}_data.md")

if 'results' in st.session_state:
    df, formatted_data, markdown, input_tokens, output_tokens, total_cost, timestamp = st.session_state['results']
