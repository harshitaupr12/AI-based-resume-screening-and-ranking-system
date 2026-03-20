# 🚀 AI Resume Screening & Ranking System

An AI-powered resume screening system that automates candidate evaluation, ranking, and shortlisting based on a given job description.

---

## 📌 Overview

This project simulates a lightweight Applicant Tracking System (ATS) that helps recruiters efficiently filter and rank candidates. It processes multiple resumes, evaluates them against a job description (JD), and generates structured insights for decision-making.

---

## ⚙️ Key Features

- 📄 Extracts text from PDF resumes  
- 🧠 Intelligent keyword-based matching with weighted scoring  
- 📊 Generates match score (0–100) for each candidate  
- 🏆 Ranks candidates based on relevance to the job description  
- ✅ Identifies top **Strengths** (2–3 key matching skills)  
- ❌ Highlights **Gaps** (2–3 missing skills)  
- 🎯 Provides final recommendation:
  - Strong Fit  
  - Moderate Fit  
  - Not Fit  
- 📈 Category-wise scoring (AI/ML, Backend, Frontend, Data, etc.)  
- 🧾 Candidate profiling (email, phone, experience estimation)  
- 📊 Interactive CLI dashboard with visual progress bars  
- 📥 Exports results to CSV for further analysis  

---

## 🧠 How It Works

1. **Input**:
   - Job Description (JD)
   - Multiple resumes (PDF format)

2. **Processing**:
   - Extracts text from resumes using PyPDF2  
   - Cleans and tokenizes text  
   - Extracts keywords from JD  
   - Matches resume skills with weighted scoring  
   - Calculates match score and identifies strengths & gaps  
   - Applies ranking and recommendation logic  

3. **Output**:
   - Candidate ranking  
   - Match scores  
   - Strengths & gaps  
   - Final recommendation  
   - CSV report  

---

## 🛠️ Tech Stack

- **Python**
- **PyPDF2** (PDF parsing)
- **Regular Expressions (re)** (text processing)
- **CLI-based interface** (structured output)
- Basic NLP logic (keyword extraction & matching)

---

## ▶️ How to Run

```bash
# Clone the repository
git clone https://github.com/your-username/AI-based-resume-screening-and-ranking-system.git

# Navigate to the project folder
cd AI-based-resume-screening-and-ranking-system

# Install dependencies
pip install PyPDF2

# Run the system
python main.py
