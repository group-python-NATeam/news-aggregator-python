# Phát triển Giao diện Người dùng (UI_UX.md)

Phần này tập trung vào việc xây dựng giao diện người dùng (UI) và trải nghiệm người dùng (UX) của Website Tin tức Tự động, đặc biệt là hướng tới trải nghiệm "lướt như TikTok".

## 1. Mục tiêu Trải nghiệm "Lướt tin" (TikTok-like)

Mục tiêu chính là tạo ra một giao diện trực quan, hấp dẫn, cho phép người dùng dễ dàng cuộn/vuốt qua các bài báo một cách mượt mà. Mỗi bài báo sẽ được trình bày dưới dạng một "thẻ" (card) lớn, chiếm gần như toàn bộ màn hình, bao gồm:

*   **Hình ảnh chính:** Hình ảnh nổi bật của bài báo.
*   **Tiêu đề:** Ngắn gọn, dễ đọc.
*   **Tóm tắt:** Một đoạn tóm tắt ngắn gọn nội dung chính.
*   **Nút "Đọc báo":** Để phát giọng đọc tự động.
*   **Thông tin nguồn/chuyên mục:** Để người dùng biết bài báo đến từ đâu.

## 2. Cấu trúc Frontend (Sprint 2 & 4)

Chúng ta sẽ sử dụng Django Templates (`.html`) kết hợp với HTML, CSS và JavaScript thuần (hoặc một thư viện/framework CSS nhẹ như Bootstrap để tăng tốc độ phát triển).

### 2.1. Django Templates (`news_app/templates/news_app/*.html`)

*   **`base.html`:** Template cơ sở chứa cấu trúc HTML chung, head, footer, và các liên kết CSS/JS toàn cục.
*   **`index.html` (Trang chủ/Lướt tin):** Đây sẽ là trang chính hiển thị trải nghiệm "lướt tin".
    *   Sẽ chứa một vòng lặp để hiển thị các `article_card`.
    *   Cần có các phần tử điều hướng (ví dụ: nút lên/xuống, hoặc xử lý sự kiện cuộn/vuốt).
*   **`category_list.html` (Trang chuyên mục):** Hiển thị danh sách các chuyên mục để người dùng lựa chọn.
*   **`article_detail.html` (Trang chi tiết bài viết - dự phòng):** Mặc dù trải nghiệm chính là "lướt tin", nhưng có thể cần một trang chi tiết đầy đủ nội dung cho những bài báo người dùng muốn đọc kỹ hơn.

### 2.2. CSS (Styling)

*   Sử dụng CSS để tạo giao diện "thẻ" bài báo, đảm bảo chúng chiếm phần lớn màn hình.
*   Tối ưu hóa cho thiết bị di động (responsive design) là cực kỳ quan trọng cho trải nghiệm "TikTok-like".
*   Sử dụng Flexbox hoặc Grid để bố cục các thành phần trong thẻ bài báo.
*   Tạo hiệu ứng chuyển động mượt mà khi lướt giữa các bài báo.

### 2.3. JavaScript (Tương tác)

JavaScript sẽ đóng vai trò quan trọng trong việc tạo ra trải nghiệm động:

*   **Xử lý cuộn/vuốt:** Phát hiện sự kiện cuộn/vuốt của người dùng để chuyển đổi giữa các bài báo.
*   **Phát/Dừng giọng đọc:** Tương tác với API Text-to-Speech để phát và dừng audio.
*   **Tải thêm bài báo (Infinite Scroll):** Khi người dùng lướt đến cuối danh sách, JavaScript sẽ gửi yêu cầu AJAX để tải thêm bài báo mới mà không cần tải lại trang.

## 3. Phát triển Giao diện "Lướt tin" (Sprint 4)

### 3.1. Thiết kế Thẻ Bài báo (Article Card)

Mỗi bài báo sẽ được hiển thị trong một `div` hoặc `section` có kích thước tương đương màn hình. Các thành phần bên trong sẽ được bố cục rõ ràng.

```html
<!-- Ví dụ cấu trúc article_card.html -->
<div class="article-card">
    <img src="{{ article.image_url }}" alt="{{ article.title }}" class="article-image">
    <div class="article-content">
        <h2 class="article-title">{{ article.title }}</h2>
        <p class="article-summary">{{ article.summary }}</p>
        <div class="article-meta">
            <span class="article-source">{{ article.source.name }}</span>
            <span class="article-category">{{ article.category.name }}</span>
        </div>
        <button class="play-audio-btn" data-article-id="{{ article.id }}">▶ Đọc báo</button>
    </div>
</div>
```

### 3.2. Cơ chế Cuộn/Vuốt (Scrolling/Swiping)

*   **CSS Scroll Snap:** Đây là một tính năng CSS mạnh mẽ cho phép các phần tử "khớp" vào vị trí khi cuộn, tạo cảm giác như đang lướt qua các trang.
    ```css
    .article-feed {
        scroll-snap-type: y mandatory;
        overflow-y: scroll;
        height: 100vh; /* Chiều cao bằng viewport */
    }
    .article-card {
        scroll-snap-align: start;
        height: 100vh;
        width: 100%;
        /* ... các style khác */
    }
    ```
*   **JavaScript Intersection Observer API:** Sử dụng để phát hiện khi một bài báo mới đi vào viewport, từ đó có thể kích hoạt tải thêm dữ liệu hoặc các hiệu ứng khác.

### 3.3. Tích hợp Giọng đọc (Text-to-Speech)

*   Khi người dùng nhấn nút "Đọc báo", JavaScript sẽ gửi yêu cầu AJAX đến một endpoint Django (`/api/article/<id>/tts/`).
*   Endpoint này sẽ trả về URL của file MP3 chứa giọng đọc (hoặc tạo mới nếu chưa có).
*   JavaScript sẽ sử dụng `Audio` API của trình duyệt để phát file MP3 đó.

### 3.4. Xử lý Hình ảnh trên Frontend

*   **Hiển thị hình ảnh chính:** Sử dụng `article.image_url` để hiển thị hình ảnh.
*   **Xử lý hình ảnh mặc định/tạo tự động:** Nếu `article.image_url` rỗng, frontend sẽ hiển thị hình ảnh mặc định theo chuyên mục (đã được backend cung cấp) hoặc một placeholder.
*   **Lazy Loading:** Sử dụng `loading="lazy"` cho thẻ `<img>` để chỉ tải hình ảnh khi chúng gần xuất hiện trên màn hình, giúp cải thiện hiệu năng.

## 4. Tối ưu hóa Hiệu năng (Sprint 4)

*   **Tối ưu hóa hình ảnh:** Nén hình ảnh, sử dụng định dạng hiện đại (WebP), và phục vụ hình ảnh có kích thước phù hợp với thiết bị.
*   **Tải dữ liệu không đồng bộ (AJAX):** Tải thêm bài báo khi người dùng cuộn xuống mà không cần tải lại toàn bộ trang.
*   **Caching:** Cache các tài nguyên tĩnh (CSS, JS, hình ảnh) và dữ liệu API để giảm thời gian tải.
*   **Minify CSS/JS:** Giảm kích thước file CSS và JavaScript.
*   **Kiểm tra với Lighthouse:** Sử dụng công cụ Lighthouse của Chrome DevTools để đánh giá và cải thiện hiệu năng, khả năng tiếp cận, và SEO của trang web.

---

**Tác giả:** Manus AI
**Ngày:** 07/10/2025
