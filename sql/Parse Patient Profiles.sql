-- ==============================================================================
-- SOURCE TEMPLATE: DO NOT EXECUTE DIRECTLY
-- This file serves as the raw, unescaped template for the Python parameterization engine.
-- To deploy this to BigQuery, you must:
-- 1. Configure config.yaml in the project root.
-- 2. Run: python3 scripts/parameterize.py
-- 3. Execute the resulting sql/Parameterized_Patient_Profiles.sql file.
-- ==============================================================================

CREATE OR REPLACE EXTERNAL TABLE `clinical_trial_multiregion.patient_profiles`
WITH CONNECTION `meridian-dev-455515.us.cloud_ai_resources` 
OPTIONS(
  object_metadata = 'SIMPLE',
  uris = ['gs://meridian-dev-455515-patient-profiles/*.txt']
);

CREATE OR REPLACE TABLE `clinical_trial_multiregion.Patients` AS (
  SELECT
    uri,
    extracted_data.name,
    extracted_data.age,
    extracted_data.sex,
    extracted_data.place_of_residency,
    extracted_data.employment_status,
    extracted_data.primary_disorder,
    extracted_data.other_relevant_history,
    extracted_data.symptoms,
    extracted_data.performance_status,
    extracted_data.physical_status,
    extracted_data.laboratory_results,
    extracted_data.prior_therapy,
    extracted_data.current_plan
  FROM (
    SELECT
      uri,
      AI.GENERATE(
        STRUCT(
          '''
          You are a clinical data extraction assistant. Extract the patient profile information from the provided document.
          
          Requirements:
          1. Use the exact keys requested.
          2. If "symptoms" are listed, separate them into an array of strings.
          3. Combine multiple laboratory results into a single string.
          4. If a field like "employment_status" is not explicitly stated but can be heavily inferred (e.g., an 84-year-old is likely "Retired"), infer it. Otherwise, return null.
          ''' AS prompt,
          OBJ.GET_ACCESS_URL(OBJ.MAKE_REF(uri, 'meridian-dev-455515.us.cloud_ai_resources'), 'r') AS document
        ),
        output_schema => '''
          name STRING,
          age STRING,
          sex STRING,
          place_of_residency STRING,
          employment_status STRING,
          primary_disorder STRING,
          other_relevant_history STRING,
          symptoms ARRAY<STRING>,
          performance_status STRING,
          physical_status STRING,
          laboratory_results STRING,
          prior_therapy STRING,
          current_plan STRING
        ''',
        model_params => JSON '{"generation_config": {"temperature": 0.1, "max_output_tokens": 2048, "thinking_config": {"include_thoughts": true}}}',
        connection_id => 'us.cloud_ai_resources',
        endpoint => 'gemini-2.5-pro'
      ) AS extracted_data
    FROM
      `meridian-dev-455515.clinical_trial_multiregion.patient_profiles`
  )
);
