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

CREATE OR REPLACE MODEL `<PROJECT_ID>.<DATASET_ID>.EmbeddingsModel`
REMOTE WITH CONNECTION `<PROJECT_ID>.<BIGQUERY_LOCATION>.llm-connection` 
OPTIONS (
  ENDPOINT = 'text-embedding-005'
);

--CREATE OR REPLACE MODEL `<PROJECT_ID>.<DATASET_ID>.EmbeddingsModelGE2`
--REMOTE WITH CONNECTION `<PROJECT_ID>.<BIGQUERY_LOCATION>.llm-connection` 
--OPTIONS (
--  ENDPOINT = 'gemini-embedding-2-preview'
--);

CREATE OR REPLACE MODEL `<PROJECT_ID>.<DATASET_ID>.EmbeddingsModelMME`
REMOTE WITH CONNECTION `<PROJECT_ID>.<BIGQUERY_LOCATION>.llm-connection` 
OPTIONS (
  ENDPOINT = 'multimodalembedding@001'
);

CREATE OR REPLACE MODEL `<PROJECT_ID>.<DATASET_ID>.EmbeddingsModelGE1`
REMOTE WITH CONNECTION `<PROJECT_ID>.<BIGQUERY_LOCATION>.llm-connection` 
OPTIONS (
  ENDPOINT = 'gemini-embedding-001'
);

CREATE OR REPLACE MODEL `<PROJECT_ID>.<DATASET_ID>.LLMModel`
REMOTE WITH CONNECTION `<PROJECT_ID>.<BIGQUERY_LOCATION>.llm-connection`
OPTIONS (
  ENDPOINT = 'gemini-2.5-pro'
);

CREATE OR REPLACE MODEL `<DATASET_ID>.cssr_reports_model`
REMOTE WITH CONNECTION `<PROJECT_ID>.<BIGQUERY_LOCATION>.cloud_ai_resources` 
  OPTIONS(
    remote_service_type = 'CLOUD_AI_DOCUMENT_V1',
    document_processor = 'e3d2713160e255fc'
);

CREATE OR REPLACE MODEL `<PROJECT_ID>.<DATASET_ID>.LLMModelFlash`
REMOTE WITH CONNECTION `<PROJECT_ID>.<BIGQUERY_LOCATION>.cloud_ai_resources`
OPTIONS (
  ENDPOINT = 'gemini-2.5-flash'
);

CREATE OR REPLACE PROPERTY GRAPH <DATASET_ID>.DrugGraph
NODE TABLES (
  -- Trial nodes
  <DATASET_ID>.Trials
    KEY (PostingID)
    LABEL Trial
    PROPERTIES (PostingID, Sponsor, StudyTitle, PreferredUMLSName),

  -- Drug nodes
  <DATASET_ID>.Drug
    KEY (drug_cui)
    LABEL Drug
    PROPERTIES (drug_cui, drug_name, preferred_name, semantic_type, atc_codes, rxnorm_code, trade_names),

  -- Disorder nodes
  <DATASET_ID>.Disorder
    KEY (disorder_cui)
    LABEL Disorder
    PROPERTIES (disorder_cui, name, preferred_name, definition, definitionEmbedding, semantic_type,
                mesh_code, mesh_codes, hpo_codes, snomed_id, snomed_hierarchy),

  -- MOA nodes
  <DATASET_ID>.MOA
    KEY (moa_id)
    LABEL MechanismOfAction
    PROPERTIES (moa_id, moa_name, description),

  -- Criteria nodes
  <DATASET_ID>.TrialCriteria
    KEY (criteria_id)
    LABEL Criteria
    PROPERTIES (criteria_id, criteria_type, criteria_text),

  -- Company nodes
  <DATASET_ID>.Company
    KEY (company_id)
    LABEL Company
    PROPERTIES (company_id, company_name),

  -- UPDATED: Phase nodes (added phase_name)
  <DATASET_ID>.Phase
    KEY (phase_id)
    LABEL Phase
    PROPERTIES (phase_id, phase_name),

  -- UPDATED: Status nodes (added status_name)
  <DATASET_ID>.Status
    KEY (status_id)
    LABEL Status
    PROPERTIES (status_id, status_name)
)
EDGE TABLES (
  -- Drug → Disorder (MayTreat)
  <DATASET_ID>.DrugDisorder
    KEY (drug_cui, disorder_cui)
    SOURCE KEY (drug_cui) REFERENCES Drug (drug_cui)
    DESTINATION KEY (disorder_cui) REFERENCES Disorder (disorder_cui)
    LABEL MayTreat
    PROPERTIES (drug_cui, disorder_cui),

  -- Drug → MOA (HasMechanismOfAction)
  <DATASET_ID>.DrugMOA
    KEY (drug_cui, moa_id)
    SOURCE KEY (drug_cui) REFERENCES Drug (drug_cui)
    DESTINATION KEY (moa_id) REFERENCES MOA (moa_id)
    LABEL HasMechanismOfAction
    PROPERTIES (drug_cui, moa_id),

  -- Trial → Criteria (Requires)
  <DATASET_ID>.TrialRequires
    KEY (posting_id, criteria_id)
    SOURCE KEY (posting_id) REFERENCES Trials (PostingID)
    DESTINATION KEY (criteria_id) REFERENCES TrialCriteria (criteria_id)
    LABEL Requires
    PROPERTIES (posting_id, criteria_id),

  -- Drug → Company (ManufacturedBy)
  <DATASET_ID>.DrugCompany
    KEY (drug_cui, company_id)
    SOURCE KEY (drug_cui) REFERENCES Drug (drug_cui)
    DESTINATION KEY (company_id) REFERENCES Company (company_id)
    LABEL ManufacturedBy
    PROPERTIES (drug_cui, company_id),

  -- Trial → Disorder (Treats)
  <DATASET_ID>.TrialDisorder
    KEY (posting_id, disorder_cui)
    SOURCE KEY (posting_id) REFERENCES Trials (PostingID)
    DESTINATION KEY (disorder_cui) REFERENCES Disorder (disorder_cui)
    LABEL Treats
    PROPERTIES (posting_id, disorder_cui),

  -- Trial → Drug (Uses)
  <DATASET_ID>.TrialDrug
    KEY (posting_id, drug_cui)
    SOURCE KEY (posting_id) REFERENCES Trials (PostingID)
    DESTINATION KEY (drug_cui) REFERENCES Drug (drug_cui)
    LABEL Uses
    PROPERTIES (posting_id, drug_cui),

  -- Trial → Status (HasStatus)
  <DATASET_ID>.TrialStatus
    KEY (posting_id, status_id)
    SOURCE KEY (posting_id) REFERENCES Trials (PostingID)
    DESTINATION KEY (status_id) REFERENCES Status (status_id)
    LABEL HasStatus
    PROPERTIES (posting_id, status_id),

  -- Trial → Phase (InPhase)
  <DATASET_ID>.TrialPhase
    KEY (posting_id, phase_id)
    SOURCE KEY (posting_id) REFERENCES Trials (PostingID)
    DESTINATION KEY (phase_id) REFERENCES Phase (phase_id)
    LABEL InPhase
    PROPERTIES (posting_id, phase_id),

  -- Disorder → Disorder (IsSubtypeOf)
  <DATASET_ID>.DisorderHierarchy
    KEY (child_cui, parent_cui)
    SOURCE KEY (child_cui) REFERENCES Disorder (disorder_cui)
    DESTINATION KEY (parent_cui) REFERENCES Disorder (disorder_cui)
    LABEL IsSubtypeOf
    PROPERTIES (child_cui, parent_cui)
);