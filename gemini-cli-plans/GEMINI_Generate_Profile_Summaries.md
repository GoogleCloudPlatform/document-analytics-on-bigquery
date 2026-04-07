You're a Data Scientist working on a Clinical Trial use case.                                                                                                        
                                                                                                                                                                        
   Your goal is to synthetically generate patient data to enable answering questions around Disorders they have, Trials they could enlist and based on their symptoms   
   and demographic information (age, sex, place of residency, etc).                                                                                                     
                                                                                                                                                                        
   For Information Gathering: You will use the clinical trial data you can find on the json files from @bigquery_exports/ClinicalTrialDenormalizedData-partaa.json to   
   @bigquery_exports/ClinicalTrialDenormalizedData-partaf.json (from *-partaa.json to *-partaf.json - total of 6 files) and the google_web_search tool to find          
   information on a diverse set of real-world clinical trials, covering various diseases, therapeutic areas, and geographical locations.                                
                                                                                                                                                                        
   I'm giving you three examples that I previously generated manually.                                                                                                  
                                                                                                                                                                        
   Examples:                                                                                                                                                            
   Profile 1: Boby Liam (Pediatrics/Infectious Disease)                                                                                                                 
   Condition: High Risk of Severe Respiratory Syncytial Virus (RSV)                                                                                                     
   Patient Context: 6-month-old male born prematurely (30 weeks gestation) with chronic lung disease of prematurity.                                                    
   Clinical Detail: Entering his first RSV season; requires passive immunization to prevent severe lower respiratory tract infection.                                   
   Trial ID: NCT06851806 (Study of Palivizumab in High-Risk Children)                                                                                                   
   Reason for Qualification: Meets the age and high-risk clinical criteria (prematurity + chronic lung disease) for palivizumab prophylaxis.                            
   Profile 2: Robert Manning (Respiratory/Cardiovascular)                                                                                                               
   Condition: Severe Asthma with Cardiovascular Monitoring                                                                                                              
   Patient Context: 62-year-old male with a 20-year history of eosinophilic asthma and recent minor arrhythmias.                                                        
   Clinical Detail: Currently prescribed Tezepelumab (Tezspire) for asthma management; requires long-term safety monitoring for Major Adverse Cardiovascular Events     
   (MACE).                                                                                                                                                              
   Trial ID: NCT06951867 (Tezspire Cardiac Events PASS)                                                                                                                 
   Reason for Qualification: Patient is an active user of Tezepelumab in a real-world setting with a known cardiovascular history, fitting the Post-Authorization       
   Safety Study (PASS) cohort.                                                                                                                                          
   Profile 3: Elena Vargas (Pulmonology)                                                                                                                                
   Condition: Chronic Obstructive Pulmonary Disease (COPD)                                                                                                              
   Patient Context: 68-year-old female, former smoker, experiencing frequent exacerbations despite dual therapy (LAMA/LABA).                                            
   Clinical Detail: CAT score of 22; FEV1 < 50% predicted. Recently switched to triple therapy (Budesonide/Glycopyrronium/Formoterol).                                  
   Trial ID: NCT06712563 (BGF Pooled Analysis in Routine Care)                                                                                                          
   Reason for Qualification: Meets criteria for "routine care" patients treated with BGF triple therapy for symptomatic COPD management.                                
                                                                                                                                                                        
                                                                                                                                                                        
   Generate other 50 profiles and append to file @generated_patient_profiles/aggregated_summarized_patient_profiles.txt. Make sure no duplicates are present.           
                                                                                                                                                                        
   Before start executing, show me your plan and wait for my approval.