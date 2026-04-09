# Installation Guide: Document Analytics on BigQuery

This project provides a comprehensive solution for analyzing healthcare documents (Clinical Trials, Patient Profiles) using BigQuery's Knowledge Graph capabilities, Gemini LLMs, and Document AI.

## 📋 Prerequisites

Before you begin, ensure you have the following:

1.  **Google Cloud Project:** A project with billing enabled.
2.  **gcloud SDK:** Installed and authenticated.
    *   `gcloud auth login`
    *   `gcloud config set project [YOUR_PROJECT_ID]`
3.  **Permissions:** You need the `Editor` or `Owner` role on the project to enable APIs and create resources.
4.  **Python 3.10+:** Required for running the demonstration notebooks and the new ingestion pipeline parameterization scripts.

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

## ⚙️ Step 2: Unstructured Ingestion Parameterization (NEW!)

Instead of modifying static SQL scripts with complicated escape characters, we now utilize a **Beginner-Friendly Parameterization Engine**.

### 1. Configure the Pipeline
Open `config.yaml` and update the values with your actual GCP details:
```yaml
# Basic Google Cloud Info
project_id: "your-project-id"
dataset_id: "clinical_trial_multiregion"
location: "us"
connection_id: "cloud_ai_resources"

# Input Data Locations
patient_data_gcs_path: "gs://your-bucket-name/patients/*.txt"
clinical_reports_gcs_path: "gs://your-bucket-name/reports/*.pdf"

# Advanced (Optional)
model_name: "cssr_reports_model"
```

### 2. Generate Deployable Stored Procedures
Run the engine script (no external dependencies required):
```bash
python3 scripts/parameterize.py
```
*This will generate `sql/Parameterized_Patient_Profiles.sql` and `sql/Parameterized_Clinical_Trials.sql`.*

### 3. Deploy the Procedures to BigQuery
The `quick-install.sh` handles this automatically, but to deploy them manually:
```bash
bq query --use_legacy_sql=false < sql/Parameterized_Patient_Profiles.sql
bq query --use_legacy_sql=false < sql/Parameterized_Clinical_Trials.sql
```

---

## 📊 Step 3: BigQuery & IAM Configuration

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

## 💾 Step 4: Data Layer & Table Creation

The script then performs the following data tasks:

1.  **AVRO Loading:** Loads all 20 tables from `sql/tables/*.avro` into the `clinical_trial` dataset.
2.  **Unstructured Data Ingestion:**
    *   Uploads patient profiles to the `${PROJECT_ID}-patient-profiles` bucket.
    *   Uploads clinical trial PDFs to the `${PROJECT_ID}-clinical-trials-docs` bucket.

---

## 🔍 Step 5: Orchestrate Analysis Layer (SQL)

Once the Data layer is created, we use an orchestration simulation to trigger the Unstructured Pipelines created in Step 2:

```bash
# Set up a virtual environment (optional) and install google-cloud-bigquery
pip install google-cloud-bigquery

# Orchestrate the procedures (this runs the actual ingestion on BQ!)
python3 scripts/orchestrate_ingestion.py
```

Finally, we construct the graph structure using:
*   `sql/Clinical TRial Denormalized Data.sql`
*   `sql/setup_clinical_trial_graph.sql`

---

## 📓 Step 6: Interaction Layer (Notebooks)

The `notebooks/` directory contains Jupyter notebooks that demonstrate the platform's capabilities.

### Key Notebooks:
*   **`Bigquery_knowledge_graph_demo.ipynb`**: Shows how to construct and query a Knowledge Graph from unstructured data.
*   **`clinical_trials_graph_demo.ipynb`**: Demonstrates semantic search and graph traversal for finding clinical trials.

### How to Run:
1.  **Vertex AI Workbench:** Upload the notebooks to a Vertex AI Workbench instance in your project.
2.  **Local Jupyter:** Run `pip install -r requirements.txt` (if available) or install `google-cloud-bigquery` and `google-cloud-storage`, then start your local server.
3.  **Google Colab:** Open the notebooks directly in Colab and follow the authentication prompts.

