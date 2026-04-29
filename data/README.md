# Data Assets: Synthetic Healthcare Documents & Profiles

This directory stores the output of synthetic data generation workflows. These assets are used to test the end-to-end clinical trial analytics pipeline, from PDF parsing to trial matching.

## Directory Structure

### `generated_clinical_trials_reports/`
Contains synthetic **Clinical Study Summary Reports (CSSR)** in PDF format.
* **Subfolders:** `new/` (active generation) and `old/` (historical versions).
* **Naming Convention:** `<PostingID>_<NCT_Number>.pdf`.
* **Structure:** Each report follows a standardized 15-section protocol structure (Administrative, Synopsis, Design, Subject Selection, etc.).

### `generated_patient_profiles/`
Contains synthetic **Patient Profiles** in text format.
* **Naming Convention:** `Patient_Profile_<First>_<Last>_<Index>.txt`.
* **Structure:** Profiles include demographic information, clinical diagnosis, symptoms, laboratory results, and treatment history.
* **Goal:** Profiles are generated as either "Eligible" or "Ineligible" for specific trials to test automated recruitment logic.
* **Aggregated Data:** `aggregated_summarized_patient_profiles.txt` provides a summary view of multiple patient records.

## Usage
These files serve as the input for the **Zero-Copy RAG** pipeline (via GCS Object Tables) and for evaluating the performance of the clinical Knowledge Graph.
