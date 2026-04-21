# Notebooks: Clinical Trial Analytics & Knowledge Graphs

This directory contains Jupyter notebooks that demonstrate the application of the Healthcare Document Analytics solution. These notebooks provide an interactive layer for exploring the BigQuery Knowledge Graph and performing semantic analysis on clinical trials.

## Key Notebooks

### 1. `Bigquery_knowledge_graph_demo (1).ipynb`
The primary demonstration for the solution's graph capabilities. It shows how to:
* Query the BigQuery Property Graph using GQL.
* Identify relationships between drugs and disorders across multiple hops.
* Visualize the clinical ecosystem.

### 2. `clinical_trials_graph_demo (1).ipynb`
A specialized demo focusing on the clinical trial domain, highlighting how the graph can be used to find eligible trials based on specific criteria or therapeutic overlaps.

### 3. `kg_demo_template (1).ipynb`
A reusable template for building custom Knowledge Graph demonstrations using the existing schema.

### 4. `00_generate_cssr_reports.ipynb` & `00_generate_reports.ipynb`
Notebooks used to execute the synthetic data generation workflows. They implement the logic defined in the `gemini-cli-plans/` directory, using Python and the Google GenAI SDK to create synthetic Clinical Study Summary Reports (CSSRs).

## Prerequisites
* Access to the BigQuery project and dataset defined in `sql/`.
* Python environment with `google-cloud-bigquery`, `google-genai`, and visualization libraries (if applicable).
