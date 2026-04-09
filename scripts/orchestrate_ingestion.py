from google.cloud import bigquery
import argparse
import sys

def run_ingestion(project_id: str, dataset_id: str, connection_id: str, patient_gcs_uri: str, trials_gcs_uri: str, model_name: str):
    """
    Triggers the BigQuery Stored Procedures to ingest unstructured clinical data from GCS.
    """
    client = bigquery.Client(project=project_id)

    print(f"Starting ingestion process for project: {project_id}, dataset: {dataset_id}...")

    # 1. Trigger Patient Profile Ingestion
    print(f"\n--- Ingesting Patient Profiles from {patient_gcs_uri} ---")
    patient_query = f"""
        CALL `{project_id}.{dataset_id}.IngestPatientProfiles`(
            '{patient_gcs_uri}', 
            '{connection_id}', 
            '{dataset_id}'
        );
    """
    try:
        query_job = client.query(patient_query)
        query_job.result()  # Waits for the job to complete
        print("✅ Patient Profile ingestion completed successfully.")
    except Exception as e:
        print(f"❌ Error during Patient Profile ingestion: {e}")
        sys.exit(1)

    # 2. Trigger Clinical Trial Reports Ingestion
    print(f"\n--- Ingesting Clinical Trial Reports from {trials_gcs_uri} ---")
    trial_query = f"""
        CALL `{project_id}.{dataset_id}.IngestClinicalTrials`(
            '{trials_gcs_uri}', 
            '{connection_id}', 
            '{dataset_id}',
            '{model_name}'
        );
    """
    try:
        query_job = client.query(trial_query)
        query_job.result()  # Waits for the job to complete
        print("✅ Clinical Trial Report ingestion completed successfully.")
    except Exception as e:
        print(f"❌ Error during Clinical Trial Report ingestion: {e}")
        sys.exit(1)

    print("\n🎉 All ingestion pipelines executed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Orchestrate unstructured data ingestion into BigQuery.")
    
    # Defaulting to the known dev project settings, but allowing overrides
    parser.add_argument("--project_id", type=str, default="meridian-dev-455515", help="GCP Project ID")
    parser.add_argument("--dataset_id", type=str, default="clinical_trial_multiregion", help="Target BigQuery Dataset")
    parser.add_argument("--connection_id", type=str, default="meridian-dev-455515.us.cloud_ai_resources", help="BigQuery Connection ID")
    
    # GCS paths
    parser.add_argument("--patient_gcs_uri", type=str, default="gs://meridian-dev-455515-patient-profiles/*.txt", help="GCS URI pattern for patient profiles")
    parser.add_argument("--trials_gcs_uri", type=str, default="gs://cssr_reports_trials/april2_generation/*.pdf", help="GCS URI pattern for clinical trial reports")
    
    # Model
    parser.add_argument("--model_name", type=str, default="meridian-dev-455515.clinical_trial_multiregion.cssr_reports_model", help="Full path to the BQML Document Processing Model")

    args = parser.parse_args()

    run_ingestion(
        project_id=args.project_id,
        dataset_id=args.dataset_id,
        connection_id=args.connection_id,
        patient_gcs_uri=args.patient_gcs_uri,
        trials_gcs_uri=args.trials_gcs_uri,
        model_name=args.model_name
    )
