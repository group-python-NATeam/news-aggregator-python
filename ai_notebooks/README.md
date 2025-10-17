## AI Notebooks – Ghi chép huấn luyện mô hình PhoBERT

## Mục tiêu
Lưu trữ các notebook, mô hình, log và kết quả huấn luyện AI (đặc biệt là các lần fine-tune PhoBERT).
---
## Issue #9 - Chuẩn bị môi trường & dữ liệu
- Cài đặt thư viện cần thiết (transformers, torch, scikit-learn)
- Tiền xử lý dữ liệu
- Label encoding
- Tokenization bằng PhoBERT
⇒ Tải PhoBERT model và tokenizer thành công!
## Issue #10 - Huấn luyện & đánh giá mô hình
Train model PhoBERT với 8 nhãn
##  Cấu trúc thư mục
ai_notebooks/
├── models/ # Lưu các mô hình đã train (.zip hoặc thư mục)
├── logs/ # Lưu file log, metrics hoặc csv
├── notebooks/ # Lưu các notebook (.ipynb)
└── README.md # File ghi chép kết quả, thông số và nhận xét

---

## Model Information
- **Base model**: vinai/phobert-base-v2
- **Number of labels**: 8
- **Dataset**: labeled_data.csv
- **Text column**: text
- **Label column**: category
- **Data split**: 80% train – 20% test (stratified by label)

---

## Hyperparameters

| Tham số | Giá trị |
|---------|---------|
| Epochs | 4 |
| Batch size | 8 |
| Learning rate | 5e-5 |
| Max sequence length | 256 |
| Optimizer | AdamW |
| Loss function | CrossEntropyLoss |
| Evaluation strategy | epoch |
| Random seed | 42 |

---

## Training Results

### Run 1 (2025-10-12)
- **Accuracy (test)**: 0.8421
- **F1-score**: 0.8201
- **Train Loss**: 1.2943
- **Val Loss**: 1.0947

### Run 2 (2025-10-12) - Best Model
- **Accuracy (test)**: 0.8771 ✅
- **F1-score**: 0.8752 ✅
- **Train Loss**: 0.1433
- **Val Loss**: 0.5741

> **Note**: Run 2 achieved the best results with accuracy **0.8771** and F1-score **0.8752**, exceeding the target of ≥ 0.50.

---

## Label Mapping
```python

label2id = {
    # 'cong-nghe': 0, 
    # 'kinh-te': 1, 
    # 'giao-duc': 2, 
    # 'giai-tri': 3, 
    # 'suc-khoe': 4, 
    # 'the-thao': 5, 
    # 'phap-luat': 6, 
    # 'xa-hoi': 7
}

id2label = {
    # 0: 'cong-nghe', 
    # 1: 'kinh-te', 
    # 2: 'giao-duc', 
    # 3:'giai-tri', 
    # 4: 'suc-khoe', 
    # 5: 'the-thao', 
    # 6: 'phap-luat', 
    # 7: 'xa-hoi'
}

** Nhận xét: **  
- Accuracy (test):  0.8 > 0.5 ⇒ đạt yêu cầu đặt ra.  
- Mô hình có xu hướng hội tụ ổn định từ epoch 2–4.  
- Có thể thử điều chỉnh “learning_rate” hoặc “max_length” để cải thiện thêm.
- Mô hình lưu tại: “my-finetuned-phobert/”

---

##  Lưu trữ mô hình

**Đường dẫn model (trên Google Drive):**


