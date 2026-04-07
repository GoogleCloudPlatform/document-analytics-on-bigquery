# Gemini CLI Plans: Reusable Agentic Workflows

This directory contains standardized, multi-step plans for the **Gemini CLI**. These plans define structured workflows for generating high-fidelity synthetic healthcare data used throughout the solution.

## Available Plans

### 1. `GEMINI_Generate_Clinical_Trials_Report_Reusable_Plan.md`
A reusable workflow for generating synthetic **Clinical Study Summary Reports (CSSR)**. It defines:
*   **Objective:** Generating 15-section clinical protocols based on BigQuery trial metadata.
*   **Tools:** Python, `google-genai` for content synthesis, and `weasyprint` for PDF conversion.
*   **Validation:** Includes a secondary evaluation step to ensure all structured data fields are accurately represented in the PDF.

### 2. `GEMINI_Generate_Patient_Profile_Reusable_Plan.md`
A standardized plan for creating **Patient Profiles**. It specifies:
*   **Objective:** Generating distinct profiles mapped to specific trial inclusion/exclusion criteria.
*   **Ineligibility Injection:** Logic for randomly assigning disqualifying factors (pediatric, geriatric frailty, organ impairment) to test negative cases.
*   **Constraints:** Prevents Trial ID leaks and ensures identity diversity.

### 3. `GEMINI_Generate_Profile_Summaries.md`
A plan focused on summarizing generated patient data into an aggregated format, facilitating quick review and large-scale testing.

## How to Use
These plans are designed to be used with the Gemini CLI. An agent (like this one) can load these plans to execute batch generation tasks with consistent quality and structure.
