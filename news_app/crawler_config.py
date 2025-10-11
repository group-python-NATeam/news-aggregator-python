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
    "dantri": {
        "base_url": "https://dantri.com.vn",
        "categories": {
            "cong-nghe": "cong-nghe.htm",
            "kinh-te": "kinh-doanh.htm",
            "giao-duc": "giao-duc.htm",
            "giai-tri": "giai-tri.htm",
            "suc-khoe": "suc-khoe.htm",
            "the-thao": "the-thao.htm",
            "phap-luat": "phap-luat.htm",
            "xa-hoi": "xa-hoi.htm",
        }
    },
    "tuoitre": {
        "base_url": "https://tuoitre.vn",
        "categories": {
            "cong-nghe": "cong-nghe/nhip-song-so.htm",
            "kinh-te": "kinh-te.htm",
            "giao-duc": "giao-duc.htm",
            "giai-tri": "giai-tri.htm",
            "suc-khoe": "suc-khoe.htm",
            "the-thao": "the-thao.htm",
            "phap-luat": "phap-luat.htm",
            "xa-hoi": "xa-hoi.htm",
        }
    },
    "thanhnien": {
        "base_url": "https://thanhnien.vn",
        "categories": {
            "cong-nghe": "https://thanhnien.vn/cong-nghe.htm",
            "xa-hoi": "https://thanhnien.vn/thoi-su.htm",
            "the-thao": "https://thanhnien.vn/the-thao.htm",
            "kinh-te": "https://thanhnien.vn/kinh-te.htm",
            "giao-duc": "https://thanhnien.vn/giao-duc.htm",
            "giai-tri": "https://thanhnien.vn/giai-tri.htm",
            "suc-khoe": "https://thanhnien.vn/suc-khoe.htm",
            "phap-luat": "https://thanhnien.vn/phap-luat.htm",
        }
    },
    # Thêm các báo khác ở đây trong tương lai
}
