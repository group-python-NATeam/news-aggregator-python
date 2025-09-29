# news_app/crawler_config.py

# Cấu hình này ánh xạ từ slug CHUẨN của hệ thống (8 slug)
# sang slug THỰC TẾ của từng trang báo.
CRAWLER_CONFIGS = {
    "VnExpress": {
        "base_url": "https://vnexpress.net",
        "categories": {
            "cong-nghe": "so-hoa",
            "kinh-te": "kinh-doanh",
            "giao-duc": "giao-duc",
            "giai-tri": "giai-tri",
            "suc-khoe": "suc-khoe",
            "the-thao": "the-thao",
            "phap-luat": "phap-luat",
            "xa-hoi": "thoi-su", # Ví dụ: VnExpress gọi Xã hội là Thời sự
        }
    },
    "Dân Trí": {
        "base_url": "https://dantri.com.vn",
        "categories": {
            "cong-nghe": "suc-manh-so",
            "kinh-te": "kinh-doanh",
            "giao-duc": "giao-duc-khuyen-hoc",
            "giai-tri": "giai-tri",
            "suc-khoe": "suc-khoe",
            "the-thao": "the-thao",
            "phap-luat": "phap-luat",
            "xa-hoi": "xa-hoi",
        }
    },
    "Tuổi Trẻ": {
        "base_url": "https://tuoitre.vn",
        "categories": {
            "cong-nghe": "nhip-song-so",
            "kinh-te": "kinh-doanh",
            "giao-duc": "giao-duc",
            "giai-tri": "giai-tri",
            "suc-khoe": "suc-khoe",
            "the-thao": "the-thao",
            "phap-luat": "phap-luat",
            "xa-hoi": "thoi-su",
        }
    },
    "Thanh Niên": {
        "base_url": "https://thanhnien.vn",
        "categories": {
            "cong-nghe": "cong-nghe",
            "kinh-te": "kinh-te",
            "giao-duc": "giao-duc",
            "giai-tri": "giai-tri",
            "suc-khoe": "suc-khoe",
            "the-thao": "the-thao",
            "phap-luat": "phap-luat",
            "xa-hoi": "thoi-su",
        }
    },
    # Thêm các báo khác ở đây trong tương lai
}
