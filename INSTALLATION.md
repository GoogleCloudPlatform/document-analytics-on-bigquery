# Installation Guide: Document Analytics on BigQuery

This project provides a comprehensive solution for analyzing healthcare documents (Clinical Trials, Patient Profiles) using BigQuery's Knowledge Graph capabilities, Gemini LLMs, and Document AI.

## Guided Installation Tutorial on Cloud Shell

Once all the permissions and data prerequisites are met, you can install these components following the step by step installation guide using the Cloud Shell Tutorial, by clicking the button below.

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://console.cloud.google.com/bigquery?cloudshell=true&cloudshell_git_repo=https://github.com/GoogleCloudPlatform/document-analytics-on-bigquery&cloudshell_tutorial=tutorial.md)

**Note:** If you are working from a forked repository, be sure to update the `cloudshell_git_repo` parameter to the URL of your forked repository for the button link above.

## 📋 Prerequisites

Before you begin, ensure you have the following:

1. **Google Cloud Project:** A project with billing enabled.
2. **gcloud SDK:** Installed and authenticated.
   * `gcloud auth login`
   * `gcloud config set project [YOUR_PROJECT_ID]`
3. **Permissions:** You need the `Editor` or `Owner` role on the project to enable APIs and create resources.
4. **Python 3.10+:** Required for running the demonstration notebooks and the new ingestion pipeline parameterization scripts.

---

## 🚀 Step 1: Quick Infrastructure Setup

We provide a `quick-install.sh` script to automate the provisioning of APIs, storage buckets, and BigQuery datasets. The script uses environment variables to configure your installation.

### 1. Set Environment Variables

You **must** set your Google Cloud Project ID. 

```bash
export PROJECT_ID="your-gcp-project-id"
```

**Optional variables (with their default values):**
```bash
export BIGQUERY_LOCATION="us"
export GCS_LOCATION="us"
export DATASET_ID="clinical_trial_multiregion"
export BUCKET_DOCS="${PROJECT_ID}-clinical-trials-docs"
export BUCKET_PROFILES="${PROJECT_ID}-patient-profiles"
```

### 2. Make the script executable

```bash
chmod +x quick-install.sh
```

### 3. Run a Dry Run (Recommended)
By default, the script only prints the commands it *would* execute. This allows you to review the infrastructure changes before they happen.

```bash
./quick-install.sh
```

### 4. Execute the Installation
Once you have reviewed the output, run the script with the `--execute` flag to apply changes to your GCP project.

```bash
./quick-install.sh --execute
```

---

## ⚙️ Step 2: Unstructured Ingestion Parameterization

The `quick-install.sh` script handles this automatically by generating a `config.yaml` file from your environment variables and running our **Beginner-Friendly Parameterization Engine**.

### Under the Hood / Manual Parameterization (Optional)
If you need to re-run parameterization manually without the full install script:

1. **Verify `config.yaml`**: Ensure the file contains your correct GCP details.
2. **Generate Deployable Stored Procedures**:
Run the engine script (no external dependencies required):

```bash
python3 scripts/parameterize.py
```

*This will generate `sql/Parameterized_Patient_Profiles.sql` and `sql/Parameterized_Clinical_Trials.sql`.*

3. **Deploy the Procedures to BigQuery**:
To deploy them manually to BigQuery:

```bash
bq query --use_legacy_sql=false < sql/Parameterized_Patient_Profiles.sql
bq query --use_legacy_sql=false < sql/Parameterized_Clinical_Trials.sql
```

---

## 📊 Step 3: BigQuery & IAM Configuration

The `quick-install.sh` script automates the following BigQuery and IAM tasks:

1. **BigQuery Connections:**
   * Creates `llm-connection` (us-central1) for Gemini and Embedding models.
   * Creates `cloud_ai_resources` (us) for Document AI models.
2. **IAM Permissions:**
   * Automatically identifies the service accounts associated with these connections.
   * Grants `roles/aiplatform.user`, `roles/storage.objectUser`, and `roles/documentai.viewer` to ensure models can interact with Google's AI services and GCS data.
3. **Remote Models:**
   * Creates `EmbeddingsModel` (text-embedding-005).
   * Creates `LLMModel` (gemini-2.5-pro).
   * Creates `cssr_reports_model` (Document AI Layout Parser).
4. **Property Graph:**
   * Defines the `<DATASET_ID>.DrugGraph` which maps Trials, Drugs, Disorders, and Mechanisms of Action into a searchable graph structure.

---

## 💾 Step 4: Data Layer & Table Creation

The script then performs the following data tasks:

1. **AVRO Loading:** Loads all 20 tables from `sql/tables/*.avro` into the `<DATASET_ID>` dataset.
2. **Unstructured Data Ingestion:**
   * Uploads patient profiles to the `${PROJECT_ID}-patient-profiles` bucket.
   * Uploads clinical trial PDFs to the `${PROJECT_ID}-clinical-trials-docs` bucket.

---

## 🔍 Step 5: Create Models and Graph (BigQuery Studio - SQL)

Finally, we construct the graph structure using:
* `sql/Clinical TRial Denormalized Data.sql`
* `sql/setup_clinical_trial_graph.sql`

Run these SQL code on BigQuery Studio.

---

## 📓 Step 6: Interaction Layer (Notebooks)

The `notebooks/` directory contains Jupyter notebooks that demonstrate the platform's capabilities.

### Key Notebooks
* **`Bigquery_knowledge_graph_demo.ipynb`**: Shows how to construct and query a Knowledge Graph from unstructured data.
* **`clinical_trials_graph_demo.ipynb`**: Demonstrates semantic search and graph traversal for finding clinical trials.

### How to Run
1. **Vertex AI Workbench:** Upload the notebooks to a Vertex AI Workbench instance in your project.
2. **Local Jupyter:** Run `pip install -r requirements.txt` (if available) or install `google-cloud-bigquery` and `google-cloud-storage`, then start your local server.
3. **Google Colab:** Open the notebooks directly in Colab and follow the authentication prompts.
