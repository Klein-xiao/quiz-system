[中文](README.md) | [English](README_EN.md)
# 📝 Smart Quiz & Mistake Note System

An efficient quiz practice and mistake management system built with Vue 3 + Element Plus on the frontend and Python on the backend. It supports PDF question bank parsing and importing, Excel/CSV answer matching, automatic detection and verification for single/multiple-choice questions, and targeted mistake review.

---
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=flat&logo=vuedotjs&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
---
## 📸 Demo
<img width="1628" height="954" alt="image" src="https://github.com/user-attachments/assets/65412de2-e839-41fe-9511-9be5ad4cd845" />


## ✨ Features

- **📄 PDF Question Bank Parsing**: Upload PDF question banks with real-time log tracking for parsing and importing progress.
- **✅ Excel/CSV Answer Matching**: Upload answer sheets in Excel or CSV format for automatic question-number matching.
- **🔘 Smart Single & Multiple Choice Detection**: Automatically switches between single-choice (Radio) and multiple-choice (Checkbox) modes based on answer format, supporting unordered letter comparison.
- **📋 Batch Mistake Import**: Quickly input question numbers (separated by newlines, commas, or spaces) to generate customized mistake sets.
- **👁️ Flexible Answer Visibility**:
  - Global toggle to show/hide correct answers and correctness status.
  - Mistake collections hide answers by default, offering single-item "Show Answer" as well as batch toggles.
- **⚡ 60-Item High-Performance Pagination**: Smoothly handles large question sets (60 items per page) with quick scroll-to-top functionality.

---

## 🛠️ Tech Stack

- **Frontend**: Vue 3 (Composition API), Element Plus, Axios, HTML5/CSS3
- **Backend**: Python (FastAPI / Flask), PyPDF2 / pdfplumber, Pandas / OpenPyXL
- **Data Storage**: SQLite / JSON file storage

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/quiz-system.git](https://github.com/your-username/quiz-system.git)
cd quiz-system
```
### 2. Backend Setup & Run
```bash
# Navigate to the backend directory (if applicable)
cd backend

# Install dependencies
pip install -r requirements.txt

# Run backend service (FastAPI example)
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
Directly open frontend/index.html in your browser, or serve it via a local HTTP server (such as VS Code Live Server or Python's http.server).

📖 Usage Guide
1. Upload Question Bank: Click the [Upload PDF] button at the top and wait for the parsing process to complete.

2. Import Answer Sheet: Click [Upload Answers] to upload the corresponding Excel or CSV file.

3. Practice Mode:

- Practice questions in the "All Questions" tab. Toggle the switch at the top to enable real-time answer verification.

- Click [Add to Mistake Book] for any incorrectly answered questions.

4. Mistake Review:

- Switch to the "Mistake Review" tab for targeted practice.

- Use [📋 Batch Import Mistakes] to import a custom list of question numbers.

- Click [Mark as Mastered] to remove resolved questions from the mistake collection.
