
import json
import subprocess
import os
from datetime import datetime

def generate_markdown_from_template(template_text, data):
    """
    Fills a template with data from a JSON object.
    This is a simple substitution implementation.
    A more sophisticated approach would use a templating engine
    or an LLM.
    """
    
    # Extract official title from semantic_text
    official_title = ""
    if "semantic_text" in data:
        for line in data["semantic_text"].split('\n'):
            if line.startswith("Official Title:"):
                official_title = line.replace("Official Title:", "").strip()
                break

    # Extract study type, blinding and randomization from semantic_text
    study_design = ""
    blinding = "N/A"
    randomization = "N/A"
    if "semantic_text" in data:
        for line in data["semantic_text"].split('\n'):
            if line.startswith("Summary:"):
                if "double-blind" in line.lower():
                    blinding = "Double-blind"
                elif "single-blind" in line.lower():
                    blinding = "Single-blind"
                elif "open-label" in line.lower():
                    blinding = "Open-label"
                if "randomized" in line.lower():
                    randomization = "Randomized"
            if line.startswith("Study Design:"):
                study_design = line.replace("Study Design:", "").strip()
                break
    
    # Extract criteria
    inclusion_criteria = ""
    exclusion_criteria = ""
    if "semantic_text" in data:
        in_inclusion = False
        in_exclusion = False
        for line in data["semantic_text"].split('\n'):
            if "Inclusion Criteria:" in line:
                in_inclusion = True
                in_exclusion = False
                inclusion_criteria += line.replace("Inclusion Criteria:", "").strip() + "\n"
                continue
            elif "Exclusion Criteria:" in line:
                in_inclusion = False
                in_exclusion = True
                exclusion_criteria += line.replace("Exclusion Criteria:", "").strip() + "\n"
                continue
            
            if in_inclusion:
                inclusion_criteria += line.strip() + "\n"
            elif in_exclusion:
                exclusion_criteria += line.strip() + "\n"


    replacements = {
        "[Draft / Final]": "Draft",
        "[0.0]": "1.0",
        "[DD-MMM-YYYY]": datetime.now().strftime("%d-%b-%Y"),
        "[Insert Official Protocol Title]": data.get("StudyTitle", ""),
        "[e.g., HK-QIP Study]": "",  # Short Title/Acronym not available
        "[Internal Study ID]": data.get("PostingID", ""),
        "[ClinicalTrials.gov Identifier]": data.get("NCT_Number", ""),
        "[Specific Subsidiary/Business Unit]": data.get("Sponsor", ""),
        "[Generic/Chemical Name or Device Name]": "", # Not available
        "[Phase I/II/III/IV or N/A for Quality Improvement]": data.get("Phase", ""),
        "[Name and Contact Information]": "", # Not available
        "{{PostingID}}": data.get("PostingID", ""),
        "{{NCT_Number}}": data.get("NCT_Number", ""),
        "{{Sponsor}}": data.get("Sponsor", ""),
        "{{StudyTitle}}": data.get("StudyTitle", ""),
        "{{Official Title}}": official_title,
        "[State the main question the study aims to answer].": "",
        "[List supporting objectives].": "",
        "Briefly describe the medical necessity. Why are we conducting this study now? (e.g., "To address the gap in RAASi optimization in CKD-ND patients with $sK+ > 5.0$ mmol/L.")": data.get("semantic_text", "").split("Summary:")[1].split("Study Design:")[0].replace('\n', ' '),
        "[e.g., Interventional, Observational, Registry]": study_design,
        "[e.g., Single-arm, Placebo-controlled, Active Comparator]": "",
        "[e.g., Open-label, Double-blind, Single-blind]": blinding,
        "[e.g., 1:1, Stratified, N/A]": randomization,
        "[Total number of evaluable patients required]": data.get("Targeted_Enrollment", ""),
        "[Global and Regional breakdown]": "",
        "[DD-MMM-YYYY]": "",
        "[Criterion 1, e.g., Age $\ge 18$ years]": inclusion_criteria.replace('*','-'),
        "[Criterion 2, e.g., Confirmed diagnosis of X via $eGFR$]": "",
        "[Criterion 3]": "",
        "[Criterion 1, e.g., Pregnancy or breastfeeding]": exclusion_criteria.replace('*','-'),
        "[Criterion 2, e.g., Concomitant use of prohibited medication Y]": "",
        "[Criterion 3, e.g., Life expectancy < 12 months]": "",
    }

    md_content = template_text
    for key, value in replacements.items():
        md_content = md_content.replace(key, str(value))
        
    return md_content

def main():
    
    template_file = 'sql/Clinical Study Summary Report Template.pdf'
    
    # For this script, we will use a text file with the ocr content.
    template_text = """
# Clinical Study Summary Report (CSSR) Template
**Document Status:** [Draft / Final] | **Version:** [0.0] | **Date:** [DD-MMM-YYYY]

## 1. Administrative & Study Identification
| Field | Data Entry / Details |
|---|---|
| Full Study Title | [Insert Official Protocol Title] |
| Short Title/Acronym | [e.g., HK-QIP Study] |
| Protocol Number | [Internal Study ID] |
| NCT Number | [ClinicalTrials.gov Identifier] |
| Sponsor Name | [Specific Subsidiary/Business Unit] |
| Investigational Product | [Generic/Chemical Name or Device Name] |
| Phase of Development | [Phase I/II/III/IV or N/A for Quality Improvement] |
| Medical Monitor | [Name and Contact Information] |

## 2. Study Synopsis & Rationale
### 2.1 Study Objective
- **Primary Objective:** [State the main question the study aims to answer].
- **Secondary Objectives:** [List supporting objectives].
### 2.2 Background & Rationale
Briefly describe the medical necessity. Why are we conducting this study now? (e.g., "To address the gap in RAASi optimization in CKD-ND patients with $sK+ > 5.0$ mmol/L.")

## 3. Study Design & Methodology
### 3.1 Design Framework
- **Study Type:** [e.g., Interventional, Observational, Registry]
- **Control Type:** [e.g., Single-arm, Placebo-controlled, Active Comparator]
- **Blinding:** [e.g., Open-label, Double-blind, Single-blind]
- **Randomization:** [e.g., 1:1, Stratified, N/A]
### 3.2 Planned Enrollment & Duration
- **Target $N$:** [Total number of evaluable patients required]
- **Number of Sites:** [Global and Regional breakdown]
- **Estimated Study Start:** [DD-MMM-YYYY]
- **Estimated Primary Completion:** [DD-MMM-YYYY]

## 4. Subject Selection (Eligibility Criteria)
### 4.1 Inclusion Criteria
1. [Criterion 1, e.g., Age $\ge 18$ years]
2. [Criterion 2, e.g., Confirmed diagnosis of X via $eGFR$]
3. [Criterion 3]
### 4.2 Exclusion Criteria
1. [Criterion 1, e.g., Pregnancy or breastfeeding]
2. [Criterion 2, e.g., Concomitant use of prohibited medication Y]
3. [Criterion 3, e.g., Life expectancy < 12 months]

## 11. Study Identifiers & Governance
- **Primary ID:** {{PostingID}}
- **Registry Number:** {{NCT_Number}}
- **Sponsor/Lead Organization:** {{Sponsor}}
- **Study Title:** {{StudyTitle}}
- **Official Regulatory Title:** {{Official Title}}
"""

    json_file = 'sql/ClinicalTrialDenormalizedData-partaf.json'
    output_dir = 'generated_reports'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(json_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            posting_id = data.get("PostingID")
            if not posting_id:
                continue

            md_content = generate_markdown_from_template(template_text, data)
            
            md_filename = os.path.join(output_dir, f"{posting_id}.md")
            with open(md_filename, 'w') as md_file:
                md_file.write(md_content)
            
            # Convert markdown to PDF using pandoc
            pdf_filename = os.path.join(output_dir, f"{posting_id}.pdf")
            try:
                subprocess.run(['pandoc', md_filename, '-o', pdf_filename], check=True)
                print(f"Generated {pdf_filename}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"Could not convert {md_filename} to PDF. Please ensure pandoc is installed.")
                # If pandoc fails, we will just have the markdown file.
                pass

if __name__ == "__main__":
    main()
