<div align="center">
  <h1>Sutrava</h1>
  <p><strong>Built By Team NEXUS</strong></p>
  <p><em>An AI-Driven System for Automated Requirements Engineering from Unstructured Stakeholder Communication.</em></p>

  <p align="center">
    <a href="https://reactjs.org/"><img src="https://img.shields.io/badge/Frontend-React%20%2B%20Electron-61DAFB?style=flat-square&logo=react" alt="React"></a>
    <a href="https://spring.io/projects/spring-boot"><img src="https://img.shields.io/badge/Backend-Spring%20Boot-6DB33F?style=flat-square&logo=springboot" alt="Spring Boot"></a>
    <a href="https://pytorch.org/"><img src="https://img.shields.io/badge/AI_Engine-PyTorch%20%2B%20Transformers-EE4C2C?style=flat-square&logo=pytorch" alt="PyTorch"></a>
  </p>
</div>

<hr/>

## Overview

**Sutrava** fundamentally transforms the software requirement gathering lifecycle by autonomously extracting, classifying, and structuring requirements from unrefined communication channels. Whether dealing with email correspondence, Slack interactions, Jira tickets, or meeting transcripts, Sutrava distills unstructured data into actionable, structured Software Requirement Specification (SRS) documentation.

## Key Features

- **AI-Powered NLP Pipeline**: 
  - Leverages a fine-tuned **DistilBERT** architecture for rapid requirement detection.
  - Employs a **spaCy + BERT** transformer ecosystem for Named Entity Recognition (NER).
- **Cross-Platform Desktop Application**: 
  - A sophisticated client built on the **Electron** framework.
  - Fortified with **React** and **Tailwind CSS** for a seamless, interactive user experience.
- **Backend Orchestration**: 
  - Driven by a robust **Spring Boot REST API**.
  - Seamlessly manages external communications, directly integrated with **Atlassian OAuth2** and **Jira API** endpoints.
- **Interactive Dashboards**: 
  - Advanced visual interfaces to analyze extracted requirements, contextual clusters, and prioritization levels.
  - Automatically exports structured Software Requirement Specification (SRS) documentation.

## System Architecture

Sutrava operates through a microservice-like architecture spanning an AI inference engine, a robust Java backend, and an interactive desktop client.

```text
NEXUS-Sutrava-main/
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
│   └── package.json           # Frontend dependencies & build scripts
│
├── BackEnd/                   # Spring Boot RESTful API & Integrations
│   ├── src/                   # Java Source Code
│   ├── pom.xml                # Maven dependencies
│   └── Dockerfile             # Containerization config
│
├── Reports/                   # Project Planning & Documentation
│   ├── Project Synopsis-Report-Final.pdf
│   └── Project SRS-Report.docx
│
└── Research Papers/           # Research, Formats, and Papers
    └── Sutrava_Research_Paper.pdf (and related materials)
```

## Technology Stack

### Artificial Intelligence & Data Science
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![Transformers](https://img.shields.io/badge/HuggingFace-FFD21E?style=flat-square&logo=huggingface&logoColor=black)
![spaCy](https://img.shields.io/badge/spaCy-09A3D5?style=flat-square&logo=spacy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit_learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)

### Backend Environment
![Java](https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat-square&logo=spring-boot&logoColor=white)
![Atlassian](https://img.shields.io/badge/Jira_API-0052CC?style=flat-square&logo=jira&logoColor=white)

### Frontend Environment
![React](https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![Electron](https://img.shields.io/badge/Electron-191970?style=flat-square&logo=electron&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-B73BA5?style=flat-square&logo=vite&logoColor=FFD62E)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)

---

## Installation & Setup Guide

### 1. AI Model Initialization

Ensure you are located at the root directory, then install the core Python dependencies:

```bash
cd model
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```
> **Note:** Consult `model/README.md` for extended guidelines on training methodologies, model checkpoints, and executing the inference pipeline.

### 2. Desktop Application Configuration

Navigate to the frontend directory to initialize the user interface:

```bash
cd Sutrava_Frontend
npm install
```

Launch the application in development mode:
```bash
npm run electron:dev
```

To compile a production-ready build:
```bash
npm run electron:build
```

### 3. Backend Services Setup

Navigate to the `BackEnd` directory to configure application properties, define Atlassian OAuth credentials, and instantiate the Spring Boot server environment.

Using Maven Wrapper:
```bash
cd BackEnd
./mvnw spring-boot:run
```

## AI Pipeline Flow

1. **Preprocessing:** Raw text from various sources is cleaned and tokenized.
2. **Requirement Classification:** DistilBERT determines if a sentence is a valid software requirement.
3. **Named Entity Recognition (NER):** Extracts key entities (e.g., *Actor*, *Action*, *System Component*).
4. **Clustering:** Groups related requirements using sentence embeddings.
5. **Prioritization:** Automatically assigns priority levels (High/Medium/Low) based on extracted context.

---
<div align="center">
  <sub>Built by the NEXUS Team for Minor Project 2026.</sub>
</div>
