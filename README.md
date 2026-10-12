# 📚 Study Analyzer

**Study Analyzer** is a personal academic analytics and productivity application designed to help engineering students prepare for semester examinations, maintain consistent daily study habits, and strengthen independent Python problem-solving skills.

The application runs **100% locally on Windows 11** using Streamlit, SQLite, Pandas, and Plotly. It requires no cloud subscriptions, external APIs, or account logins.

---

## 🎯 Key Features

- **Pre-Configured 7th Semester Subjects**: Pre-seeded with 5 core & elective subjects and their detailed 5-unit curriculum:
  1. `BCS714D`: **Big Data Analytics** (Professional Elective-4, Exam: **Nov 17, 2026** • 2:00 PM – 5:00 PM)
  2. `BME755D`: **Non-Conventional Energy Resources** (Open Elective-5, Exam: **Nov 19, 2026** • 2:00 PM – 5:00 PM)
  3. `BCS701`: **Internet of Things (IoT)** (Core, Exam: **Nov 24, 2026** • 2:00 PM – 5:00 PM)
  4. `BCS702`: **Parallel Computing** (Core, Exam: **Nov 26, 2026** • 2:00 PM – 5:00 PM)
  5. `BCS703`: **Cryptography & Network Security** (Core, Exam: **Nov 30, 2026** • 2:00 PM – 5:00 PM)
- **Examination Countdown & Urgency Engine**: Live countdown timer for upcoming examinations with urgency sorting.
- **Daily Planner & Smart Scheduler**: Schedule study sessions, track task categories, resolve overdue tasks, and generate prioritized study schedules.
- **Syllabus & Topic Tracker**: Track completion percentages across all units, rate topic confidence (1–5), and flag weak concepts for revision.
- **Actual Study Session Logger**: Distinguish between planned time and actual logged study hours with subject and date filters.
- **Test Performance Analytics**: Record mock tests and quizzes, calculate individual, arithmetic average, and weighted overall percentages, and visualize score trends.
- **Python Practice Tracker**: Track problems attempted, solved, and independently solved without viewing solutions; log hints used and concept breakdowns (Strings, Lists, Recursion, OOP, etc.).
- **Weekly Analytics & Comparison**: 7-day comparative reports against previous periods with study consistency metrics.
- **Data Safety & Backup/Restore**: Atomic database backup export and schema-validated restoration.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.11+ is installed.

### 2. Install Dependencies
Install all required libraries from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
Run Streamlit from the project directory:
```bash
streamlit run app.py
```
The application will open automatically in your browser at `http://localhost:8501`.

---

## 📁 Project Structure

```text
Study_Analyzer/
├── app.py                     # Main dashboard entry point & overview metrics
├── database.py                # SQLite schema, migrations, CRUD helpers, backup/restore
├── analytics.py               # Statistical calculations, consistency, and aggregations
├── recommendations.py         # Transparent, rule-based recommendation engine
├── requirements.txt           # Project dependencies
├── README.md                  # Documentation and usage guide
├── .gitignore                 # Ignores database files, virtual environments, cache
├── components/
│   ├── sidebar.py             # Live exam countdown & target settings sidebar
│   ├── metrics.py             # Dark developer-themed UI metric cards
│   └── charts.py              # Interactive Plotly dark-theme visual charts
├── pages/
│   ├── 1_Daily_Planner.py     # Task scheduling, priority planner & overdue tracking
│   ├── 2_Subjects_and_Topics.py # Syllabus tree, topic confidence & exam date editor
│   ├── 3_Study_Log.py         # Actual study time logging & session history
│   ├── 4_Test_Performance.py   # Test marks tracking & weighted score analytics
│   ├── 5_Python_Practice.py   # Problem solving, independent solve rate & concept charts
│   └── 6_Weekly_Analytics.py   # 7-day comparative reports & database backup/restore
├── tests/
│   ├── test_database.py       # Automated tests for database CRUD and constraints
│   └── test_analytics.py      # Automated tests for formulas and edge cases
└── data/
    └── study_analyzer.db      # Local SQLite database (created automatically on first run)
```

---

## 🧪 Running Automated Tests

To run the complete test suite:
```bash
python -m pytest -v
```
All tests run against an isolated temporary SQLite database and will never alter your real study records.

---

## 💾 Backup and Data Safety

- Your database is located at `data/study_analyzer.db`.
- To export a backup, navigate to **Weekly Analytics & Backup** (`pages/6_Weekly_Analytics.py`), select the **Database Backup & Restore** tab, and click **Download Database Backup (.db)**.
- To restore records on a new machine, upload your `.db` file in the same tab. The system validates the schema integrity before restoring.

---

## ⚙️ Troubleshooting & Notes

- **Port in use**: If port 8501 is occupied, launch on a specific port: `streamlit run app.py --server.port 8502`.
- **Exam Dates**: Exam dates can be adjusted at any time under **Subjects & Topics > Manage Subjects & Exam Dates**.
