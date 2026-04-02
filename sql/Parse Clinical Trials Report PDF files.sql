CREATE OR REPLACE EXTERNAL TABLE `clinical_trial_multiregion.cssr_reports`
WITH CONNECTION `meridian-dev-455515.us.cloud_ai_resources` 
OPTIONS(
  object_metadata = 'SIMPLE',
  uris = ['gs://cssr_reports_trials/april2_generation/*.pdf']
);

CREATE OR REPLACE TABLE clinical_trial_multiregion.cssr_reports_chunked_pdf AS (
  SELECT * FROM ML.PROCESS_DOCUMENT(
  MODEL `clinical_trial_multiregion.cssr_reports_model`,
  TABLE `clinical_trial_multiregion.cssr_reports`,
  PROCESS_OPTIONS => (JSON '{"layout_config": {"chunking_config": {"chunk_size": 250, "include_ancestor_headings": true}}}')
  )
);

CREATE OR REPLACE TABLE clinical_trial_multiregion.cssr_reports_parsed_pdf AS (
SELECT
  uri,
  JSON_EXTRACT_SCALAR(json , '$.chunkId') AS id,
  JSON_EXTRACT_SCALAR(json , '$.content') AS content,
  JSON_EXTRACT_SCALAR(json , '$.pageFooters[0].text') AS page_footers_text,
  JSON_EXTRACT_SCALAR(json , '$.pageSpan.pageStart') AS page_span_start,
  JSON_EXTRACT_SCALAR(json , '$.pageSpan.pageEnd') AS page_span_end
FROM clinical_trial_multiregion.cssr_reports_chunked_pdf, UNNEST(JSON_EXTRACT_ARRAY(ml_process_document_result.chunkedDocument.chunks, '$')) json
);


SELECT
    uri,
    AI.GENERATE(
      """
      You are a technical tabular data extractor from a clinical trial report document.
      Your task is to extract a comprehensive list of ALL columns fields from the text.
      
      ### CRITICAL: HANDLE LISTS EXHAUSTIVELY
      The text often lists multiple items for a single subject.
      EXAMPLE OUTPUT:
      {"Sponsor": "Novartis", "StudyTitle": "Study to Evaluate Efficacy and Safety of Inclisiran in Adolescents With Homozygous Familial Hypercholesterolemia", "PreferredUMLSName": ["Homozygous Familial Hypercholesterolemia"], "NCT_Number": "NCT04659863", "Phase": "PHASE3", "Trial_Status": "COMPLETED", "Disease_Areas": "Familial Hypercholesterolemia - Homozygous", "Targeted_Enrollment": 13, "Company": "Novartis", "semantic_text": "Title: Study to Evaluate Efficacy and Safety of Inclisiran in Adolescents With Homozygous Familial Hypercholesterolemia\n\nOfficial Title: Two Part (Double-blind Inclisiran Versus Placebo [Year 1] Followed by Open-label Inclisiran [Year 2]) Randomized Multicenter Study to Evaluate Safety, Tolerability, and Efficacy of Inclisiran in Adolescents (12 to Less Than 18 Years) With Homozygous Familial Hypercholesterolemia and Elevated LDL-cholesterol (ORION-13)\n\nSummary: This was a pivotal phase III study designed to evaluate safety, tolerability, and efficacy of inclisiran in adolescents with homozygous familial hypercholesterolemia (HoFH) and elevated low density lipoprotein cholesterol (LDL-C).\n\nDetailed Description: This was a two-part (double-blind, inclisiran versus placebo \\[Year 1\\] followed by open-label inclisiran \\[Year 2\\]) multicenter study in adolescents (aged 12 to \\< 18 years) with HoFH and elevated LDL-C (\\> 130 mg/dL; 3.4 mmol/L) on stable, individualized, optimal standard of care (SoC) background lipid-lowering therapy (including maximally tolerated statin treatment, at the Investigator's discretion) to evaluate the safety, tolerability, and efficacy of inclisiran in this pediatric patient population.\n\nFollowing an approximately 4-week screening/run-in period, the study had 2 sequential parts as follows:\n\nPart 1/Year 1: 12 months double-blind, parallel group period, in which participants were randomized in a 2:1 ratio to receive either inclisiran sodium 300 mg subcutaneous (s.c.) or placebo. The primary endpoint was assessed at Day 330.\n\nPart 2/Year 2: 12 months single arm, open-label follow-up period, with all participants receiving inclisiran sodium 300 mg s.c.\n\nStudy Design: Type: INTERVENTIONAL, Phase: PHASE3, Status: COMPLETED\n\nConditions: Familial Hypercholesterolemia - Homozygous\n\nEligibility Criteria: Inclusion Criteria:\n\n* Homozygous Familial Hypercholesterolemia (HoFH) diagnosed by genetic confirmation\n* Fasting LDL-C \\>130 mg/dL (3.4 mmol/L) at screening\n* On maximally tolerated dose of statin (investigator's discretion) with or without other lipid-lowering therapy; stable for ≥ 30 days before screening\n* Male or female participants \\>=12 to \\<18 years of age at screening\n\nExclusion Criteria:\n\n* Documented evidence of a null (negative) mutation in both LDLR alleles\n* Heterozygous familial hypercholesterolemia (HeFH)\n* Active liver disease\n* Secondary hypercholesterolemia, e.g. hypothyroidism or nephrotic syndrome\n* Previous treatment with monoclonal antibodies directed towards PCSK9 (within 90 days of screening)\n* Treatment with mipomersen or lomitapide (within 5 months of screening)\n* Recent and/or planned use of other investigational medicinal products or devices\n\nPrimary Outcomes: 1. Percentage Change in LDL-C From Baseline to Day 330 (Part 1/Year 1): Percentage change in low-density lipoprotein cholesterol (LDL-C) from baseline to Day 330 (Year 1)\n\nSecondary Outcomes: 1. Time-adjusted Percent Change in LDL-C From Baseline After Day 90 and up to Day 330 (Part 1/Year 1) 2. Percent Change in LDL-C From Baseline up to Day 720 3. Absolute Change in LDL-C From Baseline up to Day 720", "name": "Familial Hypercholesterolemia - Homozygous", "preferred_name": "Homozygous Familial Hypercholesterolemia", "semantic_type": ["Disease or Syndrome"], "definition": "A rare inherited genetic disorder, one form of HYPERLIPOPROTEINEMIA TYPE II, characterized by high level of LOW-DENSITY LIPOPROTEIN (LDL) which if not treated could elevate the chance of heart attack at an early age.", "mesh_code": "D000090542", "mesh_codes": [], "hpo_codes": [], "snomed_id": "238078005", "snomed_hierarchy": ["1899006|Autosomal hereditary disorder|Autosomal hereditary disorder (disorder)", "32895009|Hereditary disease|Hereditary disease (disorder)", "782964007|Genetic disease|Genetic disease (disorder)", "64572001|Disease|Disease (disorder)", "398036000|Familial hypercholesterolemia|Familial hypercholesterolemia (disorder)"], "drug_name": "inclisiran", "atc_code": "C10AX16", "atc_codes": ["C10AX16"], "rxnorm_code": "", "trade_names": ["Leqvio"], "ema_url": ["https://www.ema.europa.eu/en/documents/product-information/leqvio-epar-product-information_en.pdf"], "source_level": 5, "drug_preferred_name": "inclisiran", "drug_semantic_type": [], "criteria_type": "PHASE_REQUIREMENT", "criteria_text": "Trial must be in PHASE3", "phase_id": "PHASE3", "status_name": "COMPLETED", "status_description": "Study has been completed"}
      """ || content,
      output_schema => """
        Sponsor STRING,
        StudyTitle STRING,
        PreferredUMLSName ARRAY<STRING>,
        NCT_Number STRING,
        Phase STRING,
        Trial_Status STRING,
        Disease_Areas STRING,
        Targeted_Enrollment INT64,
        Company STRING,
        semantic_text STRING,
        name STRING,
        preferred_name STRING,
        semantic_type ARRAY<STRING>,
        definition STRING,
        mesh_code STRING,
        mesh_codes ARRAY<STRING>,
        hpo_codes ARRAY<STRING>,
        snomed_id STRING,
        snomed_hierarchy ARRAY<STRING>,
        drug_name STRING,
        atc_code STRING,
        atc_codes ARRAY<STRING>,
        rxnorm_code STRING,
        trade_names ARRAY<STRING>,
        ema_url ARRAY<STRING>,
        source_level INT64,
        drug_preferred_name STRING,
        drug_semantic_type ARRAY<STRING>,
        criteria_type STRING,
        criteria_text STRING,
        phase_id STRING,
        status_name STRING,
        status_description STRING
      """,
      connection_id => 'us.cloud_ai_resources',
      endpoint => 'gemini-2.5-flash'
    ) AS extracted_data
  FROM (
    SELECT uri, STRING_AGG(content ORDER BY page_span_start) as content FROM `meridian-dev-455515.clinical_trial_multiregion.cssr_reports_parsed_pdf`
GROUP BY uri
  )
;

