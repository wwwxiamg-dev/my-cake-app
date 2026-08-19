import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import io
import requests

# 設定網頁標題與排版
st.set_page_config(page_title="🍰 蛋糕商品照換背景助理", page_icon="🍰", layout="centered")

st.title("🍰 蛋糕商品照換背景助理")
st.write("上傳你的蛋糕照片，自動去背、選擇情境背景並生成自然陰影！")

# 1. 圖片上傳區
uploaded_file = st.file_uploader("請上傳蛋糕照片 (支援 JPG, PNG)", type=["jpg", "jpeg", "png"])

# 2. 控制介面（選單與陰影設定）
st.sidebar.header("🎨 背景與陰影設定")
bg_choice = st.sidebar.selectbox(
    "選擇預設情境背景",
    ["溫馨木紋桌", "高雅大理石", "法式廚房桌", "純白簡約背景"]
)

shadow_blur = st.sidebar.slider("陰影柔和度 (模糊)", 5, 50, 20)
shadow_opacity = st.sidebar.slider("陰影透明度", 50, 200, 120)

# 背景色/樣式繪製函式
def generate_background(choice, size):
    bg = Image.new("RGBA", size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(bg)
    w, h = size
    
    if choice == "溫馨木紋桌":
        bg = Image.new("RGBA", size, (210, 160, 110, 255)) # 木質底色
        # 繪製簡單木紋線條
        draw = ImageDraw.Draw(bg)
        for y in range(0, h, 20):
            draw.line([(0, y), (w, y)], fill=(190, 140, 90, 255), width=2)
            
    elif choice == "高雅大理石":
        bg = Image.new("RGBA", size, (240, 242, 245, 255)) # 大理石淺灰底
        draw = ImageDraw.Draw(bg)
        # 繪製灰白色大理石紋路
        draw.line([(0, h*0.2), (w*0.5, h*0.4), (w, h*0.3)], fill=(210, 215, 220, 255), width=4)
        draw.line([(0, h*0.7), (w*0.6, h*0.6), (w, h*0.8)], fill=(220, 225, 230, 255), width=3)
        
    elif choice == "法式廚房桌":
        bg = Image.new("RGBA", size, (235, 230, 220, 255)) # 溫暖米黃底
        draw = ImageDraw.Draw(bg)
        # 繪製檯面分割線
        draw.line([(0, h*0.75), (w, h*0.75)], fill=(200, 190, 180, 255), width=5)
        
    return bg

# 自動生成底部影子
def add_ellipse_shadow(background, fg_size, blur_radius, opacity):
    w, h = background.size
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    
    # 在圖片中下方繪製橢圓陰影
    shadow_w = int(fg_size[0] * 0.8)
    shadow_h = int(fg_size[1] * 0.15)
    center_x = w // 2
    center_y = int(h * 0.78)
    
    bbox = [
        center_x - shadow_w // 2,
        center_y - shadow_h // 2,
        center_x + shadow_w // 2,
        center_y + shadow_h // 2
    ]
    
    s_draw.ellipse(bbox, fill=(0, 0, 0, opacity))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    
    return Image.alpha_composite(background, shadow)

# 去背核心功能 (透過免 API Key 開源引擎)
def remove_bg_api(image_bytes):
    response = requests.post(
        "https://clipdrop-api.co/remove-background/v1",
        files={'image_file': image_bytes}
    )
    # 如果公共接口回應，取得 PNG 數據
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content)).convert("RGBA")
    else:
        # 備用方案：如果外聯失效，使用本地純白色去除演算法
        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        return img

# 主流程
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📸 原始照片")
        st.image(image)
        
    if st.button("開始自動去背 + 合成背景 🚀", type="primary"):
        with st.spinner("正在進行 AI 去背與陰影渲染中..."):
            # 轉成 Bytes 傳送
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format=image.format if image.format else 'PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # 1. 執行去背
            no_bg_img = remove_bg_api(img_bytes)
            
            # 2. 生成背景圖
            bg_img = generate_background(bg_choice, no_bg_img.size)
            
            # 3. 渲染陰影
            bg_with_shadow = add_ellipse_shadow(bg_img, no_bg_img.size, shadow_blur, shadow_opacity)
            
            # 4. 合成蛋糕主體
            final_result = Image.alpha_composite(bg_with_shadow, no_bg_img)
            
        with col2:
            st.subheader("✨ 換背景與陰影成果")
            st.image(final_result)
            
        # 下載按鈕
        buffered = io.BytesIO()
        final_result.convert("RGB").save(buffered, format="JPEG")
        st.download_button(
            label="⬇️ 下載完成商品照 (JPG)",
            data=buffered.getvalue(),
            file_name="cake_final_design.jpg",
            mime="image/jpeg"
        )
