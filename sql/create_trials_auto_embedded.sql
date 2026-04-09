CREATE OR REPLACE TABLE `meridian-dev-455515.clinical_trial_dev.Trials_Auto_Embedded` (
  PostingID INT64,
  semantic_text STRING,
  embedding STRUCT<result ARRAY<FLOAT64>, status STRING>
    GENERATED ALWAYS AS (
      AI.EMBED(
        semantic_text,
        connection_id => 'us-central1.llm-connection',
        endpoint => 'text-embedding-005'
      )
    ) STORED OPTIONS (asynchronous = TRUE)
);

INSERT INTO `meridian-dev-455515.clinical_trial_dev.Trials_Auto_Embedded` (PostingID, semantic_text)
SELECT PostingID, semantic_text FROM `meridian-dev-455515.clinical_trial_dev.Trials`;
