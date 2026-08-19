import streamlit as st
from PIL import Image
from rembg import remove
import io

# 設定網頁標題與排版
st.set_page_config(page_title="蛋糕攝影去背助理", page_icon="🍰", layout="centered")

st.title("🍰 蛋糕攝影去背助理")
st.write("上傳你的蛋糕或甜點照片，系統會自動去除背景，讓你輕鬆完成商品去背！")

# 檔案上傳區
uploaded_file = st.file_uploader("請選擇要上傳的照片 (支援 JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 顯示原圖
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("原始照片")
        st.image(image, use_column_width=True)
    
    # 點擊按鈕開始去背
    if st.button("開始一鍵去背 🚀", type="primary"):
        with st.spinner("正在努力去背中，請稍候..."):
            # 轉換圖片並進行去背
            input_image = image.convert("RGB")
            output_image = remove(input_image)
            
        with col2:
            st.subheader("去背成果")
            st.image(output_image, use_column_width=True)
            
        # 準備下載按鈕
        buffered = io.BytesIO()
        output_image.save(buffered, format="PNG")
        byte_im = buffered.getvalue()
        
        st.download_button(
            label="下載去背後的透明圖檔 (PNG)",
            data=byte_im,
            file_name="cake_removed_bg.png",
            mime="image/png"
        )
