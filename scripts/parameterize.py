import re
import os

def load_config(config_path='config.yaml'):
    config = {}
    with open(config_path, 'r') as file:
        for line in file:
            line = line.strip()
            # Ignore comments and empty lines
            if line.startswith('#') or not line:
                continue
            if ':' in line:
                key, value = line.split(':', 1)
                # Clean up quotes and whitespace
                value = value.strip().strip('"').strip("'")
                config[key.strip()] = value
    return config

def parameterize_patient_profiles(config):
    with open('sql/Parse Patient Profiles.sql', 'r') as f:
        sql = f.read()

    # robust escaping
    sql_escaped = sql.replace('\\', '\\\\').replace('"', '\\"').replace("'''", "\\'\\'\\'")

    project_id = config['project_id']
    dataset_id = config['dataset_id']
    full_connection = f"{project_id}.{config['location']}.{config['connection_id']}"
    gcs_path = config['patient_data_gcs_path']

    # Hardcoded knowledge replacements
    sql_escaped = re.sub(r'`meridian-dev-455515\.clinical_trial_multiregion\.patient_profiles`', f'`{dataset_id}.patient_profiles`', sql_escaped)
    sql_escaped = re.sub(r'`clinical_trial_multiregion\.patient_profiles`', f'`{dataset_id}.patient_profiles`', sql_escaped)
    sql_escaped = re.sub(r'`clinical_trial_multiregion\.Patients`', f'`{dataset_id}.Patients`', sql_escaped)
    
    sql_escaped = re.sub(r'`meridian-dev-455515\.us\.cloud_ai_resources`', f'`{full_connection}`', sql_escaped)
    sql_escaped = re.sub(r"'meridian-dev-455515\.us\.cloud_ai_resources'", f"'{full_connection}'", sql_escaped)
    sql_escaped = re.sub(r"'us\.cloud_ai_resources'", f"'{full_connection}'", sql_escaped)
    
    sql_escaped = re.sub(r"\['gs://meridian-dev-455515-patient-profiles/\*\.txt'\]", f"['{gcs_path}']", sql_escaped)

    stmt1 = sql_escaped.split("CREATE OR REPLACE TABLE")[0].strip()
    stmt2 = "CREATE OR REPLACE TABLE" + sql_escaped.split("CREATE OR REPLACE TABLE")[1].strip()

    proc_ddl = f"""CREATE OR REPLACE PROCEDURE `{dataset_id}.IngestPatientProfiles`()
BEGIN
    EXECUTE IMMEDIATE \"\"\"{stmt1}\"\"\";
    EXECUTE IMMEDIATE \"\"\"{stmt2}\"\"\";
END;
"""
    with open('sql/Parameterized_Patient_Profiles.sql', 'w') as f:
        f.write(proc_ddl)

def parameterize_clinical_trials(config):
    with open('sql/Parse Clinical Trials Report PDF files.sql', 'r') as f:
        sql = f.read()

    # robust escaping
    sql_escaped = sql.replace('\\', '\\\\').replace('"', '\\"').replace("'''", "\\'\\'\\'")

    project_id = config['project_id']
    dataset_id = config['dataset_id']
    full_connection = f"{project_id}.{config['location']}.{config['connection_id']}"
    gcs_path = config['clinical_reports_gcs_path']
    model_name = config.get('model_name', 'cssr_reports_model')
    full_model_path = f"{dataset_id}.{model_name}"

    # Hardcoded knowledge replacements
    sql_escaped = re.sub(r'`meridian-dev-455515\.clinical_trial_multiregion\.cssr_reports_parsed_pdf`', f'`{dataset_id}.cssr_reports_parsed_pdf`', sql_escaped)
    sql_escaped = re.sub(r'`clinical_trial_multiregion\.cssr_reports_parsed_pdf`', f'`{dataset_id}.cssr_reports_parsed_pdf`', sql_escaped)
    sql_escaped = re.sub(r'clinical_trial_multiregion\.cssr_reports_parsed_pdf', f'`{dataset_id}.cssr_reports_parsed_pdf`', sql_escaped)
    
    sql_escaped = re.sub(r'`clinical_trial_multiregion\.cssr_reports_chunked_pdf`', f'`{dataset_id}.cssr_reports_chunked_pdf`', sql_escaped)
    sql_escaped = re.sub(r'clinical_trial_multiregion\.cssr_reports_chunked_pdf', f'`{dataset_id}.cssr_reports_chunked_pdf`', sql_escaped)
    
    sql_escaped = re.sub(r'`clinical_trial_multiregion\.cssr_reports`', f'`{dataset_id}.cssr_reports`', sql_escaped)
    
    sql_escaped = re.sub(r'`clinical_trial_multiregion\.ClinicalTrialMasterData`', f'`{dataset_id}.ClinicalTrialMasterData`', sql_escaped)
    
    sql_escaped = re.sub(r'`clinical_trial_multiregion\.cssr_reports_model`', f'`{full_model_path}`', sql_escaped)
    sql_escaped = re.sub(r'`meridian-dev-455515\.us\.cloud_ai_resources`', f'`{full_connection}`', sql_escaped)
    sql_escaped = re.sub(r"'us\.cloud_ai_resources'", f"'{full_connection}'", sql_escaped)
    sql_escaped = re.sub(r"\['gs://cssr_reports_trials/april2_generation/\*\.pdf'\]", f"['{gcs_path}']", sql_escaped)

    stmts = sql_escaped.split("CREATE OR REPLACE")
    
    stmt1 = "CREATE OR REPLACE" + stmts[1].strip()
    stmt2 = "CREATE OR REPLACE" + stmts[2].strip()
    stmt3 = "CREATE OR REPLACE" + stmts[3].strip()
    stmt4 = "CREATE OR REPLACE" + stmts[4].strip()

    proc_ddl = f"""CREATE OR REPLACE PROCEDURE `{dataset_id}.IngestClinicalTrials`()
BEGIN
    EXECUTE IMMEDIATE \"\"\"{stmt1}\"\"\";
    EXECUTE IMMEDIATE \"\"\"{stmt2}\"\"\";
    EXECUTE IMMEDIATE \"\"\"{stmt3}\"\"\";
    EXECUTE IMMEDIATE \"\"\"{stmt4}\"\"\";
END;
"""
    with open('sql/Parameterized_Clinical_Trials.sql', 'w') as f:
        f.write(proc_ddl)

if __name__ == "__main__":
    if not os.path.exists('config.yaml'):
        print("Error: config.yaml not found. Please create it first.")
        exit(1)
        
    config = load_config()
    parameterize_patient_profiles(config)
    parameterize_clinical_trials(config)
    print("Successfully generated Parameterized_Patient_Profiles.sql and Parameterized_Clinical_Trials.sql using config.yaml")
