import os
import random
import time
import re
import json
import logging
from datetime import datetime
from typing import List, Dict, Type

import pandas as pd
from bs4 import BeautifulSoup
from pydantic import BaseModel, create_model
import html2text
import tiktoken

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from openai import OpenAI
import google.generativeai as genai
from groq import Groq

from config import OPENAI_API_KEY, GOOGLE_API_KEY, GROQ_API_KEY
from assets import USER_AGENTS, PRICING, HEADLESS_OPTIONS, SYSTEM_MESSAGE, USER_MESSAGE, LLAMA_MODEL_FULLNAME, GROQ_LLAMA_MODEL_FULLNAME

logging.basicConfig(level=logging.INFO)

def setup_selenium():
    options = Options()
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"user-agent={user_agent}")
    for option in HEADLESS_OPTIONS:
        options.add_argument(option)
    service = Service(r"./chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def fetch_html_selenium(url):
    driver = setup_selenium()
    try:
        driver.get(url)
        time.sleep(1)
        driver.maximize_window()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        html = driver.page_source
        return html
    except Exception as e:
        logging.error(f"Lỗi khi fetch HTML bằng Selenium: {e}")
    finally:
        driver.quit()

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for element in soup.find_all(['header', 'footer']):
        element.decompose()
    return str(soup)

def html_to_markdown_with_readability(html_content):
    cleaned_html = clean_html(html_content)
    markdown_converter = html2text.HTML2Text()
    markdown_converter.ignore_links = False
    return markdown_converter.handle(cleaned_html)

def save_raw_data(raw_data, timestamp, output_folder='output'):
    os.makedirs(output_folder, exist_ok=True)
    raw_output_path = os.path.join(output_folder, f'rawData_{timestamp}.md')
    with open(raw_output_path, 'w', encoding='utf-8') as f:
        f.write(raw_data)
    logging.info(f"Dữ liệu thô đã lưu tại: {raw_output_path}")
    return raw_output_path

def create_dynamic_listing_model(field_names: List[str]) -> Type[BaseModel]:
    field_definitions = {field: (str, ...) for field in field_names}
    return create_model('DynamicListingModel', **field_definitions)

def create_listings_container_model(listing_model: Type[BaseModel]) -> Type[BaseModel]:
    return create_model('DynamicListingsContainer', listings=(List[listing_model], ...))

def gemini_format(data, token_counts, DynamicListingsContainer):
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash',
                                  generation_config={
                                      "response_mime_type": "application/json",
                                      "response_schema": DynamicListingsContainer
                                  })
    prompt = SYSTEM_MESSAGE + "\n" + USER_MESSAGE + data
    input_tokens = model.count_tokens(prompt)
    completion = model.generate_content(prompt)
    usage_metadata = completion.usage_metadata
    token_counts.update({
        "input_tokens": usage_metadata.prompt_token_count,
        "output_tokens": usage_metadata.candidates_token_count
    })
    return completion.text, token_counts

def format_data(data, DynamicListingsContainer, DynamicListingModel, selected_model):
    token_counts = {}
    if selected_model == "gemini-1.5-flash":
        return gemini_format(data, token_counts, DynamicListingsContainer)
    else:
        raise ValueError(f"Model không được hỗ trợ: {selected_model}")

import os
import json
import logging
import pandas as pd

def save_formatted_data(formatted_data, timestamp, output_folder='output'):
    """
    Hàm này lưu dữ liệu đã định dạng dưới dạng JSON và Excel.
    formatted_data: Dữ liệu đã được định dạng từ mô hình AI.
    timestamp: Dấu thời gian để lưu tên file.
    output_folder: Thư mục đầu ra để lưu các file JSON và Excel.
    """
    os.makedirs(output_folder, exist_ok=True)

    # Xử lý formatted_data để đảm bảo nó là JSON hợp lệ
    try:
        if isinstance(formatted_data, str):
            # Nếu formatted_data là chuỗi, kiểm tra xem nó có phải là chuỗi JSON hợp lệ không
            formatted_data_dict = json.loads(formatted_data)
        else:
            # Nếu không, giả định formatted_data là đối tượng Python, cố gắng chuyển nó thành dict nếu cần
            formatted_data_dict = formatted_data.dict() if hasattr(formatted_data, 'dict') else formatted_data
    except json.JSONDecodeError as e:
        logging.error(f"JSONDecodeError: {e}")
        return None  # Trả về None nếu không thể parse JSON

    # Lưu dữ liệu JSON vào file
    json_output_path = os.path.join(output_folder, f'sorted_data_{timestamp}.json')
    try:
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_data_dict, f, indent=4)
        logging.info(f"Dữ liệu đã được lưu dưới dạng JSON tại: {json_output_path}")
    except Exception as e:
        logging.error(f"Lỗi khi lưu JSON: {e}")
        return None

    # Chuyển đổi dữ liệu thành DataFrame và lưu dưới dạng Excel
    try:
        # Giả định dữ liệu chứa trong dict là một danh sách
        df = pd.DataFrame(next(iter(formatted_data_dict.values())) if len(formatted_data_dict) == 1 else formatted_data_dict)
        excel_output_path = os.path.join(output_folder, f'sorted_data_{timestamp}.xlsx')
        df.to_excel(excel_output_path, index=False)
        logging.info(f"Dữ liệu đã lưu dưới dạng Excel tại: {excel_output_path}")
        return df
    except Exception as e:
        logging.error(f"Lỗi khi tạo DataFrame hoặc lưu Excel: {e}")
        return None



def calculate_price(token_counts, model):
    input_token_count = token_counts.get("input_tokens", 0)
    output_token_count = token_counts.get("output_tokens", 0)
    input_cost = input_token_count * PRICING[model]["input"]
    output_cost = output_token_count * PRICING[model]["output"]
    total_cost = input_cost + output_cost
    return input_token_count, output_token_count, total_cost
