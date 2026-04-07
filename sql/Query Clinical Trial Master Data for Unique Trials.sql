-- Query the denormalized table `meridian-dev-455515.clinical_trial.ClinicalTrialMasterData`, only return one row per PostingID. There are multiple rows with the same PostingID, other columns may change. I just need one row per PostingID.

SELECT
*
FROM
  `meridian-dev-455515`.`clinical_trial`.`ClinicalTrialMasterData` AS t
QUALIFY
  ROW_NUMBER() OVER (PARTITION BY t.PostingID ORDER BY 1) = 1
