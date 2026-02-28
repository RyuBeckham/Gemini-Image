import os
import streamlit as st
import random
import time
from google import genai
from google.genai import types
from io import BytesIO
from PIL import Image
from pillow_heif import register_heif_opener
from dotenv import load_dotenv

register_heif_opener()
load_dotenv()

current_time = int(time.time())
random.seed = current_time

st.set_page_config(page_title="Gemini Image 影像生成", page_icon="🍌")
st.title("🍌 影像生成")
st.caption("Powered by Gemini 3.1 Flash Image Preview")

prompt_default = "以圖2的構圖用圖1的人物生成寫實人像照片，比例3:4"

if "image_history" not in st.session_state:
    st.session_state.image_history = []

if "prompt" not in st.session_state:
    st.session_state["prompt"] = prompt_default

def update_text_area():
    if not st.session_state["prompt"].strip():
        st.session_state["prompt"] = prompt_default

api_key = os.getenv("GEMINI_API_KEY")
    
resolutions = {
            "1024x1024": "1K",
            "2048x2048": "2K",
            "4096x4096": "4K",
}
selected_label = st.sidebar.selectbox("🖼️ 解析度", list(resolutions.keys()))
resolution = resolutions[selected_label]

uploade_files = st.sidebar.file_uploader("圖片", type=["jpg", "jpeg", "png", "webp", "heic", "heif"], accept_multiple_files=True)
images = None

if uploade_files:
    images = []
    for file in uploade_files:
        image = Image.open(file)
        images.append(image)
        st.sidebar.image(image)
else:
    images = None

st.text_area("你想畫什麼？請描述你的畫面：", 
            height=100, key="prompt")

if st.button("✨ 生成圖片", type="primary", on_click=update_text_area):
    with st.spinner("正在為您作畫中，請稍候..."):
        try:
            client = genai.Client()
            contents = [st.session_state["prompt"]]
            if images is not None:
                contents.append(images)
            response = client.models.generate_content(
                model="gemini-3.1-flash-image-preview",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    seed=random.randint(0, 2147483647),
                    image_config=types.ImageConfig(
                        image_size=resolution,
                    ),
                    tools=[
                        types.Tool(google_search=types.GoogleSearch(
                            search_types=types.SearchTypes(
                                web_search=types.WebSearch(),
                                image_search=types.ImageSearch()
                            )
                        ))
                    ],
                )
            )

            if response.parts is not None:
                for part in response.parts:
                    if part.text is not None:
                        print(part.text)
                    elif part.inline_data is not None:
                        image = Image.open(BytesIO(part.as_image().image_bytes))
                        st.session_state.image_history.insert(0, image)
            else:
                st.error(f"生成失敗：{response.text}")

        except Exception as e:
            st.error(f"發生錯誤：{e}")
            st.info("請確認你的 API Key 是否具有呼叫影像生成模型的權限，或檢查 SDK 是否為最新版本。")

st.divider()
st.subheader("📚 你的創作畫廊 (歷史紀錄)")

if st.session_state.image_history:
    if st.button("🗑️ 清空歷史紀錄"):
        st.session_state.image_history = []
        st.rerun()

if st.session_state.image_history:
    for image in st.session_state.image_history:
        st.image(image)
else:
    st.info("目前還沒有生成的圖片喔！趕快在上方輸入指令召喚第一張圖片吧。")
