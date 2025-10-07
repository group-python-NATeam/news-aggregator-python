# Dự án: Website Tin tức Tự động (News Aggregator)

## 🚀 Tổng quan Dự án

Dự án "Website Tin tức Tự động" là một hệ thống tổng hợp tin tức tiếng Việt từ nhiều nguồn báo chính thống, tự động xử lý, phân loại và làm giàu dữ liệu để cung cấp trải nghiệm đọc tin tức độc đáo, trực quan cho người dùng. Mục tiêu cuối cùng là tạo ra một nền tảng cho phép người dùng "lướt" qua các tin tức một cách nhanh chóng và hấp dẫn, tương tự như trải nghiệm trên các nền tảng video ngắn như TikTok, với hình ảnh, đoạn tóm tắt và giọng đọc tự động.

### Mục tiêu chính:

*   **Thu thập và phân loại tin tức:** Tự động crawl tin tức từ các nguồn báo lớn và phân loại chúng vào các chuyên mục cụ thể.
*   **Trải nghiệm người dùng "TikTok-like":** Cung cấp giao diện trực quan, cho phép người dùng dễ dàng lướt qua các bài báo, mỗi bài hiển thị với hình ảnh, tóm tắt ngắn gọn và tùy chọn nghe giọng đọc tự động.
*   **Tự động hóa:** Toàn bộ quy trình từ thu thập, xử lý đến hiển thị tin tức đều được tự động hóa.

## ✨ Tính năng nổi bật (Dự kiến)

*   **Tổng hợp tin tức đa nguồn:** Thu thập bài viết từ VnExpress, Dân Trí, Tuổi Trẻ, Thanh Niên.
*   **Phân loại chuyên mục:** Tự động gán bài viết vào 8 chuyên mục chính (Công nghệ, Kinh tế, Giáo dục, Giải trí, Sức khỏe, Thể thao, Pháp luật, Xã hội).
*   **Phát hiện trùng lặp:** Đảm bảo mỗi bài viết là duy nhất trong hệ thống.
*   **Tóm tắt văn bản:** Cung cấp bản tóm tắt ngắn gọn cho mỗi bài báo (sử dụng API tóm tắt).
*   **Text-to-Speech:** Chuyển đổi nội dung bài báo thành giọng nói tự động (sử dụng Google Text-to-Speech API).
*   **Giao diện "Lướt tin":** Trải nghiệm đọc tin tức dạng cuộn/vuốt, tối ưu cho thiết bị di động.
*   **Xử lý hình ảnh thông minh:** Ưu tiên hình ảnh từ bài báo gốc, hoặc sử dụng hình ảnh mặc định/tạo tự động khi không có.

## 🛠️ Công nghệ sử dụng

*   **Ngôn ngữ lập trình:** Python 3.12.6
*   **Web Framework:** Django 5.2.6
*   **Web Scraping:** `requests`, `BeautifulSoup4`
*   **Database:** PostgreSQL (production), SQLite (development)
*   **Containerization:** Podman
*   **AI/ML:** PhoBERT (cho phân loại), API tóm tắt văn bản (dự kiến), Google Text-to-Speech API
*   **DevOps:** GitHub Actions, Render (triển khai)

## 🗺️ Lộ trình Phát triển (Roadmap)

Dự án được chia thành các Sprint với mục tiêu và nhiệm vụ rõ ràng. Trạng thái hiện tại của dự án đã hoàn thành Sprint 1 và đang trong quá trình chuẩn bị cho các Sprint tiếp theo.

### Sprint 0: Nền móng (Foundation) - **Đã hoàn thành**
*   Khởi tạo Git Repository, thống nhất Tech Stack (Python 3.11/3.12, Django, PostgreSQL, Pre-trained AI Model), thiết lập Git Flow, mời thành viên và thiết lập Kanban Board.

### Sprint 1: Thu thập Dữ liệu thô (Raw Data Collection) - **Đã hoàn thành**
*   Hoàn thiện Models `Category`, `Source`, `Article`. Xây dựng crawler cho VnExpress, bóc tách dữ liệu (title, original_url, cleaned_content, publication_date), tạo `content_hash` và lưu vào database. Tái cấu trúc và mở rộng crawler cho Dân Trí, Tuổi Trẻ, Thanh Niên. Bắt đầu thu thập và gán nhãn thủ công bộ dữ liệu nhỏ cho AI.

### Sprint 2: Lõi AI & Giao diện cơ bản (AI Core & Basic UI) - **Đang thực hiện/Chuẩn bị**
*   Nghiên cứu và thiết lập môi trường fine-tune PhoBERT. Viết script fine-tune model và tích hợp vào Django để phân loại bài báo. Viết `views.py` và Django Templates cơ bản. Bắt đầu phác thảo cấu trúc HTML/CSS cho trải nghiệm "lướt như TikTok". Cập nhật Models và Crawler để lưu trữ URL hình ảnh chính của bài báo.

### Sprint 3: Tóm tắt, Giọng đọc & Tự động hóa (Summarization, TTS & Automation) - **Dự kiến**
*   Xây dựng module tóm tắt văn bản (ưu tiên tích hợp API có sẵn). Tích hợp tính năng Text-to-Speech dùng Google API. Thiết lập GitHub Actions để tự động chạy crawler. Cập nhật template Django để hiển thị tóm tắt và nút "Đọc báo" trên cấu trúc "lướt như TikTok".

### Sprint 4: Giao diện "TikTok-like" & Tối ưu (TikTok-like UI & Optimization) - **Dự kiến**
*   Phát triển giao diện người dùng "lướt như TikTok" hoàn chỉnh (cuộn/vuốt mượt mà, hiển thị hình ảnh, điều khiển giọng đọc). Xử lý hình ảnh khi bài báo không có hình ảnh chính (ưu tiên bộ ảnh mặc định/tạo ảnh đơn giản). Kiểm tra và tối ưu hiệu năng toàn diện.

### Sprint 5: Triển khai & Bảo trì (Deployment & Maintenance) - **Dự kiến**
*   Cấu hình dự án Django cho production. Tạo và cấu hình database PostgreSQL trên Render. Triển khai ứng dụng Django lên Render. Thiết lập giám sát và cảnh báo. Hoàn thiện tài liệu hướng dẫn sử dụng và bảo trì.

## 🧑‍💻 Hướng dẫn cho Developer

Các tài liệu chi tiết hơn sẽ được cung cấp trong các file Markdown riêng biệt để hỗ trợ các lập trình viên trong nhóm và những ai muốn tái tạo dự án:

*   `SETUP.md`: Hướng dẫn cài đặt môi trường phát triển.
*   `CRAWLER.md`: Chi tiết về cơ chế thu thập dữ liệu.
*   `AI_CORE.md`: Hướng dẫn về phần AI phân loại và tóm tắt.
*   `UI_UX.md`: Mô tả chi tiết về phát triển giao diện người dùng.
*   `DEPLOYMENT.md`: Hướng dẫn triển khai và quản lý dự án.

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tham khảo các file hướng dẫn chi tiết và quy trình làm việc trên GitHub Project Kanban Board.

---

**Tác giả:** Manus AI
**Ngày:** 07/10/2025
