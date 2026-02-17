# GenAI Verification System

A Python-based verification framework that combines rule engines and machine learning to perform document and data verification tasks.  
This system can be extended for compliance checks, document classification, loan verification, RBI compliance evaluation, and similar automated validation workflows.

---

## 🧠 Overview

The **GenAI Verification System** is designed to:

- 📄 Extract and classify information from structured and unstructured data
- 📋 Apply business-level rules for compliance and validation
- 🤖 Combine human logic and machine learning for intelligent decision making
- 📊 Generate verification reports

⚙️ The project is modular — components like extractors, classifiers, and rule engines can be reused in other workflows.

---

## 📂 Repository Structure
├── app.py # Main application entrypoint
├── run.py # Script to run/execute workflows
├── aadhaar_extractor.py # Module to extract data from Aadhaar documents
├── loan_extractor.py # Loan info extractor logic
├── document_classifier.py # Classifier for document types
├── rbi_compliance_analyst.py # RBI compliance check logic
├── verify_loan_ltv.py # Loan LTV verification logic
├── verification_report.py # Report generation code
├── consensus.py # Consensus/decision aggregator
├── rules_engine/ # Directory containing business rule definitions
├── data/ # Sample/placeholder data
├── llm_models/ # Pretrained or custom language models
├── ocr/ # OCR models or configuration
├── tests/ # Unit tests
│ ├── test_model_b.py
│ └── test_policy_rules.py
├── requirements.txt # Python dependencies
└── README.md # (This file)


---

## 🚀 Features

### 🔍 Document Extraction
Extract specific fields (e.g., Aadhaar data, loan details) from documents using OCR + custom logic.

### 🧠 Classification
Classify input data using machine learning models to determine document types or categories.

### 📜 Rule-Based Validation
Business logic and policy checks are implemented via a rules engine (in `rules_engine/`).

### 🧮 Decision Aggregation
Combine multiple model outputs and rules for a more confident verification result.

### 📊 Reporting
Generate verification reports for audit or downstream processing.

---

## 💻 Installation

Make sure you have **Python 3.8+** installed.

1. Clone the repository:

   ```bash
   git clone https://github.com/gautam-rahul-09/genai_verification_system.git
