import os
import streamlit as st
import random
import time
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

current_time = int(time.time())
random.seed = current_time

st.set_page_config(page_title="Gemini Image 影像生成", page_icon="🍌")
st.title("🍌 影像生成")
st.caption("Powered by Gemini 3.1 Flash Image Preview")

api_key = os.getenv("GEMINI_API_KEY")
    
resolutions = {
            "1024x1024": "1K",
            "2048x2048": "2K",
            "4096x4096": "4K",
}
selected_label = st.sidebar.selectbox("🖼️ 解析度", list(resolutions.keys()))
resolution = resolutions[selected_label]

uploade_files = st.sidebar.file_uploader("圖片", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
images = []
if uploade_files:
    images.clear()
    for file in uploade_files:
        image = Image.open(file)
        images.append(image)
        st.sidebar.image(image)

prompt = st.text_area("你想畫什麼？請描述你的畫面：", 
        placeholder="例如：一隻穿著太空裝的橘貓，在火星上喝著珍珠奶茶，賽博龐克風格，高畫質 4k",
        height=100)

if st.button("✨ 生成圖片", type="primary"):
    if not prompt.strip():
        st.warning("請先輸入圖片描述喔！")
    else:
        with st.spinner("Nano Banana 2 正在為您作畫中，請稍候..."):
            try:
                client = genai.Client()
                response = client.models.generate_content(
                    model="gemini-3.1-flash-image-preview",
                    contents=[prompt, images],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
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

                for part in response.parts:
                    if part.text is not None:
                        print(part.text)
                    elif part.inline_data is not None:
                        image = Image.open(BytesIO(part.as_image().image_bytes))
                        if image is not None:
                            st.image(image, caption="生成的圖片")

            except Exception as e:
                st.error(f"發生錯誤：{e}")
                st.info("請確認你的 API Key 是否具有呼叫影像生成模型的權限，或檢查 SDK 是否為最新版本。")
