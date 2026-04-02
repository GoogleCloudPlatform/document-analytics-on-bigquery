SELECT 
t.* EXCEPT (embedding, char_count), 
d.* EXCEPT(disorder_cui, definitionEmbedding),
dr.* EXCEPT(drug_cui, preferred_name, semantic_type),
dr.preferred_name as drug_preferred_name, 
dr.semantic_type as drug_semantic_type,
tc.* EXCEPT(criteria_id),
tp.* EXCEPT(posting_id),
s.* EXCEPT(status_id)
FROM `meridian-dev-455515.clinical_trial.Trials` t
INNER JOIN `meridian-dev-455515.clinical_trial.TrialDisorder` td 
ON td.posting_id = t.PostingID
INNER JOIN `meridian-dev-455515.clinical_trial.Disorder` d
ON td.disorder_cui = d.disorder_cui
INNER JOIN `meridian-dev-455515.clinical_trial.TrialDrug` tdr
ON tdr.posting_id = t.PostingID
INNER JOIN `meridian-dev-455515.clinical_trial.Drug` dr
ON dr.drug_cui = tdr.drug_cui
INNER JOIN `meridian-dev-455515.clinical_trial.TrialRequires` treq
ON treq.posting_id = t.PostingID
INNER JOIN `meridian-dev-455515.clinical_trial.TrialCriteria` tc
ON tc.criteria_id = treq.criteria_id
INNER JOIN `meridian-dev-455515.clinical_trial.TrialPhase` tp
ON tp.posting_id = t.PostingID
INNER JOIN `meridian-dev-455515.clinical_trial.TrialStatus` ts
ON ts.posting_id = t.PostingID
INNER JOIN `meridian-dev-455515.clinical_trial.Status` s
ON s.status_id = ts.status_id
