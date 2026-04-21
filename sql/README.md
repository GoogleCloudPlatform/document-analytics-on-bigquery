# SQL Scripts: BigQuery AI & Graph Workflows

This directory contains the foundational SQL scripts for the Healthcare Document Analytics solution. These scripts orchestrate the transition from unstructured PDF reports to a structured, relational, and graph-based data model directly within BigQuery.

## ⚠️ Important: Parameterization Engine (v2.0)
Do **NOT** execute the raw extraction files directly anymore. They are now utilized as **Source Templates** by the python parameterization engine:
* `Parse Clinical Trials Report PDF files.sql` -> *DO NOT EXECUTE. DO NOT EDIT HARDCODED VALUES.*
* `Parse Patient Profiles.sql` -> *DO NOT EXECUTE. DO NOT EDIT HARDCODED VALUES.*

To deploy these pipelines to BigQuery, you must now:
1. Edit the `config.yaml` in the root folder with your Project ID, Dataset, and GCS URIs.
2. Run `python3 scripts/parameterize.py`.
3. Execute the newly generated, safely-escaped files:
   * `Parameterized_Clinical_Trials.sql`
   * `Parameterized_Patient_Profiles.sql`

## Key Scripts

### 1. `setup_clinical_trial_graph.sql`
Defines the **BigQuery Property Graph** (`<DATASET_ID>.DrugGraph`).
* **Model Definitions:** Configures Remote Models for text embeddings (`text-embedding-005`), multimodal embeddings, and Gemini LLMs (`gemini-2.5-pro`).
* **Node Tables:** Maps structured clinical entities (Trials, Drugs, Disorders, MOA, etc.) to graph nodes.
* **Edge Tables:** Defines clinical relationships (e.g., `Drug` -> `MayTreat` -> `Disorder`, `Trial` -> `Uses` -> `Drug`).
* **Hierarchies:** Includes logic for disorder-to-disorder relationships (`IsSubtypeOf`).

### 2. `Parameterized_Clinical_Trials.sql` (Generated)
Implements the **Zero-Copy RAG** extraction pipeline as a Stored Procedure:
* **Object Table Integration:** Connects to PDF files in Google Cloud Storage via parameters.
* **Document AI Processing:** Uses `ML.PROCESS_DOCUMENT` to chunk and extract text while preserving layout.
* **Generative Extraction:** Leverages Gemini (via `AI.GENERATE`) with a detailed prompt and output schema to parse clinical fields (Sponsor, Phase, NCT_Number, etc.) into structured columns.

### 3. `Parameterized_Patient_Profiles.sql` (Generated)
Implements text extraction as a Stored Procedure:
* Extracts demographic and medical information natively using Object Tables and `AI.GENERATE`.

### 4. `Clinical TRial Denormalized Data.sql`
Consolidates extracted and pre-existing clinical data into unified views, preparing the dataset for analytics and graph construction.

### 5. `Query Clinical Trial Master Data for Unique Trials.sql`
A utility script for retrieving unique trials and metadata, often used as an input for synthetic data generation workflows.

## Prerequisites
* A BigQuery Dataset (e.g., `<DATASET_ID>`).
* A Cloud Resource Connection (e.g., `us-central1.llm-connection`) with IAM permissions for Vertex AI and Document AI.
* A Document AI processor configured for the `ML.PROCESS_DOCUMENT` call.
