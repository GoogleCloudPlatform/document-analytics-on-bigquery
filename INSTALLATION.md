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

## 📊 Step 2: Data Layer & Table Creation

The `quick-install.sh` script automatically performs the following data tasks:

1.  **AVRO Loading:** Loads `sql/tables/TrialStatus.avro` into the `clinical_trial.TrialStatus` table.
2.  **Unstructured Data Ingestion:**
    *   Uploads patient profile text files from `data/generated_patient_profiles/` to the `${PROJECT_ID}-patient-profiles` bucket.
    *   Uploads clinical trial PDF reports from `data/generated_clinical_trials_reports/new/` to the `${PROJECT_ID}-clinical-trials-docs` bucket.

---

## 🔍 Step 3: Analysis Layer (SQL)

To generate the denormalized view of the clinical trials data, you can run the SQL query provided in the repository. This query joins the trials, drugs, and disorders into a flat structure for easier analysis.

```bash
bq query --use_legacy_sql=false < sql/"Clinical TRial Denormalized Data.sql"
```

---

## 📓 Step 4: Interaction Layer (Notebooks)

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
