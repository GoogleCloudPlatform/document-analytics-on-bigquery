# Plan: Synthetic Clinical Study Summary Report (CSSR) Generation

This plan provides a standardized, reusable workflow for generating high-fidelity, synthetic Clinical Study Summary Reports (CSSR) for clinical trial analytics.

## 1. Objective
Generate distinct, multi-page synthetic CSSR PDF documents that simulate real-world clinical trial protocols. These reports must accurately reflect the specific details of a given clinical trial (condition, intervention, phase, eligibility criteria).

## 2. Structural Requirements
Each report must be a `.pdf` file named `<PostingID>_<NCT_Number>.pdf`.
The document must follow a standardized 15-section structure:

1. **Administrative & Study Identification**
2. **Study Synopsis & Rationale**
3. **Study Design & Methodology**
4. **Subject Selection (Eligibility Criteria)**
5. **Intervention & Treatment Plan**
6. **Study Timeline & Visit Schedule**
7. **Outcome Measures (Endpoints)**
8. **Safety & Adverse Event Reporting**
9. **Statistical Analysis Plan (SAP) Summary**
10. **Quality Assurance & Regulatory Compliance**
11. **Study Identifiers & Governance**
12. **Clinical Framework**
13. **Study Procedures & Methodology**
14. **Observation & Follow-Up Schedule**
15. **Sign-off & Approval**

## 3. Data Sources
- **Trial Metadata**: BigQuery table `meridian-dev-455515.clinical_trial.ClinicalTrialMasterData` (or `Trials`). Contains all requisite structured data including `NCT_Number`, `PostingID`, `StudyTitle`, `Sponsor`, `Phase`, `Trial_Status`, `Disease_Areas`, trial condition, inclusion/exclusion criteria, and endpoints.

## 4. Generation Logic (Python)
When creating or running the generation script/notebook, implement the following:

- **Data Retrieval**: Query the BigQuery `ClinicalTrialMasterData` table for target `NCT_Number`s. Ensure that you capture the unique `PostingID` to avoid naming collisions.
- **LLM Content Synthesis**: 
  - Use `google-genai` to generate a Markdown draft following the strict 15-section template.
  - Provide the retrieved structured trial data to the prompt context.
- **Content Verification**: 
  - Implement a secondary evaluation LLM call to ensure the generated Markdown accurately includes all critical structured data (Sponsor, Phase, specific Inclusion/Exclusion criteria, Endpoints). If fields are missing, re-prompt the LLM to correct the omission.
- **PDF Conversion**: Use the `markdown` and `weasyprint` libraries to convert the validated Markdown string into a formatted PDF document.
- **Storage**: Save the generated PDFs locally to `data/generated_clinical_trials_reports/new/` (or push directly to GCS buckets as required by the pipeline).

## 5. Execution Workflow
1. **Prepare**: Extract target list of `PostingID` and `NCT_Number` pairs. Check local or cloud storage for existing files to avoid redundant processing.
2. **Fetch**: Query BigQuery for the detailed attributes of each trial.
3. **Synthesize**: Run the LLM-based generation and validation chain to produce the Markdown.
4. **Convert**: Render the Markdown into a PDF using `weasyprint`.
5. **Verify**:
   - Check the output directory for the newly generated `.pdf` files.
   - Confirm standard file naming convention `<PostingID>_<NCT_Number>.pdf`.
6. **Cleanup**: Monitor rate limits (e.g., HTTP 429 Resource Exhausted) during LLM generation and implement retry backoffs (e.g., 60-second sleep).

## 6. Template Structure Overview
```markdown
Clinical Study Summary Report (CSSR)
Document Status: Final | Version: 1.0 | Date: [Date]

1. Administrative & Study Identification
Full Study Title: [Title]
...

2. Study Synopsis & Rationale
...

[Sections 3 through 14 populated accordingly]

15. Sign-off & Approval
| Role | Name | Signature | Date |
| :--- | :--- | :--- | :--- |
| Principal Investigator | [Name] | ____________________ | [DD-MMM-YYYY] |
| Clinical Operations Lead | [Name] | ____________________ | [DD-MMM-YYYY] |
| Lead Statistician | [Name] | ____________________ | [DD-MMM-YYYY] |
```