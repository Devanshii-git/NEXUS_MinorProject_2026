# Sutrava
**NEXUS_MinorProject_2026**

An AI-Driven System for Automated Requirements Engineering from Unstructured Stakeholder Communication.

Sutrava fundamentally transforms the software requirement gathering lifecycle by autonomously extracting, classifying, and structuring requirements from unrefined communication channels, including email correspondence, Slack interactions, Jira tickets, and meeting transcripts. 

## Key Features

- **AI-Powered NLP Pipeline**: Leverages a fine-tuned DistilBERT architecture for rapid requirement detection and a spaCy + BERT transformer ecosystem for Named Entity Recognition (NER).
- **Cross-Platform Desktop Application**: A sophisticated, cross-platform client built on the Electron framework, fortified with React and Tailwind CSS for seamless user experience.
- **Backend Orchestration**: Driven by a robust Spring Boot REST API that seamlessly manages external communications, integrated directly with Atlassian OAuth2 and Jira API endpoints.
- **Interactive Dashboards**: Advanced visual interfaces designed to analyze extracted requirements, contextual clusters, prioritization levels, and automatically export structured Software Requirement Specification (SRS) documentation.

## Project Architecture

```text
NEXUS_MinorProject_2026-main/
├── model/                     # AI Pipeline (Python, PyTorch, Transformers, spaCy)
│   ├── requirement_classifier/# DistilBERT binary classifier (Req / Not Req)
│   ├── ner_model/             # Named Entity Recognition (spaCy 3 + BERT)
│   ├── clustering/            # Sentence embeddings & clustering
│   ├── prioritization/        # Priority level classification
│   └── inference_pipeline/    # End-to-end processing pipeline
│
├── Sutrava_Frontend/          # Desktop Application (Electron + React + Vite)
│   ├── electron/              # Electron main process scripts
│   ├── src/                   # React frontend source code
│   └── package.json           # Frontend dependencies and build scripts
│
├── Phase-1/                   # Project Planning & Proposals
│   ├── Minor Project Proposal.pdf
│   ├── Project Synopsis-Report-Final.pdf
│   ├── Updated_Proposal.pdf
│   ├── Project_form_Nexus .pdf
│   └── PERT CHART.drawio.png
│
├── Phase-2/                   # System Development & Backend
│   ├── BackEnd/               # Spring Boot RESTful API & Jira Integrations
│   ├── Project SRS-Report.docx
│   └── README.md
│
└── requirements.txt           # Core Python dependencies for the AI models
```

*(Note: Presentation materials have been omitted from this tree for brevity).*

## Technology Stack

- **Frontend Environment**: React, Electron, Vite, Tailwind CSS, Framer Motion, Lucide React
- **Backend Environment**: Java, Spring Boot, REST API, Atlassian/Jira Integration
- **Artificial Intelligence**: Python, PyTorch, HuggingFace Transformers, spaCy, scikit-learn, Sentence-Transformers

## Installation & Setup Guide

### 1. AI Model Initialization
Ensure you are located at the root directory, then install the core Python dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```
*(Consult `model/README.md` for extended guidelines on training methodologies and executing the inference pipeline).*

### 2. Desktop Application Configuration
Navigate to the frontend directory to initialize the user interface:
```bash
cd Sutrava_Frontend
npm install
```
To launch the application in development mode:
```bash
npm run electron:dev
```
To compile a production-ready build:
```bash
npm run electron:build
```

### 3. Backend Services Setup
Navigate to the `Phase-2/BackEnd` directory to configure application properties, define Atlassian OAuth credentials, and instantiate the Spring Boot server environment via Maven or your preferred Java IDE.

