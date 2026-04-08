SELECT *
FROM `clinical_trial.Disorder`
WHERE definitionEmbedding IS NOT NULL 
  AND ARRAY_LENGTH(definitionEmbedding) = 768
