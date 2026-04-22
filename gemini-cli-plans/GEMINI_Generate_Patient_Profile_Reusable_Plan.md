# Plan: Synthetic Patient Profile Generation

This plan provides a standardized, reusable workflow for generating high-fidelity, synthetic patient profiles for clinical trial analytics.

## 1. Objective
Generate distinct patient profiles that simulate real-world clinical data. Profiles must fall into two categories:
- **Eligible**: Patients who meet standard inclusion criteria for trials in `ClinicalTrialMasterData`.
- **Ineligible**: Patients with specific "deal-breaker" factors (e.g., extreme age, pregnancy, severe organ impairment) to test exclusion logic.

## 2. Structural Requirements
Each profile must be a `.txt` file named `Patient_Profile_<First>_<Last>_<Index>.txt` with exactly five sections:

1. **DEMOGRAPHIC INFORMATION**
   - Must include: Name, Age, Sex, Place of Residency (specific city/country).
2. **CLINICAL DIAGNOSIS & DISORDERS**
   - Must include: Primary Disorder, Other Relevant History.
3. **SYMPTOMS & PHYSICAL STATUS**
   - **Constraint**: List a realistic subset of **2 to 4 symptoms** only. Do not dump the entire symptom list.
4. **LABORATORY RESULTS**
   - Include realistic hematology, biochemistry, or imaging markers.
5. **TREATMENT HISTORY**
   - Must include: Prior Therapy, Current Plan.
   - **Constraint**: DO NOT include Trial IDs (NCT numbers).
   - **Constraint**: DO NOT provide a rationale for trial qualification or ineligibility.

## 3. Data Sources
- **Trials/Conditions**: `<PROJECT_ID>.<DATASET_ID>.ClinicalTrialMasterData` (column: `preferred_name`).
- **Symptoms**: `<PROJECT_ID>.<DATASET_ID>.DisorderSymptoms` (column: `symptoms.list.element`).

## 4. Generation Logic (Python)
When creating a generation script, implement the following:

- **Uniqueness**: Maintain a `blacklist` of names by reading existing files in `generated_patient_profiles/` to prevent identity duplicates.
- **Identity Diversity**: Use a large pool (>100) of first/last names and global cities. Ensure gender-appropriate first names.
- **Symptom Sampling**:
  
  ```python
picked = random.sample(possible_symptoms, random.randint(2, 4))

  ```

- **Ineligibility Injection** (for negative cases): Randomly assign one disqualifying factor:
  - `Pediatric` (<18) for adult trials.
  - `Geriatric Frailty` (>85 + ECOG 3/4).
  - `Pregnancy/Breastfeeding`.
  - `Organ Impairment` (e.g., CrCl < 30 mL/min).
  - `Active Co-infections` (HIV/Hepatitis).
  - `Concurrent Trial Enrollment`.

## 5. Execution Workflow
1. **Prepare**: Extract existing names to a JSON file.
2. **Fetch**: Query BigQuery for a randomized subset of trials and the full symptoms mapping.
3. **Synthesize**: Run a Python script to generate files in batches of 50 or more.
4. **Verify**:
   - Confirm total file count.
   - Grep for `[` or `]` to ensure no prompt placeholders remain.
   - Grep for `NCT` to ensure no Trial IDs were leaked.
5. **Cleanup**: Remove temporary scripts and data exports.

## 6. Template

```text
PATIENT PROFILE: <NAME>

1. DEMOGRAPHIC INFORMATION
- Name: <First Last>
- Age: <X> years
- Sex: <Male/Female>
- Place of Residency: <City, Country>

2. CLINICAL DIAGNOSIS & DISORDERS
- Primary Disorder: <Condition>
- Other Relevant History: <Realistic clinical narrative>

3. SYMPTOMS & PHYSICAL STATUS
- Symptoms: <Symptom A, Symptom B, Symptom C.>
- Performance Status: <ECOG 0-4>
- Physical Status: <General health note>

4. LABORATORY RESULTS
- <Realistic lab values/markers>

5. TREATMENT HISTORY
- Prior Therapy: <Previous meds/procedures>
- Current Plan: <Next steps in care>
```
