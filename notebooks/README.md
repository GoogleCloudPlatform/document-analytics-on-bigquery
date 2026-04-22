# Notebooks: Clinical Trial Analytics & Knowledge Graphs

This directory contains Jupyter notebooks that demonstrate the application of the Healthcare Document Analytics solution. These notebooks provide an interactive layer for exploring the BigQuery Knowledge Graph, performing semantic analysis on clinical trials, and utilizing Gemini for generative insights.

## Prerequisites
* Access to the BigQuery project and dataset defined in `sql/`.
* Python environment with `google-cloud-bigquery`, `google-cloud-bigquery-storage`, `pandas`, `db-dtypes`, and `bigquery-magics[spanner-graph-notebook]`.

> [!NOTE]
> 🔬 **The documents explored in these notebooks are all synthetically generated.** If you would you like to generate your own synthetic documents you can use the Gemini CLI plans as guidance [PLANS](https://github.com/GoogleCloudPlatform/document-analytics-on-bigquery/blob/main/gemini-cli-plans/README.md). You can reuse the existing documents by following instruction on the installation guide [INSTALLATION.md](https://github.com/GoogleCloudPlatform/document-analytics-on-bigquery/blob/main/INSTALLATION.md) and [README.md](https://github.com/GoogleCloudPlatform/document-analytics-on-bigquery/blob/main/README.md) in the [document-analytics-on-bigquery](https://github.com/GoogleCloudPlatform/document-analytics-on-bigquery) repository.

## Key Notebooks

### 1. `NEXT_DEMO_clinical_trials_platform.ipynb`
The primary, comprehensive demonstration of the R&D Data Research Platform. This end-to-end notebook showcases the full \"4-pillar\" capabilities of BigQuery:
* **Generative AI:** LLM-powered summaries and eligibility guidance using Gemini 2.5 Pro.
* **Semantic Search:** Vector similarity using 768-dimensional embeddings to match patient symptoms to medical conditions and trials.
* **Graph Traversal:** Multi-hop pattern matching using GQL (`GRAPH_TABLE`) to explore relationships between Drugs, Disorders, and Trials.
* **Relational SQL:** Traditional analytics and aggregations for portfolio and progression analysis.

### 2. `clinical_trials_graph_demo (1).ipynb`
A specialized demonstration focusing deeply on the clinical trial domain and graph analytics. It highlights how the property graph can be used to:
* Execute complex GQL multi-hop paths (e.g., Trial -> Uses Drug -> MayTreat -> Disorder).
* Leverage medical ontologies (like SNOMED CT hierarchies) for semantic expansion.
* Perform business intelligence and pipeline analysis on trial sponsors.
