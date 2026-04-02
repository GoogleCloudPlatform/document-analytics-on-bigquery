CREATE OR REPLACE MODEL `meridian-dev-455515.clinical_trial.EmbeddingsModel`
REMOTE WITH CONNECTION `meridian-dev-455515.us-central1.llm-connection` 
OPTIONS (
  ENDPOINT = 'text-embedding-005'
);

--CREATE OR REPLACE MODEL `meridian-dev-455515.clinical_trial.EmbeddingsModelGE2`
--REMOTE WITH CONNECTION `meridian-dev-455515.us-central1.llm-connection` 
--OPTIONS (
--  ENDPOINT = 'gemini-embedding-2-preview'
--);

CREATE OR REPLACE MODEL `meridian-dev-455515.clinical_trial.EmbeddingsModelMME`
REMOTE WITH CONNECTION `meridian-dev-455515.us-central1.llm-connection` 
OPTIONS (
  ENDPOINT = 'multimodalembedding@001'
);

CREATE OR REPLACE MODEL `meridian-dev-455515.clinical_trial.EmbeddingsModelGE1`
REMOTE WITH CONNECTION `meridian-dev-455515.us-central1.llm-connection` 
OPTIONS (
  ENDPOINT = 'gemini-embedding-001'
);

CREATE OR REPLACE MODEL `meridian-dev-455515.clinical_trial.LLMModel`
REMOTE WITH CONNECTION `meridian-dev-455515.us-central1.llm-connection`
OPTIONS (
  ENDPOINT = 'gemini-2.5-pro'
);

CREATE OR REPLACE MODEL `clinical_trial_multiregion.cssr_reports_model`
REMOTE WITH CONNECTION `meridian-dev-455515.us.cloud_ai_resources` 
  OPTIONS(
    remote_service_type = 'CLOUD_AI_DOCUMENT_V1',
    document_processor = 'e3d2713160e255fc'
);

CREATE OR REPLACE PROPERTY GRAPH clinical_trial.DrugGraph
NODE TABLES (
  -- Trial nodes
  clinical_trial.Trials
    KEY (PostingID)
    LABEL Trial
    PROPERTIES (PostingID, Sponsor, StudyTitle, PreferredUMLSName),

  -- Drug nodes
  clinical_trial.Drug
    KEY (drug_cui)
    LABEL Drug
    PROPERTIES (drug_cui, drug_name, preferred_name, semantic_type, atc_codes, rxnorm_code, trade_names),

  -- Disorder nodes
  clinical_trial.Disorder
    KEY (disorder_cui)
    LABEL Disorder
    PROPERTIES (disorder_cui, name, preferred_name, definition, definitionEmbedding, semantic_type,
                mesh_code, mesh_codes, hpo_codes, snomed_id, snomed_hierarchy),

  -- MOA nodes
  clinical_trial.MOA
    KEY (moa_id)
    LABEL MechanismOfAction
    PROPERTIES (moa_id, moa_name, description),

  -- Criteria nodes
  clinical_trial.TrialCriteria
    KEY (criteria_id)
    LABEL Criteria
    PROPERTIES (criteria_id, criteria_type, criteria_text),

  -- Company nodes
  clinical_trial.Company
    KEY (company_id)
    LABEL Company
    PROPERTIES (company_id, company_name),

  -- UPDATED: Phase nodes (added phase_name)
  clinical_trial.Phase
    KEY (phase_id)
    LABEL Phase
    PROPERTIES (phase_id, phase_name),

  -- UPDATED: Status nodes (added status_name)
  clinical_trial.Status
    KEY (status_id)
    LABEL Status
    PROPERTIES (status_id, status_name)
)
EDGE TABLES (
  -- Drug → Disorder (MayTreat)
  clinical_trial.DrugDisorder
    KEY (drug_cui, disorder_cui)
    SOURCE KEY (drug_cui) REFERENCES Drug (drug_cui)
    DESTINATION KEY (disorder_cui) REFERENCES Disorder (disorder_cui)
    LABEL MayTreat
    PROPERTIES (drug_cui, disorder_cui),

  -- Drug → MOA (HasMechanismOfAction)
  clinical_trial.DrugMOA
    KEY (drug_cui, moa_id)
    SOURCE KEY (drug_cui) REFERENCES Drug (drug_cui)
    DESTINATION KEY (moa_id) REFERENCES MOA (moa_id)
    LABEL HasMechanismOfAction
    PROPERTIES (drug_cui, moa_id),

  -- Trial → Criteria (Requires)
  clinical_trial.TrialRequires
    KEY (posting_id, criteria_id)
    SOURCE KEY (posting_id) REFERENCES Trials (PostingID)
    DESTINATION KEY (criteria_id) REFERENCES TrialCriteria (criteria_id)
    LABEL Requires
    PROPERTIES (posting_id, criteria_id),

  -- Drug → Company (ManufacturedBy)
  clinical_trial.DrugCompany
    KEY (drug_cui, company_id)
    SOURCE KEY (drug_cui) REFERENCES Drug (drug_cui)
    DESTINATION KEY (company_id) REFERENCES Company (company_id)
    LABEL ManufacturedBy
    PROPERTIES (drug_cui, company_id),

  -- Trial → Disorder (Treats)
  clinical_trial.TrialDisorder
    KEY (posting_id, disorder_cui)
    SOURCE KEY (posting_id) REFERENCES Trials (PostingID)
    DESTINATION KEY (disorder_cui) REFERENCES Disorder (disorder_cui)
    LABEL Treats
    PROPERTIES (posting_id, disorder_cui),

  -- Trial → Drug (Uses)
  clinical_trial.TrialDrug
    KEY (posting_id, drug_cui)
    SOURCE KEY (posting_id) REFERENCES Trials (PostingID)
    DESTINATION KEY (drug_cui) REFERENCES Drug (drug_cui)
    LABEL Uses
    PROPERTIES (posting_id, drug_cui),

  -- Trial → Status (HasStatus)
  clinical_trial.TrialStatus
    KEY (posting_id, status_id)
    SOURCE KEY (posting_id) REFERENCES Trials (PostingID)
    DESTINATION KEY (status_id) REFERENCES Status (status_id)
    LABEL HasStatus
    PROPERTIES (posting_id, status_id),

  -- Trial → Phase (InPhase)
  clinical_trial.TrialPhase
    KEY (posting_id, phase_id)
    SOURCE KEY (posting_id) REFERENCES Trials (PostingID)
    DESTINATION KEY (phase_id) REFERENCES Phase (phase_id)
    LABEL InPhase
    PROPERTIES (posting_id, phase_id),

  -- Disorder → Disorder (IsSubtypeOf)
  clinical_trial.DisorderHierarchy
    KEY (child_cui, parent_cui)
    SOURCE KEY (child_cui) REFERENCES Disorder (disorder_cui)
    DESTINATION KEY (parent_cui) REFERENCES Disorder (disorder_cui)
    LABEL IsSubtypeOf
    PROPERTIES (child_cui, parent_cui)
);