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

SELECT 
t.* EXCEPT (embedding, char_count), 
d.* EXCEPT(disorder_cui, definitionEmbedding),
dr.* EXCEPT(drug_cui, preferred_name, semantic_type),
dr.preferred_name as drug_preferred_name, 
dr.semantic_type as drug_semantic_type,
tc.* EXCEPT(criteria_id),
tp.* EXCEPT(posting_id),
s.* EXCEPT(status_id)
FROM `<PROJECT_ID>.<DATASET_ID>.Trials` t
INNER JOIN `<PROJECT_ID>.<DATASET_ID>.TrialDisorder` td 
ON td.posting_id = t.PostingID
INNER JOIN `<PROJECT_ID>.<DATASET_ID>.Disorder` d
ON td.disorder_cui = d.disorder_cui
INNER JOIN `<PROJECT_ID>.<DATASET_ID>.TrialDrug` tdr
ON tdr.posting_id = t.PostingID
INNER JOIN `<PROJECT_ID>.<DATASET_ID>.Drug` dr
ON dr.drug_cui = tdr.drug_cui
INNER JOIN `<PROJECT_ID>.<DATASET_ID>.TrialRequires` treq
ON treq.posting_id = t.PostingID
INNER JOIN `<PROJECT_ID>.<DATASET_ID>.TrialCriteria` tc
ON tc.criteria_id = treq.criteria_id
INNER JOIN `<PROJECT_ID>.<DATASET_ID>.TrialPhase` tp
ON tp.posting_id = t.PostingID
INNER JOIN `<PROJECT_ID>.<DATASET_ID>.TrialStatus` ts
ON ts.posting_id = t.PostingID
INNER JOIN `<PROJECT_ID>.<DATASET_ID>.Status` s
ON s.status_id = ts.status_id
