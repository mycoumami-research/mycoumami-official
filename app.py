
import streamlit as st
import requests
import json
import base64
import hmac
import re
import io
import html
from pathlib import Path
from PIL import Image

# =============================================
# 1. CAU HINH WEBSITE
# =============================================

st.set_page_config(
    page_title="MYCOUMAMI | Tinh hoa Umami Da Lat",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

ROOT = Path(__file__).parent

# =============================================
# 2. GIAO DIEN THUONG HIEU
# =============================================

st.markdown("""
<style>

.stApp {
    background: #FAFBF7;
    color: #173D2B;
}

[data-testid="stHeader"] {
    background: #FAFBF7;
}

.block-container {
    max-width: 1350px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    color: #174632;
    font-weight: 700;
}

.brand-bar {
    background: #123E2E;
    color: #FFFFFF;
    text-align: center;
    padding: 14px;
    border-radius: 8px;
    font-size: 13px;
    letter-spacing: 2px;
    margin-bottom: 22px;
}

.hero {
    background: linear-gradient(
        135deg, #102F23, #286348
    );
    color: white;
    padding: 45px 35px;
    border-radius: 20px;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: clamp(32px, 5vw, 60px);
    color: #FFFFFF;
    letter-spacing: 1px;
    line-height: 1.2;
}

.hero h2 {
    color: #DEE8CA;
    font-size: 23px;
}

.hero p {
    font-size: 17px;
    line-height: 1.8;
    color: #F2F6EC;
}

.eyebrow {
    color: #BAD2A7;
    letter-spacing: 4px;
    font-size: 12px;
    font-weight: 600;
}

.section-card {
    background: #FFFFFF;
    padding: 25px;
    border: 1px solid #E1E9DF;
    border-radius: 16px;
    min-height: 170px;
    box-shadow: 0 5px 20px #163D2810;
    margin-bottom: 15px;
}

.section-card h3 {
    color: #174632;
}

.section-card p {
    color: #425D4C;
    line-height: 1.7;
}

.process-card {
    background: #EDF3E9;
    border-radius: 14px;
    padding: 22px;
    text-align: center;
    min-height: 210px;
    margin-bottom: 12px;
}

.process-number {
    font-size: 34px;
    font-weight: bold;
    color: #5F8865;
}

.order-button {
    display: inline-block;
    background: #174632;
    color: white !important;
    text-decoration: none !important;
    padding: 16px 28px;
    border-radius: 40px;
    font-size: 18px;
    font-weight: bold;
    margin: 10px 0;
}

.order-button:hover {
    background: #397653;
}

.footer {
    background: #123E2E;
    color: #FFFFFF;
    padding: 35px 20px;
    border-radius: 16px;
    text-align: center;
    margin-top: 30px;
}

.footer h2 {
    color: #FFFFFF;
}

.stButton > button {
    border-radius: 25px;
    border: 1px solid #174632;
    color: #174632;
    font-weight: 600;
}

[data-testid="stImage"] img {
    border-radius: 12px;
}

[data-testid="stSidebar"] {
    background: #EAF1E7;
}

html, body {
    font-family: "Segoe UI", sans-serif;
}

@media(max-width: 700px) {
    .hero {
        padding: 25px 20px;
    }
    .brand-bar {
        letter-spacing: 1px;
        font-size: 11px;
    }
}

</style>
""", unsafe_allow_html=True)

# =============================================
# 3. BAO MAT VA KET NOI GITHUB
# =============================================

def secret(name):
    try:
        return str(st.secrets[name])
    except Exception:
        return ""

REPO = secret("GITHUB_REPO")
TOKEN = secret("GITHUB_TOKEN")
PASSWORD = secret("ADMIN_PASSWORD")
BRANCH = "main"

REMOTE = bool(REPO and TOKEN)

if "admin" not in st.session_state:
    st.session_state.admin = False

def github_headers(raw=False):

    return {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": (
            "application/vnd.github.raw+json"
            if raw else
            "application/vnd.github+json"
        ),
        "X-GitHub-Api-Version": "2022-11-28"
    }

def github_url(filename):

    return (
        "https://api.github.com/repos/"
        f"{REPO}/contents/{filename}"
    )

ALLOWED_FILES = {
    "content.json",
    "product.png",
    "ingredients.png",
    "logo.png",
    "banner.png",
    "poster.pdf",
    "team.png",
    "video.mp4"
}
ALLOWED_FILES.update({
    "advisor.png",
    "hieu.png",
    "tram.png",
    "tam.png",
    "huyen.png"
})
@st.cache_data(ttl=60, max_entries=24)
def load_file(filename):

    if filename not in ALLOWED_FILES:
        return None

    if REMOTE:

        result = requests.get(
            github_url(filename),
            headers=github_headers(raw=True),
            params={"ref": BRANCH},
            timeout=30
        )

        if result.status_code == 200:
            return result.content

        if result.status_code == 404:
            return None

        raise RuntimeError(
            "Khong doc duoc du lieu GitHub."
        )

    path = ROOT / filename

    if path.exists():
        return path.read_bytes()

    return None

def get_file(filename):

    try:
        return load_file(filename)
    except Exception:
        st.warning(
            "Tạm thời không tải được "
            + filename
        )
        return None

def save_file(filename, content):

    # Kiem tra quyen tren may chu
    if not st.session_state.admin:
        raise PermissionError(
            "Khong co quyen Admin."
        )

    if not REMOTE:
        raise RuntimeError(
            "Chua cau hinh GitHub Secrets."
        )

    if filename not in ALLOWED_FILES:
        raise ValueError("File khong hop le.")

    if len(content) > 20 * 1024 * 1024:
        raise ValueError("File qua lon.")

    url = github_url(filename)

    current = requests.get(
        url,
        headers=github_headers(),
        params={"ref": BRANCH},
        timeout=30
    )

    payload = {
        "message": f"Admin update {filename}",
        "content": base64.b64encode(
            content
        ).decode("ascii"),
        "branch": BRANCH
    }

    if current.status_code == 200:

        payload["sha"] = current.json()["sha"]

    elif current.status_code != 404:

        raise RuntimeError(
            "Khong doc duoc file GitHub."
        )

    result = requests.put(
        url,
        headers=github_headers(),
        json=payload,
        timeout=90
    )

    if result.status_code not in (200, 201):

        raise RuntimeError(
            "GitHub tu choi cap nhat. "
            "Kiem tra token va quyen Contents."
        )

    load_file.clear()

# =============================================
# 4. NOI DUNG MAC DINH
# =============================================

DEFAULT = {

    "headline":
        "Tinh hoa vị Umami Đà Lạt",

    "slogan":
        "Từ nông sản Đà Lạt - "
        "Nâng tầm giá trị Việt",

    "description":
        "MYCOUMAMI là dự án phát triển "
        "hạt nêm nấm – rau củ từ gốc "
        "nấm kim châm và nông sản ngoài "
        "chuẩn thương mại Đà Lạt, "
        "ứng dụng công nghệ enzyme "
        "để nâng cao giá trị nguyên liệu.",

    "phone": "",

    "price": "Liên hệ",

    "advisor": "ThS. Thi Đình Nguyên",

    "members":
        "Hoàng Trọng Hiếu – Đại diện nhóm",

    "video_url": "",

    "order_open": False

}

def read_content():

    settings = DEFAULT.copy()

    saved = get_file("content.json")

    if saved:

        try:

            loaded = json.loads(
                saved.decode("utf-8")
            )

            settings.update(loaded)

        except Exception:

            st.warning(
                "Không đọc được nội dung đã lưu."
            )

    return settings

settings = read_content()

def safe(value):
    return html.escape(str(value))

# =============================================
# 5. HAM HIEN THI HINH ANH
# =============================================

def show_image(filename, caption=None):

    data = get_file(filename)

    if data:

        st.image(
            data,
            caption=caption,
            width="stretch"
        )

        return True

    return False
# GIAO DIEN MYCOUMAMI SCIENCE & NATURE

if st.query_params.get("admin") != "1":

    from showcase import render_showcase

    render_showcase(settings, get_file)

    st.stop()
# =============================================
# 6. HEADER VA MENU
# =============================================

st.markdown("""
<div class="brand-bar">
FOOD INNOVATION & DEVELOPMENT 2026
&nbsp; • &nbsp; DALAT, VIETNAM
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1, 1])

with left:

    st.markdown(
        "## MYCOUMAMI"
    )

    st.caption(
        "MUSHROOM & VEGETABLE SEASONING"
    )

with right:

    logo = get_file("logo.png")

    if logo:
        st.image(logo, width=340)
    else:
        st.markdown(
            "### YERSIN UNIVERSITY"
        )

menu = st.radio(
    "Điều hướng",
    [
        "Trang chủ",
        "Sản phẩm",
        "Quy trình sản xuất",
        "Nghiên cứu",
        "Đội ngũ",
        "Đặt hàng",
        "Admin"
    ],
    horizontal=True, index=6,
    label_visibility="collapsed"
)

st.divider()

# =============================================
# 7. HAM LIEN HE DAT HANG
# =============================================

def order_contact():

    phone = re.sub(
        r"[\s().-]", "",
        str(settings["phone"])
    )

    valid = re.fullmatch(
        r"\+?[0-9]{9,15}", phone
    )

    if settings["order_open"] and valid:

        st.markdown(
            f"""
            <a class="order-button"
            href="tel:{phone}">
            ☎ Gọi đặt hàng: {safe(phone)}
            </a>
            """,
            unsafe_allow_html=True
        )

    elif valid:

        st.info(
            "Liên hệ tìm hiểu sản phẩm: "
            + phone
        )

    else:

        st.info(
            "Thông tin liên hệ đang được cập nhật."
        )

# =============================================
# 8. TRANG CHU
# =============================================

if menu == "Trang chủ":

    show_image("banner.png")

    a, b = st.columns([1, 1.2])

    with a:

        st.markdown(
            f"""
            <div class="hero">
            <div class="eyebrow">
            INSPIRED BY DA LAT
            </div>

            <h1>MYCOUMAMI</h1>

            <h2>
            {safe(settings["headline"])}
            </h2>

            <p>
            {safe(settings["description"])}
            </p>

            <p>
            <b>
            {safe(settings["slogan"])}
            </b>
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        order_contact()

    with b:

        if not show_image("product.png"):

            st.info(
                "Hình ảnh sản phẩm "
                "đang được cập nhật."
            )

    st.divider()

    st.caption("OUR STORY")

    st.title(
        "Một hành trình nâng tầm nông sản"
    )

    a, b = st.columns(2)

    with a:

        show_image("ingredients.png")

    with b:

        st.markdown("""
        ### Không dừng lại ở hình thức

        Tại Đà Lạt, nhiều dòng nông sản
        bị giảm giá trị thương mại do
        kích thước hoặc hình dáng.

        MYCOUMAMI hướng đến tận dụng
        phần nguyên liệu còn phù hợp
        cho chế biến thực phẩm, kết hợp
        với công nghệ enzyme để phát
        triển nền gia vị mới.

        ### Từ nông nghiệp đến khoa học

        Kết nối người sản xuất, nhà nghiên
        cứu và người tiêu dùng thông qua
        một chuỗi giá trị có trách nhiệm.
        """)

    st.divider()

    st.title("Giá trị MYCOUMAMI")

    values = [
        (
            "🌱",
            "Nguồn nguyên liệu địa phương",
            "Khai thác giá trị từ nông sản "
            "và dòng nguyên liệu thứ cấp."
        ),
        (
            "🧪",
            "Công nghệ enzyme",
            "Phát triển nền gia vị dựa "
            "trên nghiên cứu thực nghiệm."
        ),
        (
            "🌏",
            "Định hướng bền vững",
            "Hướng đến nâng cao hiệu suất "
            "sử dụng nguyên liệu."
        )
    ]

    cols = st.columns(3)

    for col, item in zip(cols, values):

        with col:

            st.markdown(
                f"""
                <div class="section-card">
                <h1>{item[0]}</h1>
                <h3>{item[1]}</h3>
                <p>{item[2]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.caption(
        "Dự án phát triển sản phẩm "
        "thuộc FID 2026."
    )

# =============================================
# 9. TRANG SAN PHAM
# =============================================

elif menu == "Sản phẩm":

    st.caption("MYCOUMAMI COLLECTION")

    st.title("Hạt nêm nấm – rau củ")

    a, b = st.columns([1.3, 1])

    with a:

        show_image(
            "product.png",
            "Thiết kế bao bì MYCOUMAMI"
        )

    with b:

        st.subheader(
            "Tinh hoa vị Umami Đà Lạt"
        )

        st.write(settings["description"])

        st.markdown(
            "**Quy cách bao bì thiết kế:** 100 g"
        )

        st.markdown(
            "**Giá tham khảo:** "
            + str(settings["price"])
        )

        if settings["order_open"]:
            st.success("Đã mở liên hệ đặt hàng")
        else:
            st.info(
                "Sản phẩm đang được phát triển."
            )

        order_contact()

    st.divider()

    st.title("Ba dòng nguyên liệu")

    show_image("ingredients.png")

    items = [
        (
            "🍄 Nấm kim châm",
            "Nguồn amino acid, nucleotide "
            "và nền hương vị nấm."
        ),
        (
            "🍅 Cà chua",
            "Bổ sung nền vị, độ chua "
            "và màu sắc."
        ),
        (
            "🥔 Khoai tây",
            "Khảo sát khả năng tạo độ "
            "đầy vị và cấu trúc."
        )
    ]

    for col, item in zip(st.columns(3), items):

        with col:

            st.markdown(
                f"""
                <div class="section-card">
                <h3>{item[0]}</h3>
                <p>{item[1]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.subheader("Định hướng ứng dụng")

    st.write(
        "Canh • Súp • Món xào • Nước sốt "
        "• Nền gia vị chế biến"
    )

    st.caption(
        "Công thức, liều sử dụng và "
        "thời hạn bảo quản cần được "
        "xác nhận trước thương mại hóa."
    )

# =============================================
# 10. QUY TRINH SAN XUAT
# =============================================

elif menu == "Quy trình sản xuất":

    st.caption("FROM FARM TO PRODUCT")

    st.title(
        "Hành trình tạo nên MYCOUMAMI"
    )

    st.write(
        "Quy trình định hướng phát triển "
        "hạt nêm từ nông sản Đà Lạt."
    )

    steps = [
        (
            "🌱",
            "Thu gom nguyên liệu",
            "Tiếp nhận nguyên liệu phù hợp "
            "cho chế biến thực phẩm."
        ),
        (
            "💧",
            "Sơ chế và chuẩn bị",
            "Phân loại, làm sạch và "
            "chuẩn bị nguyên liệu."
        ),
        (
            "🧪",
            "Xử lý enzyme",
            "Thủy phân gốc nấm bằng papain; "
            "khảo sát xử lý cà chua "
            "bằng pectinase."
        ),
        (
            "⚗️",
            "Lọc và cô đặc",
            "Thu hồi dịch xử lý, "
            "chuẩn bị phối trộn."
        ),
        (
            "⚙️",
            "Sấy - nghiền - rây",
            "Định hướng tạo nền gia vị "
            "dạng bột hoặc hạt."
        ),
        (
            "📦",
            "Đánh giá sản phẩm",
            "Kiểm tra cảm quan, chất lượng "
            "và hoàn thiện bao bì."
        )
    ]

    for start in range(0, 6, 3):

        cols = st.columns(3)

        for i, col in enumerate(cols):

            index = start + i
            step = steps[index]

            with col:

                st.markdown(
                    f"""
                    <div class="process-card">
                    <div class="process-number">
                    {index+1:02d}
                    </div>

                    <h2>{step[0]}</h2>
                    <h3>{step[1]}</h3>
                    <p>{step[2]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.divider()

    st.subheader(
        "Công nghệ theo ba nhánh nguyên liệu"
    )

    a, b, c = st.columns(3)

    with a:

        st.success(
            "NHÁNH A\n\n"
            "Gốc nấm kim châm → Papain "
            "→ Dịch thủy phân."
        )

    with b:

        st.info(
            "NHÁNH B\n\n"
            "Cà chua → Pectinase "
            "→ Thu hồi pha dịch."
        )

    with c:

        st.info(
            "NHÁNH C\n\n"
            "Khoai tây → Làm chín "
            "→ Khảo sát phối trộn."
        )

    st.caption(
        "Nhánh A đã có dữ liệu nghiên cứu. "
        "Các nhánh còn lại và công thức "
        "cuối cần kiểm chứng thêm."
    )

    show_image(
        "product.png",
        "Định hướng sản phẩm MYCOUMAMI"
    )

# =============================================
# 11. TRANG NGHIEN CUU VA POSTER
# =============================================

elif menu == "Nghiên cứu":

    st.caption("SCIENCE & INNOVATION")

    st.title(
        "Khoa học phía sau MYCOUMAMI"
    )

    a, b, c = st.columns(3)

    a.metric("Nghiệm thức thủy phân", "17")
    b.metric("Yếu tố khảo sát", "3")
    c.metric("R² theo báo cáo", "0.9588")

    st.markdown("""
    ### Nghiên cứu công nghệ enzyme

    Dự án khảo sát ảnh hưởng của hoạt độ
    papain, thời gian và nhiệt độ đến
    đáp ứng ninhydrin A570 của dịch
    thủy phân gốc nấm kim châm.

    Thiết kế Box-Behnken mở rộng và
    phương pháp bề mặt đáp ứng được
    sử dụng để khảo sát vùng điều
    kiện thuận lợi.
    """)

    st.caption(
        "Glu-eq là giá trị quy đổi theo "
        "chuẩn MSG, không phải phép đo "
        "L-glutamate đặc hiệu."
    )

    st.divider()

    st.subheader("Poster nghiên cứu FID 2026")

    poster = get_file("poster.pdf")

    if poster:

        st.info(
            "Poster là tài liệu của nhóm. "
            "Các chỉ tiêu và điều kiện tối ưu "
            "cần đối chiếu với báo cáo toàn văn."
        )

        st.pdf(poster, height=850)

        st.download_button(
            "Tải poster PDF",
            data=poster,
            file_name="MYCOUMAMI_Poster.pdf",
            mime="application/pdf"
        )

    else:

        st.info(
            "Poster đang được cập nhật."
        )

# =============================================
# 12. TRANG DOI NGU
# =============================================

elif menu == "Đội ngũ":

    st.caption("MEET OUR TEAM")

    st.title("Những người tạo nên MYCOUMAMI")

    if not show_image(
        "team.png",
        "Đội ngũ nghiên cứu MYCOUMAMI"
    ):

        st.info(
            "Hình ảnh nhóm đang được cập nhật."
        )

    st.divider()

    st.subheader("Giảng viên hướng dẫn")

    st.markdown(
        "### " + str(settings["advisor"])
    )

    st.caption(
        "Trường Đại học Yersin Đà Lạt"
    )

    st.divider()

    st.subheader("Thành viên nhóm")

    members = [
        m.strip()
        for m in str(
            settings["members"]
        ).splitlines()
        if m.strip()
    ]

    for start in range(0, len(members), 3):

        cols = st.columns(3)

        for col, member in zip(
            cols, members[start:start+3]
        ):

            with col:

                st.markdown(
                    f"""
                    <div class="section-card">
                    <h1>👤</h1>
                    <h3>{safe(member)}</h3>
                    <p>MYCOUMAMI TEAM</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.divider()

    st.subheader("Video giới thiệu nhóm")

    video = get_file("video.mp4")

    if video:

        st.video(
            video,
            format="video/mp4"
        )

    elif str(
        settings["video_url"]
    ).startswith((
        "https://www.youtube.com/",
        "https://youtu.be/"
    )):

        st.video(settings["video_url"])

    else:

        st.info(
            "Video giới thiệu "
            "đang được cập nhật."
        )

    st.markdown("""
    **MYCOUMAMI TEAM**

    Trường Đại học Yersin Đà Lạt

    Food Innovation and Development 2026
    """)

# =============================================
# 13. TRANG DAT HANG
# =============================================

elif menu == "Đặt hàng":

    st.caption("CONNECT WITH MYCOUMAMI")

    st.title("Liên hệ đặt hàng")

    a, b = st.columns(2)

    with a:

        show_image("product.png")

    with b:

        st.subheader(
            "MYCOUMAMI - Hạt nêm nấm, rau củ"
        )

        st.write(
            "Quy cách bao bì thiết kế: 100 g"
        )

        st.metric(
            "Giá tham khảo",
            str(settings["price"])
        )

        if settings["order_open"]:

            qty = st.number_input(
                "Số lượng dự kiến",
                min_value=1,
                max_value=1000,
                value=1
            )

            st.code(
                "Xin chào MYCOUMAMI! "
                f"Tôi muốn đặt {qty} gói "
                "hạt nêm 100 g. "
                "Vui lòng tư vấn giúp tôi.",
                language="text"
            )

        else:

            st.info(
                "Hiện chưa mở đặt hàng. "
                "Bạn có thể liên hệ tìm hiểu "
                "hoặc hợp tác phát triển sản phẩm."
            )

        order_contact()

        st.caption(
            "Đơn hàng được trao đổi và "
            "xác nhận trực tiếp qua điện thoại. "
            "Website không thu tiền "
            "hay tự động gửi đơn hàng."
        )

# =============================================
# 14. KHU VUC ADMIN
# =============================================

elif menu == "Admin":

    st.title("MYCOUMAMI ADMIN CENTER")

    st.caption(
        "Khu vực quản trị dành riêng "
        "cho chủ sở hữu website."
    )

    if len(PASSWORD) < 16 or not REMOTE:
        st.write("Mat khau hop le:", len(PASSWORD) >= 16)
        st.write("Co GitHub Token:", bool(TOKEN))
        st.write("Co GitHub Repo:", bool(REPO))
        st.warning(
            "Chức năng Admin chưa được cấu hình. "
            "Cần thêm GitHub token và mật khẩu "
            "trong Streamlit Secrets."
        )

    elif not st.session_state.admin:

        with st.form(
            "admin_login",
            clear_on_submit=True
        ):

            password = st.text_input(
                "Mật khẩu quản trị",
                type="password"
            )

            login = st.form_submit_button(
                "Đăng nhập Admin"
            )

        if login:

            if hmac.compare_digest(
                password.encode("utf-8"),
                PASSWORD.encode("utf-8")
            ):

                st.session_state.admin = True
                st.rerun()

            else:

                st.error(
                    "Mật khẩu không chính xác."
                )

    else:

        st.success(
            "Đã đăng nhập quyền quản trị."
        )

        if st.button("Đăng xuất"):

            st.session_state.admin = False
            st.rerun()

        tab1, tab2 = st.tabs([
            "Chỉnh sửa nội dung",
            "Quản lý hình ảnh và video"
        ])

        # CHINH SUA NOI DUNG

        with tab1:

            with st.form("edit_content"):

                headline = st.text_input(
                    "Tiêu đề thương hiệu",
                    value=settings["headline"]
                )

                slogan = st.text_input(
                    "Slogan",
                    value=settings["slogan"]
                )

                description = st.text_area(
                    "Nội dung giới thiệu",
                    value=settings["description"],
                    height=180
                )

                phone = st.text_input(
                    "Số điện thoại đặt hàng",
                    value=settings["phone"]
                )

                price = st.text_input(
                    "Giá sản phẩm",
                    value=settings["price"]
                )

                advisor = st.text_input(
                    "Giảng viên hướng dẫn",
                    value=settings["advisor"]
                )

                members = st.text_area(
                    "Danh sách thành viên "
                    "(mỗi người một dòng)",
                    value=settings["members"],
                    height=180
                )

                video_url = st.text_input(
                    "Link YouTube giới thiệu",
                    value=settings["video_url"]
                )

                order_open = st.checkbox(
                    "Mở chức năng đặt hàng",
                    value=settings["order_open"]
                )

                confirm = st.form_submit_button(
                    "Lưu thay đổi website"
                )

            if confirm:

                clean_phone = re.sub(
                    r"[\s().-]", "", phone
                )

                if order_open and not re.fullmatch(
                    r"\+?[0-9]{9,15}",
                    clean_phone
                ):

                    st.error(
                        "Cần nhập số điện thoại hợp lệ."
                    )

                else:

                    new_content = {

                        "headline": headline,
                        "slogan": slogan,
                        "description": description,
                        "phone": phone,
                        "price": price,
                        "advisor": advisor,
                        "members": members,
                        "video_url": video_url,
                        "order_open": order_open
                    }

                    try:

                        save_file(
                            "content.json",
                            json.dumps(
                                new_content,
                                ensure_ascii=False,
                                indent=2
                            ).encode("utf-8")
                        )

                        st.success(
                            "Đã lưu nội dung lên GitHub."
                        )

                    except Exception:

                        st.error(
                            "Không lưu được. "
                            "Kiểm tra GitHub token."
                        )

        # QUAN LY MEDIA

        with tab2:

            st.subheader(
                "Tải nội dung mới lên website"
            )

            media_types = {

                "Banner ngang":
                    ("banner.png", ["png","jpg","jpeg"]),

                "Ảnh sản phẩm":
                    ("product.png", ["png","jpg","jpeg"]),

                "Ảnh nguyên liệu":
                    ("ingredients.png", ["png","jpg","jpeg"]),

                "Logo trường":
                    ("logo.png", ["png","jpg","jpeg"]),

                "Ảnh nhóm":
                    ("team.png", ["png","jpg","jpeg"]),

                "Poster PDF":
                    ("poster.pdf", ["pdf"]),

                "Video giới thiệu":
                    ("video.mp4", ["mp4"])
            }
            media_types.update({

                "Ảnh GVHD - ThS. Thi Đình Nguyên":
                    ("advisor.png", ["png", "jpg", "jpeg"]),

                "Ảnh Hoàng Trọng Hiếu":
                    ("hieu.png", ["png", "jpg", "jpeg"]),

                "Ảnh Lê Quỳnh Trâm":
                    ("tram.png", ["png", "jpg", "jpeg"]),

                "Ảnh Trương Thị Ngọc Tâm":
                    ("tam.png", ["png", "jpg", "jpeg"]),

                "Ảnh Trần Lê Ngọc Huyền":
                    ("huyen.png", ["png", "jpg", "jpeg"])

            })
            choice = st.selectbox(
                "Chọn nội dung cần thay đổi",
                list(media_types.keys())
            )

            filename, extensions = (
                media_types[choice]
            )

            uploaded = st.file_uploader(
                "Chọn file mới",
                type=extensions,
                key="upload_" + filename
            )

            st.caption(
                "Giới hạn 20 MB mỗi file. "
                "Video dài nên sử dụng YouTube."
            )

            if uploaded is not None:

                content = uploaded.getvalue()

                if filename.endswith(".png"):

                    try:

                        image = Image.open(
                            io.BytesIO(content)
                        )

                        image.thumbnail(
                            (2400, 2400)
                        )

                        buffer = io.BytesIO()

                        image.convert("RGBA").save(
                            buffer, format="PNG"
                        )

                        content = buffer.getvalue()

                        st.image(
                            content,
                            width="stretch"
                        )

                    except Exception:

                        st.error(
                            "Ảnh không hợp lệ."
                        )

                        content = None

                elif filename.endswith(".pdf"):

                    if not content.startswith(b"%PDF"):

                        st.error(
                            "File PDF không hợp lệ."
                        )

                        content = None

                if content:

                    if st.button(
                        "Xác nhận cập nhật "
                        + choice
                    ):

                        try:

                            save_file(
                                filename, content
                            )

                            st.success(
                                "Đã cập nhật "
                                + choice
                                + " lên GitHub."
                            )

                        except Exception:

                            st.error(
                                "Cập nhật thất bại. "
                                "Kiểm tra dung lượng "
                                "và quyền GitHub."
                            )

# =============================================
# 15. FOOTER
# =============================================

st.markdown("""
<div class="footer">

<h2>MYCOUMAMI</h2>

<p>
Tinh hoa vị Umami Đà Lạt
</p>

<p>
Từ nông sản Đà Lạt -
Nâng tầm giá trị Việt
</p>

<hr style="border-color:#507461">

<p>
TRƯỜNG ĐẠI HỌC YERSIN ĐÀ LẠT
</p>

<p>
FOOD INNOVATION AND DEVELOPMENT 2026
</p>

<p style="font-size:12px;color:#C6D8C6">
© 2026 MYCOUMAMI TEAM
</p>

</div>
""", unsafe_allow_html=True)
