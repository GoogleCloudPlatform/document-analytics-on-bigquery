CREATE OR REPLACE TABLE `meridian-dev-455515.clinical_trial_dev.Disorder_With_Embeddings` (
  disorder_cui STRING,
  name STRING,
  definition STRING,
  definitionEmbedding STRUCT<result ARRAY<FLOAT64>, status STRING>
    GENERATED ALWAYS AS (
      AI.EMBED(
        definition,
        connection_id => 'us-central1.llm-connection',
        endpoint => 'text-embedding-005'
      )
    ) STORED OPTIONS (asynchronous = TRUE)
);

INSERT INTO `meridian-dev-455515.clinical_trial_dev.Disorder_With_Embeddings` (disorder_cui, name, definition)
SELECT disorder_cui, name, definition FROM `meridian-dev-455515.clinical_trial_dev.Disorder`;
