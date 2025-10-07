# Lõi AI của Dự án (AI_CORE.md)

Phần này mô tả các thành phần Trí tuệ Nhân tạo (AI) và Học máy (ML) cốt lõi của dự án, bao gồm phân loại bài báo, tóm tắt văn bản và chuyển văn bản thành giọng nói (Text-to-Speech). Với việc team chưa có nhiều kinh nghiệm, tài liệu này sẽ cung cấp hướng dẫn chi tiết và các gợi ý thực tế.

## 1. Phân loại Bài báo (Article Classification)

### 1.1. Mục tiêu

Phân loại các bài báo đã thu thập được vào 8 chuyên mục định sẵn của hệ thống (Công nghệ, Kinh tế, Giáo dục, Giải trí, Sức khỏe, Thể thao, Pháp luật, Xã hội). Việc này giúp người dùng dễ dàng tìm kiếm và lướt tin theo sở thích.

### 1.2. Công nghệ: PhoBERT Fine-tuning

Chúng ta sẽ sử dụng **PhoBERT**, một mô hình BERT được huấn luyện trước (pre-trained) trên kho ngữ liệu tiếng Việt lớn. PhoBERT rất mạnh mẽ trong việc hiểu ngữ nghĩa tiếng Việt và là lựa chọn lý tưởng cho tác vụ phân loại văn bản.

Để PhoBERT có thể phân loại chính xác các chuyên mục của chúng ta, chúng ta cần thực hiện **fine-tuning** (tinh chỉnh) mô hình trên một tập dữ liệu nhỏ đã được gán nhãn.

### 1.3. Hướng dẫn chi tiết Fine-tuning PhoBERT (Sprint 2)

Với team chưa có nhiều kinh nghiệm, việc fine-tuning một mô hình ngôn ngữ lớn có thể hơi phức tạp. Dưới đây là các bước chi tiết:

#### Bước 1: Chuẩn bị Dữ liệu

*   **Dữ liệu đầu vào:** Tập dữ liệu 240 bài báo đã được gán nhãn thủ công ở Sprint 1 (30 bài/chuyên mục x 8 chuyên mục).
*   **Định dạng:** Dữ liệu nên được tổ chức dưới dạng CSV hoặc JSON, với mỗi dòng/đối tượng chứa `text` (nội dung bài báo) và `label` (tên chuyên mục).

#### Bước 2: Thiết lập Môi trường (Google Colab)

*   **Tại sao dùng Google Colab?** Colab cung cấp GPU miễn phí, giúp quá trình huấn luyện nhanh hơn rất nhiều so với CPU thông thường. Điều này rất quan trọng khi làm việc với các mô hình lớn như BERT.
*   **Các bước:**
    1.  Mở trình duyệt và truy cập [Google Colab](https://colab.research.google.com/).
    2.  Tạo một Notebook mới.
    3.  Vào `Runtime` -> `Change runtime type`, chọn `GPU` làm `Hardware accelerator`.
    4.  Kết nối Google Drive của bạn để lưu trữ dữ liệu và mô hình đã huấn luyện.

#### Bước 3: Cài đặt Thư viện

Trong Colab Notebook, chạy các lệnh sau để cài đặt thư viện `transformers` của Hugging Face và `pytorch` (nếu chưa có).

```python
!pip install transformers accelerate datasets evaluate torch
```

#### Bước 4: Viết Script Fine-tuning

Bạn sẽ cần một script Python để tải PhoBERT, chuẩn bị dữ liệu, và huấn luyện mô hình. Dưới đây là một ví dụ cơ bản:

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from datasets import Dataset
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# 1. Tải dữ liệu (ví dụ từ CSV)
# Thay thế 'your_data.csv' bằng đường dẫn đến file dữ liệu của bạn trên Google Drive
df = pd.read_csv('your_data.csv') 

# Ánh xạ nhãn string sang ID
unique_labels = df['label'].unique()
label_to_id = {label: i for i, label in enumerate(unique_labels)}
id_to_label = {i: label for i, label in enumerate(unique_labels)}
df['labels'] = df['label'].map(label_to_id)

# Chia tập dữ liệu
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

train_dataset = Dataset.from_pandas(train_df)
test_dataset = Dataset.from_pandas(test_df)

# 2. Tải Tokenizer và Model PhoBERT
model_name = 


model_name = "vinai/phobert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=len(unique_labels))

# 3. Tiền xử lý dữ liệu
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)

tokenized_train_dataset = train_dataset.map(tokenize_function, batched=True)
tokenized_test_dataset = test_dataset.map(tokenize_function, batched=True)

# 4. Định nghĩa hàm tính toán metrics
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average=\'weighted\')
    acc = accuracy_score(labels, preds)
    return {
        \'accuracy\': acc,
        \'f1\': f1,
        \'precision\': precision,
        \'recall\': recall
    }

# 5. Cấu hình và Huấn luyện
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3, # Số epoch có thể điều chỉnh
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_test_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()

# 6. Lưu model đã huấn luyện
model.save_pretrained("./my_phobert_classifier")
tokenizer.save_pretrained("./my_phobert_classifier")
```

#### Bước 5: Tích hợp Model vào Django (Sprint 2)

Sau khi huấn luyện và lưu model, bạn cần tích hợp nó vào ứng dụng Django để phân loại bài báo mới được crawl.

1.  **Tạo thư mục `ml_models`:** Trong `news_app`, tạo một thư mục `ml_models` và copy các file model đã lưu (`config.json`, `pytorch_model.bin`, `tokenizer.json`, v.v.) vào đó.

2.  **Tạo service phân loại:** Tạo file `news_app/services/ai_classifier.py`.

    ```python
    # news_app/services/ai_classifier.py

    import os
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    from django.conf import settings

    class AIClassifier:
        _instance = None

        def __new__(cls):
            if cls._instance is None:
                cls._instance = super(AIClassifier, cls).__new__(cls)
                cls._instance._load_model()
            return cls._instance

        def _load_model(self):
            model_path = os.path.join(settings.BASE_DIR, \'news_app\', \'ml_models\', \'my_phobert_classifier\')
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.id_to_label = {0: \'Công nghệ\', 1: \'Kinh tế\', ...} # Cần ánh xạ lại từ script fine-tuning

        def predict_category(self, text):
            inputs = self.tokenizer(text, return_tensors=\'pt\', truncation=True, padding=True, max_length=512)
            outputs = self.model(**inputs)
            predicted_class_id = outputs.logits.argmax().item()
            return self.id_to_label[predicted_class_id]

    classifier = AIClassifier() # Khởi tạo singleton
    ```

3.  **Cập nhật Crawler:** Trong các crawler (ví dụ `crawl_vnexpress.py`), sau khi đã làm sạch nội dung bài báo, gọi service này để lấy category và lưu vào database.

    ```python
    # Trong hàm handle() của crawler
    from news_app.services.ai_classifier import classifier
    # ...
    cleaned_content = clean_html(article_content) # Giả sử có hàm clean_html
    predicted_category_name = classifier.predict_category(cleaned_content)
    category = Category.objects.get(name=predicted_category_name)
    # ... lưu article với category này
    ```

## 2. Tóm tắt Văn bản (Text Summarization) (Sprint 3)

### 2.1. Mục tiêu

Cung cấp một bản tóm tắt ngắn gọn cho mỗi bài báo, giúp người dùng nắm bắt nội dung chính nhanh chóng mà không cần đọc toàn bộ bài viết. Điều này rất quan trọng cho trải nghiệm "lướt tin" nhanh.

### 2.2. Công nghệ: Tích hợp API Tóm tắt (Ưu tiên)

Với kinh nghiệm hạn chế của team và để nhanh chóng có được tính năng, chúng ta sẽ ưu tiên tích hợp một API tóm tắt văn bản có sẵn thay vì xây dựng từ đầu.

#### Đề xuất API:

*   **Google Cloud Natural Language API:** Cung cấp tính năng tóm tắt (Extractive Summarization). Có thể có chi phí nhưng chất lượng cao.
*   **OpenAI API (GPT-3.5/GPT-4):** Rất mạnh mẽ trong việc tóm tắt, có thể tùy chỉnh độ dài và phong cách tóm tắt. Cần cân nhắc chi phí.
*   **Các thư viện Python có sẵn:** Nếu muốn giải pháp miễn phí và mã nguồn mở, có thể dùng các thư viện như `sumy` (đã được gợi ý) hoặc các mô hình tóm tắt tiếng Việt trên Hugging Face (nếu có).

#### Hướng dẫn Tích hợp (Ví dụ với một API giả định):

1.  **Tạo service tóm tắt:** Tạo file `news_app/services/summarizer.py`.

    ```python
    # news_app/services/summarizer.py

    import requests
    import json

    # Thay thế bằng API key và endpoint thực tế
    API_ENDPOINT = "https://api.example.com/summarize"
    API_KEY = "YOUR_API_KEY"

    def get_summary(text, max_length=150):
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "max_length": max_length
        }
        try:
            response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json().get("summary", "")
        except requests.exceptions.RequestException as e:
            print(f"Error calling summarization API: {e}")
            return ""
    ```

2.  **Cập nhật Crawler:** Sau khi crawl và phân loại bài báo, gọi service tóm tắt để lấy summary và lưu vào database.

    ```python
    # Trong hàm handle() của crawler
    from news_app.services.summarizer import get_summary
    # ...
    cleaned_content = clean_html(article_content)
    summary = get_summary(cleaned_content)
    # ... lưu article với summary này
    ```

## 3. Chuyển văn bản thành Giọng nói (Text-to-Speech - TTS) (Sprint 3)

### 3.1. Mục tiêu

Cho phép người dùng nghe nội dung bài báo (hoặc tóm tắt) thay vì đọc, tăng cường trải nghiệm đa phương tiện và khả năng tiếp cận.

### 3.2. Công nghệ: Google Text-to-Speech API

Chúng ta sẽ tích hợp Google Text-to-Speech API vì đây là một giải pháp chất lượng cao, dễ sử dụng và có hỗ trợ tiếng Việt tốt.

#### Hướng dẫn Tích hợp:

1.  **Thiết lập Google Cloud Project:**
    *   Tạo một dự án trên Google Cloud Console.
    *   Kích hoạt Google Cloud Text-to-Speech API.
    *   Tạo một Service Account Key (JSON file) và tải về. Đặt file này ở một nơi an toàn trong dự án (ví dụ: `news_agg_project/google_credentials.json`).
    *   Đặt biến môi trường `GOOGLE_APPLICATION_CREDENTIALS` trỏ đến đường dẫn của file JSON này.

2.  **Cài đặt thư viện Google Cloud:**

    ```bash
    pip install google-cloud-texttospeech
    ```

3.  **Tạo service TTS:** Tạo file `news_app/services/tts.py`.

    ```python
    # news_app/services/tts.py

    from google.cloud import texttospeech
    import os

    # Đảm bảo biến môi trường GOOGLE_APPLICATION_CREDENTIALS đã được thiết lập
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/google_credentials.json"

    client = texttospeech.TextToSpeechClient()

    def synthesize_speech(text, lang_code="vi-VN", voice_name="vi-VN-Wavenet-A", output_filename="output.mp3"):
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code,
            name=voice_name, # Chọn giọng phù hợp, ví dụ: vi-VN-Wavenet-A, vi-VN-Standard-A
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE # hoặc MALE
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        # Lưu audio vào file
        with open(output_filename, "wb") as out:
            out.write(response.audio_content)
            print(f\'Audio content written to file {output_filename}\'')
        return output_filename
    ```

4.  **Tích hợp vào Django:**
    *   Khi người dùng yêu cầu nghe bài báo, một API endpoint (ví dụ: `/api/article/<id>/speak/`) sẽ được gọi.
    *   Endpoint này sẽ gọi `synthesize_speech` với nội dung bài báo (hoặc tóm tắt) và trả về file MP3 hoặc URL đến file MP3 đã được lưu trữ (ví dụ: trên S3).
    *   Để tránh tạo lại file audio mỗi lần, bạn nên lưu trữ file audio đã tạo và chỉ tạo lại khi nội dung bài báo thay đổi.

## 4. Xử lý Hình ảnh (Sprint 4)

### 4.1. Mục tiêu

Đảm bảo mỗi bài báo hiển thị trên giao diện "lướt tin" đều có một hình ảnh đi kèm, tăng tính hấp dẫn và trực quan.

### 4.2. Cơ chế xử lý

1.  **Ưu tiên hình ảnh từ bài báo gốc:** Trong quá trình crawl, crawler sẽ cố gắng bóc tách URL của hình ảnh chính hoặc hình ảnh nổi bật nhất trong bài viết và lưu vào trường `image_url` trong model `Article`.

2.  **Giải pháp thay thế khi không có hình ảnh (Miễn phí/Tiết kiệm chi phí):**
    *   **Hình ảnh mặc định theo chuyên mục:** Chuẩn bị một bộ hình ảnh chất lượng cao, phù hợp với từng chuyên mục (ví dụ: hình ảnh về máy tính cho chuyên mục Công nghệ, hình ảnh về thị trường cho Kinh tế). Khi một bài báo không có hình ảnh gốc, hệ thống sẽ tự động gán URL của hình ảnh mặc định tương ứng với chuyên mục của bài báo đó.
    *   **Thư viện tạo ảnh đơn giản:** Sử dụng các thư viện Python như `Pillow` để tạo ra các hình ảnh đơn giản với tiêu đề bài báo hoặc tên chuyên mục làm text. Đây là một giải pháp miễn phí nhưng hình ảnh có thể không quá bắt mắt.

#### Hướng dẫn Tích hợp:

1.  **Cập nhật Model `Article`:** Thêm trường `image_url` để lưu trữ URL hình ảnh.

    ```python
    # news_app/models.py
    class Article(models.Model):
        # ... các trường khác
        image_url = models.URLField(max_length=500, blank=True, null=True)
    ```

2.  **Cập nhật Crawler:** Trong quá trình bóc tách nội dung, tìm kiếm thẻ `<img>` đầu tiên hoặc thẻ `meta property="og:image"` để lấy URL hình ảnh.

    ```python
    # Trong hàm handle() của crawler
    # ...
    soup = BeautifulSoup(html_content, \'html.parser\')
    # Ví dụ lấy từ meta tag
    og_image_tag = soup.find(\'meta\', property=\'og:image\')
    image_url = og_image_tag[\'content\'] if og_image_tag else None

    # Hoặc từ thẻ img đầu tiên trong nội dung
    if not image_url:
        first_img = soup.find(\'img\')
        if first_img and first_img.get(\'src\'):
            image_url = first_img[\'src\']

    # ... lưu article với image_url này
    ```

3.  **Logic xử lý hình ảnh mặc định/tạo tự động:** Trong `views.py` hoặc một service riêng, khi hiển thị bài báo, nếu `article.image_url` rỗng, hãy gán URL của hình ảnh mặc định theo chuyên mục hoặc gọi hàm tạo ảnh đơn giản.

---

**Tác giả:** Manus AI
**Ngày:** 07/10/2025
