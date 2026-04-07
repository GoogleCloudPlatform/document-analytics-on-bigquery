# Installation Guide: Document Analytics on BigQuery

This project provides a comprehensive solution for analyzing healthcare documents (Clinical Trials, Patient Profiles) using BigQuery's Knowledge Graph capabilities, Gemini LLMs, and Document AI.

## 📋 Prerequisites

Before you begin, ensure you have the following:

1.  **Google Cloud Project:** A project with billing enabled.
2.  **gcloud SDK:** Installed and authenticated.
    *   `gcloud auth login`
    *   `gcloud config set project [YOUR_PROJECT_ID]`
3.  **Permissions:** You need the `Editor` or `Owner` role on the project to enable APIs and create resources.
4.  **Python 3.10+:** Required for running the demonstration notebooks.

---

## 🚀 Step 1: Quick Infrastructure Setup

We provide a `quick-install.sh` script to automate the provisioning of APIs, storage buckets, and BigQuery datasets.

### 1. Make the script executable:
```bash
chmod +x quick-install.sh
```

### 2. Run a Dry Run (Recommended):
By default, the script only prints the commands it *would* execute. This allows you to review the infrastructure changes before they happen.
```bash
./quick-install.sh
```

### 3. Execute the Installation:
Once you have reviewed the output, run the script with the `--execute` flag to apply changes to your GCP project.
```bash
./quick-install.sh --execute
```

---

## 📊 Step 2: BigQuery & IAM Configuration

The `quick-install.sh` script automates the following BigQuery and IAM tasks:

1.  **BigQuery Connections:**
    *   Creates `llm-connection` (us-central1) for Gemini and Embedding models.
    *   Creates `cloud_ai_resources` (us) for Document AI models.
2.  **IAM Permissions:**
    *   Automatically identifies the service accounts associated with these connections.
    *   Grants `roles/aiplatform.user`, `roles/storage.objectUser`, and `roles/documentai.viewer` to ensure models can interact with Google's AI services and GCS data.
3.  **Remote Models:**
    *   Creates `EmbeddingsModel` (text-embedding-005).
    *   Creates `LLMModel` (gemini-2.5-pro).
    *   Creates `cssr_reports_model` (Document AI Layout Parser).
4.  **Property Graph:**
    *   Defines the `clinical_trial.DrugGraph` which maps Trials, Drugs, Disorders, and Mechanisms of Action into a searchable graph structure.

---

## 💾 Step 3: Data Layer & Table Creation

The script then performs the following data tasks:

1.  **AVRO Loading:** Loads all 20 tables from `sql/tables/*.avro` into the `clinical_trial` dataset.
2.  **Unstructured Data Ingestion:**
    *   Uploads patient profiles to the `${PROJECT_ID}-patient-profiles` bucket.
    *   Uploads clinical trial PDFs to the `${PROJECT_ID}-clinical-trials-docs` bucket.

---

## 🔍 Step 4: Analysis Layer (SQL)

To generate the denormalized view or run sample graph queries, the script executes:
*   `sql/Clinical TRial Denormalized Data.sql`
*   `sql/setup_clinical_trial_graph.sql` (to provision the graph schema)

---

## 📓 Step 5: Interaction Layer (Notebooks)

The `notebooks/` directory contains Jupyter notebooks that demonstrate the platform's capabilities.

### Key Notebooks:
*   **`Bigquery_knowledge_graph_demo.ipynb`**: Shows how to construct and query a Knowledge Graph from unstructured data.
*   **`clinical_trials_graph_demo.ipynb`**: Demonstrates semantic search and graph traversal for finding clinical trials.

### How to Run:
1.  **Vertex AI Workbench:** Upload the notebooks to a Vertex AI Workbench instance in your project.
2.  **Local Jupyter:** Run `pip install -r requirements.txt` (if available) or install `google-cloud-bigquery` and `google-cloud-storage`, then start your local server.
3.  **Google Colab:** Open the notebooks directly in Colab and follow the authentication prompts.

---

## 🛠️ Troubleshooting

*   **Bucket Name Collisions:** GCS bucket names must be globally unique. If the script fails during bucket creation, ensure your `PROJECT_ID` prefix makes them unique.
*   **Quota Limits:** If enabling APIs fails, check your project's quota limits in the Google Cloud Console.
*   **Authentication:** If you receive "Access Denied" errors, re-run `gcloud auth application-default login`.
