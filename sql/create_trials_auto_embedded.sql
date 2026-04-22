-- Copyright 2024 Google LLC
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--     https://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

CREATE OR REPLACE TABLE `<PROJECT_ID>.<DATASET_ID>.Trials_Auto_Embedded` (
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

INSERT INTO `<PROJECT_ID>.<DATASET_ID>.Trials_Auto_Embedded` (PostingID, semantic_text)
SELECT PostingID, semantic_text FROM `<PROJECT_ID>.<DATASET_ID>.Trials`;
