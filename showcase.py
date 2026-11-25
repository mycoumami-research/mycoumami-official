
import streamlit as st
import base64
import html
import re
import io
from PIL import Image, ImageOps


def render_showcase(settings, get_file):

    def esc(value):
        return html.escape(str(value), quote=True)

    def image_uri(filename):
        data = get_file(filename)

        if not data:
            return ""

        try:
            image = Image.open(io.BytesIO(data))
            image = ImageOps.exif_transpose(image)
            image.thumbnail((1800, 1800))

            output = io.BytesIO()

            if filename in ["logo.png", "ingredients.png"]:
                image.convert("RGBA").save(
                    output, format="PNG"
                )
                mime = "image/png"
            else:
                image.convert("RGB").save(
                    output,
                    format="JPEG",
                    quality=88
                )
                mime = "image/jpeg"

            encoded = base64.b64encode(
                output.getvalue()
            ).decode("ascii")

            return f"data:{mime};base64,{encoded}"

        except Exception:
            return ""

    def picture(filename, alt, css=""):

        uri = image_uri(filename)

        if uri:
            return (
                f'<img src="{uri}" '
                f'alt="{esc(alt)}" '
                f'class="{css}">'
            )

        return f"""
        <div class="myco-placeholder">
            {esc(alt)} - Đang cập nhật
        </div>
        """

    headline = esc(settings.get(
        "headline",
        "Tinh hoa vị Umami Đà Lạt"
    ))

    slogan = esc(settings.get(
        "slogan",
        "Từ nông sản Đà Lạt - Nâng tầm giá trị Việt"
    ))

    description = esc(settings.get(
        "description",
        "Kết nối nông sản Đà Lạt "
        "với công nghệ enzyme."
    ))

    advisor = esc(
        settings.get("advisor")
        or "ThS. Thi Đình Nguyên"
    )

    price = esc(settings.get("price", "Liên hệ"))

    phone = re.sub(
        r"[\s().-]", "",
        str(settings.get("phone", ""))
    )

    valid_phone = bool(
        re.fullmatch(r"\+?[0-9]{9,15}", phone)
    )

    order_open = settings.get("order_open") is True

    banner = image_uri("banner.png")

    if banner:
        hero_background = (
            "linear-gradient(90deg,"
            "rgba(250,247,237,.96),"
            "rgba(250,247,237,.40),"
            "rgba(224,239,232,.35)),"
            f"url('{banner}')"
        )
    else:
        hero_background = (
            "linear-gradient(120deg,"
            "#F8F3E9,#E6EDE0,#B6D1CC)"
        )

    product = picture(
        "product.png",
        "Hạt nêm MYCOUMAMI",
        "hero-product"
    )

    ingredients = picture(
        "ingredients.png",
        "Nấm kim châm, cà chua và khoai tây"
    )

    team = picture(
        "team.png",
        "Đội ngũ nghiên cứu MYCOUMAMI"
    )

    logo = image_uri("logo.png")

    if logo:
        logo_html = f"""
        <img class="university-logo"
             src="{logo}"
             alt="Trường Đại học Yersin Đà Lạt">
        """
    else:
        logo_html = """
        <div class="university-text">
        YERSIN UNIVERSITY
        </div>
        """

    members = [
        esc(m.strip())
        for m in str(
            settings.get("members", "")
        ).splitlines()
        if m.strip()
    ]

    members_html = "".join(
        f'<div class="member">{m}</div>'
        for m in members
    )

    if not members_html:
        members_html = """
        <p>Danh sách thành viên đang cập nhật.</p>
        """

    if valid_phone:

        action_label = (
            "Gọi đặt hàng"
            if order_open
            else "Liên hệ tìm hiểu sản phẩm"
        )

        order_button = f"""
        <a class="myco-btn"
           href="tel:{phone}">
            ☎ {action_label}: {esc(phone)}
        </a>
        """

    else:
        order_button = """
        <span class="contact-note">
            Số điện thoại đang được cập nhật
        </span>
        """

    order_status = (
        "Liên hệ trực tiếp để xác nhận đơn hàng."
        if order_open and valid_phone
        else "Sản phẩm đang trong giai đoạn phát triển."
    )

    # ==========================================
    # THIET KE SCIENCE & NATURE
    # ==========================================

    st.html("""
    <style>

    .stApp {
        background: #F8F3E9;
    }

    [data-testid="stHeader"] {
        background: #F8F3E9;
    }

    .block-container {
        max-width: 1600px;
        padding: 1.2rem 2rem 2rem;
    }

    .myco {
        color: #164535;
        font-family: "Segoe UI", Arial, sans-serif;
        line-height: 1.65;
    }

    .myco * {
        box-sizing: border-box;
    }

    .myco h1,
    .myco h2,
    .myco h3 {
        color: #104B37;
        line-height: 1.2;
    }

    .myco img {
        display: block;
        width: 100%;
        border-radius: 15px;
        object-fit: contain;
    }

    .myco a {
        text-decoration: none;
    }

    .myco section {
        scroll-margin-top: 75px;
    }

    .myco-top {
        background: #104B37;
        color: white;
        text-align: center;
        font-size: 12px;
        letter-spacing: 2px;
        padding: 11px;
        border-bottom: 3px solid #D4B36B;
    }

    .myco-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
        padding: 18px 24px;
        background: white;
        flex-wrap: wrap;
    }

    .myco-brand {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .myco .university-logo {
        width: 190px;
        border-radius: 0;
    }

    .university-text {
        font-size: 13px;
        color: #A4161A;
        font-weight: 800;
    }

    .brand-name {
        font-size: 25px;
        font-weight: 900;
        border-left: 1px solid #D6DAD1;
        padding-left: 15px;
    }

    .nav-links {
        display: flex;
        flex-wrap: wrap;
        gap: 18px;
        align-items: center;
    }

    .myco .nav-links a {
        color: #164535;
        font-size: 14px;
        font-weight: 650;
        transition: color .2s;
    }

    .myco .nav-links a:hover {
        color: #B64C28;
    }

    .myco .myco-btn {
        display: inline-block;
        padding: 13px 23px;
        color: white;
        background: #B64C28;
        border-radius: 30px;
        font-weight: 700;
        box-shadow: 0 5px 15px #9A492822;
        transition: transform .2s,
                    background .2s;
    }

    .myco .myco-btn:hover {
        transform: translateY(-3px);
        background: #104B37;
    }

    .myco .outline-btn {
        display: inline-block;
        border: 1px solid #104B37;
        border-radius: 30px;
        padding: 12px 22px;
        color: #104B37;
        font-weight: 700;
    }

    .myco-hero {
        background-size: cover;
        background-position: center;
        display: grid;
        grid-template-columns: 1fr 1.2fr .65fr;
        align-items: center;
        min-height: 490px;
        padding: 50px 32px;
        gap: 25px;
        overflow: hidden;
        border-radius: 0 0 35px 35px;
        border-bottom: 7px solid #104B37;
        animation: mycoFade .8s ease;
    }

    @keyframes mycoFade {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .myco-kicker {
        font-size: 12px;
        font-weight: 750;
        letter-spacing: 2.5px;
        color: #B64C28;
        text-transform: uppercase;
    }

    .myco-hero h1 {
        font-size: clamp(36px,4vw,65px);
        letter-spacing: -1px;
        font-weight: 900;
        margin: 15px 0 8px;
    }

    .myco-hero h2 {
        font-size: clamp(21px,2.1vw,32px);
        font-weight: 500;
        font-style: italic;
        font-family: Georgia, serif;
        margin-bottom: 20px;
    }

    .myco-hero p {
        font-size: 15px;
        color: #354D42;
    }

    .myco .hero-product {
        border-radius: 25px;
        box-shadow: 0 18px 45px #173D2B25;
        transition: transform .4s ease;
    }

    .myco .hero-product:hover {
        transform: scale(1.025);
    }

    .hero-feature {
        display: flex;
        align-items: center;
        gap: 13px;
        margin: 22px 0;
    }

    .feature-icon {
        flex-shrink: 0;
        width: 52px;
        height: 52px;
        border-radius: 15px;
        background: #FFFFFFA8;
        border: 1px solid #9AB7A7;
        display: grid;
        place-items: center;
        font-size: 25px;
    }

    .hero-feature b {
        font-size: 14px;
        display: block;
    }

    .hero-feature small {
        color: #426152;
    }

    .myco-wave {
        height: 14px;
        border-radius: 0 0 50% 50%;
        background: linear-gradient(
            90deg,#104B37,#8FAF84,#D4B36B
        );
        margin-bottom: 15px;
    }

    .myco-section {
        padding: 48px 28px;
    }

    .myco-title {
        font-size: clamp(25px,3vw,37px);
        font-weight: 800;
        margin: 8px 0 24px;
    }

    .myco-grid {
        display: grid;
        grid-template-columns:
            repeat(3,minmax(0,1fr));
        gap: 20px;
    }

    .myco-two {
        display: grid;
        grid-template-columns: 1fr 1fr;
        align-items: center;
        gap: 30px;
    }

    .myco-card {
        background: #FFFFFF;
        border-radius: 20px;
        padding: 25px;
        border: 1px solid #E2DDD0;
        box-shadow: 0 8px 25px #173D2B09;
        transition: transform .25s,
                    box-shadow .25s;
    }

    .myco-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px #173D2B15;
    }

    .accent-green {
        border-top: 5px solid #104B37;
    }

    .accent-red {
        border-top: 5px solid #B64C28;
        background: #FFF8F2;
    }

    .accent-gold {
        border-top: 5px solid #D4B36B;
        background: #FFFCF1;
    }

    .card-icon {
        font-size: 34px;
        margin-bottom: 12px;
    }

    .science-strip {
        background: #E0EBE5;
        border-radius: 25px;
        padding: 30px;
        display: grid;
        grid-template-columns: repeat(3,1fr);
        gap: 20px;
        text-align: center;
    }

    .science-strip strong {
        display: block;
        font-size: 42px;
        color: #B64C28;
        line-height: 1.3;
    }

    .science-strip small {
        font-size: 14px;
        color: #345F4D;
    }

    .ingredients-area {
        background: linear-gradient(
            120deg,#EFE7D4,#FFFFFF,#E3EEE3
        );
        border-radius: 30px;
        padding: 35px;
    }

    .process-area {
        background: #E7EFE7;
        border-radius: 30px;
        padding: 35px 25px;
    }

    .process-grid {
        display: grid;
        grid-template-columns: repeat(3,1fr);
        gap: 18px;
    }

    .process-step {
        position: relative;
        padding: 25px;
        background: white;
        border-radius: 18px;
        border-bottom: 4px solid #91B49A;
    }

    .step-number {
        font-size: 36px;
        font-weight: 850;
        color: #B64C28;
    }

    .step-symbol {
        float: right;
        font-size: 30px;
    }

    .team-area {
        background: #FFFFFF;
        border-radius: 28px;
        padding: 30px;
    }

    .advisor-card {
        padding: 25px;
        background: #E6EFE8;
        border-left: 5px solid #104B37;
        border-radius: 14px;
        margin-bottom: 20px;
    }

    .member {
        background: #FAF5EA;
        border: 1px solid #E8DFC9;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        font-weight: 600;
    }

    .order-area {
        background: linear-gradient(
            120deg,#104B37,#236B50
        );
        color: white;
        border-radius: 28px;
        padding: 42px 35px;
        text-align: center;
    }

    .order-area h2 {
        color: white;
        font-size: 35px;
    }

    .order-area p {
        color: #DDEEE2;
    }

    .myco .order-area .myco-btn {
        background: #D4B36B;
        color: #103D2D;
    }

    .price-text {
        font-size: 30px;
        font-weight: 800;
        color: #F0D8A1;
    }

    .contact-note {
        display: inline-block;
        padding: 12px 20px;
        border-radius: 20px;
        background: #F8F3E9;
        color: #104B37;
    }

    .myco-footer {
        background: #0D382B;
        color: #C9DED0;
        padding: 35px;
        border-radius: 20px;
        text-align: center;
        border-top: 5px solid #D4B36B;
        margin-top: 25px;
    }

    .myco-footer h2 {
        color: #E4CB94;
        letter-spacing: 4px;
    }

    .myco .admin-link {
        color: #C9DED0;
        font-size: 12px;
        text-decoration: underline;
    }

    .myco-placeholder {
        min-height: 180px;
        background: #E9EDE4;
        color: #557463;
        border-radius: 15px;
        padding: 35px;
        display: grid;
        place-items: center;
        text-align: center;
    }

    @media(max-width:1100px) {

        .myco-hero {
            grid-template-columns: 1fr 1fr;
        }

        .hero-features {
            grid-column: 1 / -1;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }

    }

    @media(max-width:700px) {

        .block-container {
            padding: 10px 12px;
        }

        .myco-hero,
        .myco-two,
        .myco-grid,
        .process-grid {
            grid-template-columns: 1fr;
        }

        .myco-hero {
            padding: 25px 20px;
            min-height: 0;
        }

        .myco-section {
            padding: 30px 5px;
        }

        .myco-nav {
            padding: 15px;
        }

        .myco .university-logo {
            width: 130px;
        }

        .brand-name {
            font-size: 18px;
        }

        .nav-links {
            gap: 12px;
        }

        .science-strip {
            padding: 16px;
            gap: 8px;
        }

        .science-strip strong {
            font-size: 27px;
        }

        .hero-features {
            display: block;
        }

        .ingredients-area,
        .team-area,
        .process-area {
            padding: 20px;
        }

    }

    @media(prefers-reduced-motion:reduce) {
        .myco * {
            animation: none !important;
            transition: none !important;
        }
    }

    </style>
    """)

    # ==========================================
    # QUY TRINH SAN XUAT
    # ==========================================

    steps = [
        (
            "01", "🌱",
            "Thu gom nguyên liệu",
            "Lựa chọn nông sản phù hợp "
            "cho chế biến thực phẩm."
        ),
        (
            "02", "💧",
            "Phân loại và sơ chế",
            "Làm sạch và chuẩn bị "
            "ba dòng nguyên liệu."
        ),
        (
            "03", "🧪",
            "Ứng dụng enzyme",
            "Nghiên cứu thủy phân "
            "gốc nấm bằng papain."
        ),
        (
            "04", "⚗️",
            "Lọc và cô đặc",
            "Thu hồi dịch xử lý "
            "và chuẩn bị phối trộn."
        ),
        (
            "05", "⚙️",
            "Sấy - nghiền - rây",
            "Tạo nền gia vị "
            "dạng bột hoặc hạt."
        ),
        (
            "06", "📦",
            "Đánh giá thành phẩm",
            "Khảo sát chất lượng, "
            "cảm quan và hoàn thiện bao bì."
        )
    ]

    process_html = "".join(
        f"""
        <div class="process-step">
            <span class="step-number">{num}</span>
            <span class="step-symbol">{icon}</span>
            <h3>{title}</h3>
            <p>{detail}</p>
        </div>
        """
        for num, icon, title, detail in steps
    )

    # ==========================================
    # TRANG CHU VA BANNER
    # ==========================================

    st.html(f"""
    <div class="myco">

    <div class="myco-top">
        FOOD INNOVATION & DEVELOPMENT 2026
        &nbsp; • &nbsp; DALAT, VIETNAM
    </div>

    <nav class="myco-nav">
        <div class="myco-brand">
            {logo_html}
            <div class="brand-name">
                MYCOUMAMI
            </div>
        </div>

        <div class="nav-links">
            <a href="#trang-chu">Trang chủ</a>
            <a href="#cau-chuyen">Giới thiệu</a>
            <a href="#san-pham">Sản phẩm</a>
            <a href="#quy-trinh">Quy trình</a>
            <a href="#nghien-cuu">Nghiên cứu</a>
            <a href="#doi-ngu">Đội ngũ</a>
        </div>

        <a class="myco-btn" href="#dat-hang">
            ☎ Đặt hàng
        </a>
    </nav>

    <section id="trang-chu"
             class="myco-hero"
             style="background-image:{hero_background}">

        <div>

            <div class="myco-kicker">
                Science meets nature
            </div>

            <h1>MYCOUMAMI</h1>

            <h2>{headline}</h2>

            <p>{description}</p>

            <p><b>{slogan}</b></p>

            <a href="#san-pham"
               class="myco-btn">
                Khám phá sản phẩm →
            </a>

        </div>

        <div>{product}</div>

        <div class="hero-features">

            <div class="hero-feature">
                <div class="feature-icon">🌿</div>
                <div>
                    <b>THIÊN NHIÊN</b>
                    <small>
                    Nông sản địa phương
                    </small>
                </div>
            </div>

            <div class="hero-feature">
                <div class="feature-icon">🧪</div>
                <div>
                    <b>KHOA HỌC</b>
                    <small>
                    Công nghệ enzyme
                    </small>
                </div>
            </div>

            <div class="hero-feature">
                <div class="feature-icon">♻️</div>
                <div>
                    <b>BỀN VỮNG</b>
                    <small>
                    Nâng giá trị nguyên liệu
                    </small>
                </div>
            </div>

        </div>

    </section>

    <div class="myco-wave"></div>

    <!-- CAU CHUYEN -->

    <section class="myco-section"
             id="cau-chuyen">

        <div class="myco-two">

            <div>
                <div class="myco-kicker">
                    Our story
                </div>

                <h2 class="myco-title">
                    Từ những điều bị bỏ quên
                    đến một giá trị mới.
                </h2>

                <p>
                Không phải mọi nông sản ngoài chuẩn
                thương mại đều mất đi giá trị sử dụng.
                </p>

                <p>
                MYCOUMAMI hướng đến khai thác
                gốc nấm kim châm, cà chua và
                khoai tây còn phù hợp cho chế biến,
                kết hợp cùng công nghệ enzyme.
                </p>

                <p>
                Một hành trình kết nối nông nghiệp,
                khoa học thực phẩm và đổi mới
                sáng tạo tại Đà Lạt.
                </p>

            </div>

            <div>{ingredients}</div>

        </div>

        <div class="science-strip">

            <div>
                <strong>03</strong>
                <small>Nguyên liệu chủ đạo</small>
            </div>

            <div>
                <strong>17</strong>
                <small>Nghiệm thức khảo sát</small>
            </div>

            <div>
                <strong>01</strong>
                <small>Dự án đổi mới sáng tạo</small>
            </div>

        </div>

    </section>

    <!-- SAN PHAM -->

    <section id="san-pham"
             class="myco-section">

        <div class="ingredients-area">

            <div class="myco-kicker">
                Inspired by Da Lat
            </div>

            <h2 class="myco-title">
                Ba nguyên liệu - Một hương vị
            </h2>

            <div class="myco-grid">

                <div class="myco-card accent-green">
                    <div class="card-icon">🍄</div>
                    <h3>Nấm kim châm</h3>
                    <p>
                    Nguồn nguyên liệu được khảo sát
                    thủy phân để phát triển nền vị nấm.
                    </p>
                </div>

                <div class="myco-card accent-red">
                    <div class="card-icon">🍅</div>
                    <h3>Cà chua</h3>
                    <p>
                    Góp phần xây dựng nền hương vị
                    và màu sắc cho sản phẩm.
                    </p>
                </div>

                <div class="myco-card accent-gold">
                    <div class="card-icon">🥔</div>
                    <h3>Khoai tây</h3>
                    <p>
                    Định hướng bổ sung độ đầy vị
                    và cấu trúc cho nền gia vị.
                    </p>
                </div>

            </div>

        </div>

    </section>

    <section class="myco-section">

        <div class="myco-two">

            <div>
                {product}
            </div>

            <div>
                <div class="myco-kicker">
                    MYCOUMAMI COLLECTION
                </div>

                <h2 class="myco-title">
                    Hạt nêm nấm - rau củ
                </h2>

                <p>{description}</p>

                <p>
                    ✓ Nấm kim châm, cà chua, khoai tây
                </p>

                <p>
                    ✓ Định hướng ứng dụng công nghệ enzyme
                </p>

                <p>
                    ✓ Quy cách bao bì thiết kế: 100 g
                </p>

                <p>
                    ✓ Định hướng sử dụng cho canh,
                    súp và các món chế biến
                </p>

                <h3>Giá tham khảo: {price}</h3>

                <a class="myco-btn"
                   href="#dat-hang">
                    Liên hệ sản phẩm →
                </a>

            </div>

        </div>

    </section>

    <!-- QUY TRINH -->

    <section class="myco-section"
             id="quy-trinh">

        <div class="process-area">

            <div class="myco-kicker">
                From farm to food
            </div>

            <h2 class="myco-title">
                Quy trình tạo nên MYCOUMAMI
            </h2>

            <div class="process-grid">
                {process_html}
            </div>

            <p>
            <small>
            Quy trình định hướng nghiên cứu
            và phát triển sản phẩm.
            </small>
            </p>

        </div>

    </section>

    <!-- NGHIEN CUU -->

    <section class="myco-section"
             id="nghien-cuu">

        <div class="myco-kicker">
            Research and innovation
        </div>

        <h2 class="myco-title">
            Khoa học phía sau hương vị
        </h2>

        <div class="myco-grid">

            <div class="myco-card accent-green">
                <div class="card-icon">🧪</div>
                <h3>Công nghệ enzyme</h3>
                <p>
                Khảo sát quá trình thủy phân
                gốc nấm kim châm bằng papain.
                </p>
            </div>

            <div class="myco-card accent-red">
                <div class="card-icon">📊</div>
                <h3>Thiết kế thực nghiệm</h3>
                <p>
                Khảo sát ba yếu tố bằng
                phương pháp bề mặt đáp ứng.
                </p>
            </div>

            <div class="myco-card accent-gold">
                <div class="card-icon">♻️</div>
                <h3>Giá trị nông sản</h3>
                <p>
                Hướng đến nâng cao giá trị
                sử dụng nguyên liệu địa phương.
                </p>
            </div>

        </div>

        <p>
            <a class="outline-btn" href="#poster-video">
                Xem poster và video giới thiệu →
            </a>
        </p>

    </section>

    <!-- DOI NGU -->

    <section class="myco-section"
             id="doi-ngu">

        <div class="team-area">

            <div class="myco-kicker">
                Meet our team
            </div>

            <h2 class="myco-title">
                Những người tạo nên MYCOUMAMI
            </h2>

            <div class="myco-two">

                <div>{team}</div>

                <div>

                    <div class="advisor-card">
                        GIẢNG VIÊN HƯỚNG DẪN

                        <h3>{advisor}</h3>

                        <p>
                        Trường Đại học Yersin Đà Lạt
                        </p>
                    </div>

                    <h3>Thành viên nhóm</h3>

                    {members_html}

                </div>

            </div>

        </div>

    </section>

    <section class="myco-section"
             id="poster-video">

        <div class="myco-kicker">
            Discover MYCOUMAMI
        </div>

        <h2 class="myco-title">
            Khám phá hành trình nghiên cứu
        </h2>

    </section>

    </div>
    """)

    # ==========================================
    # POSTER VA VIDEO
    # ==========================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📄 Poster dự án")

        poster = get_file("poster.pdf")

        if poster and poster.startswith(b"%PDF"):

            try:
                st.pdf(poster, height=580)
            except Exception:
                st.info(
                    "Bạn có thể tải poster "
                    "để xem toàn bộ nội dung."
                )

            st.download_button(
                "Tải poster MYCOUMAMI",
                data=poster,
                file_name="MYCOUMAMI_Poster.pdf",
                mime="application/pdf",
                width="stretch"
            )

        else:
            st.info("Poster đang được cập nhật.")

    with col2:

        st.subheader("🎬 Video giới thiệu")

        video = get_file("video.mp4")

        video_url = str(
            settings.get("video_url", "")
        )

        if video:

            st.video(
                video,
                format="video/mp4"
            )

        elif video_url.startswith((
            "https://www.youtube.com/",
            "https://youtu.be/"
        )):

            st.video(video_url)

        else:

            st.info(
                "Video giới thiệu nhóm "
                "đang được cập nhật."
            )

    # ==========================================
    # DAT HANG VA FOOTER
    # ==========================================

    st.html(f"""
    <div class="myco">

        <section id="dat-hang"
                 class="myco-section">

            <div class="order-area">

                <div style="color:#D4B36B;
                            letter-spacing:3px">
                    FROM DALAT TO YOUR KITCHEN
                </div>

                <h2>
                    Mang hương vị Đà Lạt
                    về căn bếp của bạn.
                </h2>

                <p>
                    MYCOUMAMI - Hạt nêm nấm, rau củ
                </p>

                <div class="price-text">
                    {price}
                </div>

                <br>

                {order_button}

                <p>{order_status}</p>

                <small>
                    Website không thu tiền
                    hoặc tự động xác nhận đơn hàng.
                </small>

            </div>

        </section>

        <footer class="myco-footer">

            <h2>MYCOUMAMI</h2>

            <p>{slogan}</p>

            <p>
                TRƯỜNG ĐẠI HỌC YERSIN ĐÀ LẠT
            </p>

            <p>
                FOOD INNOVATION & DEVELOPMENT 2026
            </p>

            <hr style="opacity:.25">

            <small>© 2026 MYCOUMAMI TEAM</small>

            <br><br>

            <a class="admin-link"
               href="?admin=1"
               target="_self">
                ⚙ Quản trị website
            </a>

        </footer>

    </div>
    """)
