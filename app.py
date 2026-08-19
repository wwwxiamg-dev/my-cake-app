import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
from rembg import remove, new_session
import io

# 設定頁面
st.set_page_config(page_title="🍰 蛋糕商品照換背景助理", page_icon="🍰", layout="centered")

st.title("🍰 蛋糕商品照換背景助理")
st.write("上傳你的蛋糕照片，系統會自動去背、換上背景並加上自然陰影！")

# 載入輕量版去背模型 (u2netp 僅 40MB，不會導致伺服器記憶體溢位)
@st.cache_resource
def load_rembg_session():
    return new_session("u2netp")

rembg_session = load_rembg_session()

# 1. 上傳照片
uploaded_file = st.file_uploader("請上傳蛋糕照片 (支援 JPG, PNG)", type=["jpg", "jpeg", "png"])

# 2. 側邊欄控制
st.sidebar.header("🎨 背景與陰影設定")
bg_choice = st.sidebar.selectbox(
    "選擇預設情境背景",
    ["溫馨木紋桌", "高雅大理石", "法式廚房桌", "純白簡約背景"]
)

shadow_blur = st.sidebar.slider("陰影柔和度 (模糊)", 5, 50, 20)
shadow_opacity = st.sidebar.slider("陰影透明度", 30, 200, 100)

# 繪製背景
def generate_background(choice, size):
    w, h = size
    bg = Image.new("RGBA", size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(bg)
    
    if choice == "溫馨木紋桌":
        bg = Image.new("RGBA", size, (210, 160, 110, 255))
        draw = ImageDraw.Draw(bg)
        for y in range(0, h, 25):
            draw.line([(0, y), (w, y)], fill=(180, 130, 80, 255), width=3)
            
    elif choice == "高雅大理石":
        bg = Image.new("RGBA", size, (240, 242, 245, 255))
        draw = ImageDraw.Draw(bg)
        draw.line([(0, int(h*0.3)), (w*0.6, int(h*0.5)), (w, int(h*0.4))], fill=(210, 215, 220, 255), width=4)
        draw.line([(0, int(h*0.7)), (w*0.4, int(h*0.6)), (w, int(h*0.8))], fill=(220, 225, 230, 255), width=3)
        
    elif choice == "法式廚房桌":
        bg = Image.new("RGBA", size, (235, 230, 220, 255))
        draw = ImageDraw.Draw(bg)
        draw.line([(0, int(h*0.75)), (w, int(h*0.75))], fill=(190, 180, 170, 255), width=6)
        
    return bg

# 繪製陰影
def add_ellipse_shadow(background, fg_size, blur_radius, opacity):
    w, h = background.size
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    
    shadow_w = int(fg_size[0] * 0.75)
    shadow_h = int(fg_size[1] * 0.12)
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

# 執行邏輯
if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📸 原始照片")
        st.image(image)
        
    if st.button("開始自動去背 + 合成背景 🚀", type="primary"):
        with st.spinner("正在執行 AI 去背與背景合成..."):
            # 1. 使用 rembg 輕量模型去背
            no_bg_img = remove(image, session=rembg_session).convert("RGBA")
            
            # 2. 生成情境背景
            bg_img = generate_background(bg_choice, no_bg_img.size)
            
            # 3. 繪製底部陰影
            bg_with_shadow = add_ellipse_shadow(bg_img, no_bg_img.size, shadow_blur, shadow_opacity)
            
            # 4. 疊加去背後的蛋糕
            final_result = Image.alpha_composite(bg_with_shadow, no_bg_img)
            
        with col2:
            st.subheader("✨ 換背景成果")
            st.image(final_result)
            
        # 下載區域
        buffered = io.BytesIO()
        final_result.convert("RGB").save(buffered, format="JPEG")
        st.download_button(
            label="⬇️ 下載完成商品照 (JPG)",
            data=buffered.getvalue(),
            file_name="cake_final_design.jpg",
            mime="image/jpeg"
        )
