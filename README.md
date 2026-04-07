# Healthcare Document Analytics Solution: Zero-Copy RAG & Knowledge Graph

## Overview
This solution provides a comprehensive, agentic framework for analyzing healthcare documents—specifically Clinical Study Summary Reports (CSSR)—using a "Zero-Copy RAG" architecture on Google Cloud. It leverages BigQuery as the central data and AI orchestration engine, integrating Document AI, Vertex AI (Gemini), and BigQuery Graph to transform unstructured PDF reports into a structured, searchable, and relational Knowledge Graph.

## Key Architectural Pillars: The Zero-Copy RAG
Traditional RAG (Retrieval-Augmented Generation) often requires moving data between silos (extracting text, sending to an external vector DB, then to an LLM). This solution implements **Zero-Copy RAG**, where:
1.  **Data Stays in BigQuery:** PDF documents are stored in Google Cloud Storage and exposed to BigQuery via **Object Tables**.
2.  **In-Warehouse Processing:** 
    *   **Document AI Integration:** BigQuery uses `ML.PROCESS_DOCUMENT` to chunk and parse PDFs without moving the data.
    *   **Generative Extraction:** `ML.GENERATE_TEXT` (utilizing Gemini models via BQML Remote Connections) extracts structured entities (Sponsor, Phase, NCT Number, etc.) directly from the document content.
3.  **Seamless Joinery:** Extracted data is immediately joined with existing structured clinical datasets in BigQuery, creating a "Golden Record" in the `ClinicalTrialMasterData` table.

## Solution Components

### 1. Data Ingestion & Parsing (`sql/`)
*   **External Object Tables:** Unified access to PDF reports in GCS.
*   **Integrated DocAI:** Automated chunking and layout analysis.
*   **Gemini-Powered Extraction:** High-fidelity extraction of complex clinical fields using the latest Gemini models (2.5 Pro/Flash).

### 2. Clinical Knowledge Graph (`sql/setup_clinical_trial_graph.sql`)
The solution constructs a **BigQuery Property Graph** to map the complex ecosystem of clinical research:
*   **Nodes:** Trial, Drug, Disorder, Mechanism of Action (MOA), Company, Phase, Status, Criteria.
*   **Relationships:** 
    *   `Drug` -> `MayTreat` -> `Disorder`
    *   `Trial` -> `Uses` -> `Drug`
    *   `Drug` -> `HasMechanismOfAction` -> `MOA`
    *   `Disorder` -> `IsSubtypeOf` -> `Disorder` (Hierarchy)

### 3. Agentic Synthetic Data Generation (`gemini-cli-plans/`)
To support development and testing, the solution includes reusable **Gemini CLI Plans** for:
*   **Synthetic CSSR Generation:** Creating multi-page, 15-section clinical protocols that simulate real-world data.
*   **Patient Profile Generation:** Creating synthetic medical records (eligible and ineligible) to test trial matching logic.

### 4. Knowledge Graph Exploration (`notebooks/`)
Interactive Jupyter notebooks demonstrate:
*   Querying the Property Graph using GQL (Graph Query Language).
*   Visualizing relationships between therapeutic areas and drugs.
*   Performing semantic search across clinical trials.

## Prerequisites
*   Google Cloud Project with BigQuery, Vertex AI, and Document AI enabled.
*   BigQuery Remote Connections configured for LLM and Embedding models.
*   Gemini CLI (for running synthetic data generation plans).

## Repository Structure
*   `sql/`: BigQuery DDL, DML, and BQML scripts for parsing and graph construction.
*   `notebooks/`: End-to-end demonstrations and visualization of the clinical graph.
*   `data/`: Local storage for generated synthetic PDFs and text profiles.
*   `gemini-cli-plans/`: Standardized workflows for agentic data synthesis.
