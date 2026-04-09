#!/usr/bin/env sh
#
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script automates the setup of the Document Analytics on BigQuery project.
# It is idempotent and operates in "Dry Run" mode by default.
# Use --execute to apply changes.

set -o errexit
set -o nounset

# --- CONFIGURATION ---
PROJECT_ID=$(gcloud config get-value project)
LOCATION="us-central1" # Default location
DATASET_ID="clinical_trial_demo"
BUCKET_DOCS="${PROJECT_ID}-clinical-trials-docs"
BUCKET_PROFILES="${PROJECT_ID}-patient-profiles"
BUCKET_REPORTS="${PROJECT_ID}-cssr-reports"
SERVICE_ACCOUNT="vertex-pipelines-sa"

# --- DISPLAY HELPERS ---
CYAN='\033[0;36m'
BCYAN='\033[1;36m'
BGREEN='\033[1;32m'
BYELLOW='\033[1;33m'
NC='\033[0m' # No Color

DIVIDER=$(printf '%*s' "$(tput cols 2>/dev/null || echo 80)" '' | tr ' ' '-')

section_open() {
  printf "\n${BCYAN}%s${NC}\n" "$1"
  echo "$DIVIDER"
}

section_close() {
  printf "${CYAN}Section Complete: %s${NC}\n" "$1"
}

log() {
  printf "${BGREEN}[LOG]${NC} %s\n" "$1"
}

warn() {
  printf "${BYELLOW}[WARN]${NC} %s\n" "$1"
}

# --- ARGUMENT PARSING ---
EXECUTE=false
for arg in "$@"; do
  if [ "$arg" = "--execute" ]; then
    EXECUTE=true
  fi
done

if [ "$EXECUTE" = false ]; then
  warn "DRY RUN MODE: Commands will be printed but NOT executed. Use --execute to apply."
fi

# --- DEPENDENCY CHECK ---
check_dependencies() {
  command -v gcloud >/dev/null 2>&1 || { echo >&2 "gcloud CLI is required but not installed. Aborting."; exit 1; }
  command -v bq >/dev/null 2>&1 || { echo >&2 "bq CLI is required but not installed. Aborting."; exit 1; }
}

# --- IDEMPOTENT HELPERS ---
run_command() {
  local cmd=$1
  if [ "$EXECUTE" = true ]; then
    log "Executing: $cmd"
    eval "$cmd"
  else
    echo "  [DRY RUN] $cmd"
  fi
}

enable_api() {
  local api=$1
  if gcloud services list --enabled --filter="name:$api" --project="$PROJECT_ID" | grep -q "$api"; then
    log "API $api is already enabled."
  else
    run_command "gcloud services enable $api --project=$PROJECT_ID"
  fi
}

create_bucket() {
  local bucket_name=$1
  if gsutil ls -b "gs://$bucket_name" >/dev/null 2>&1; then
    log "Bucket gs://$bucket_name already exists."
  else
    run_command "gsutil mb -p $PROJECT_ID -l $LOCATION gs://$bucket_name"
  fi
}

create_dataset() {
  local ds=$1
  if bq ls --project_id="$PROJECT_ID" | grep -q "$ds"; then
    log "Dataset $ds already exists."
  else
    run_command "bq mk --dataset --project_id=$PROJECT_ID $ds"
  fi
}

create_sa() {
  local sa_name=$1
  if gcloud iam service-accounts list --filter="email:$sa_name@$PROJECT_ID.iam.gserviceaccount.com" --project="$PROJECT_ID" | grep -q "$sa_name"; then
    log "Service account $sa_name already exists."
  else
    run_command "gcloud iam service-accounts create $sa_name --display-name='$sa_name' --project=$PROJECT_ID"
  fi
}

# --- MAIN EXECUTION ---
check_dependencies

section_open "1. Enabling APIs"
APIS="
aiplatform.googleapis.com
analyticshub.googleapis.com
artifactregistry.googleapis.com
bigquery.googleapis.com
bigqueryconnection.googleapis.com
bigquerydatatransfer.googleapis.com
calendar-json.googleapis.com
chat.googleapis.com
cloudaicompanion.googleapis.com
cloudbuild.googleapis.com
cloudfunctions.googleapis.com
cloudkms.googleapis.com
cloudresourcemanager.googleapis.com
cloudscheduler.googleapis.com
compute.googleapis.com
dataflow.googleapis.com
dataform.googleapis.com
datalineage.googleapis.com
dataplex.googleapis.com
docs.googleapis.com
documentai.googleapis.com
drive.googleapis.com
geminidataanalytics.googleapis.com
gmail.googleapis.com
iam.googleapis.com
iamcredentials.googleapis.com
logging.googleapis.com
monitoring.googleapis.com
notebooks.googleapis.com
pubsub.googleapis.com
secretmanager.googleapis.com
serviceusage.googleapis.com
sheets.googleapis.com
slides.googleapis.com
storage-api.googleapis.com
storage-component.googleapis.com
storage.googleapis.com
visionai.googleapis.com
"
for api in $APIS; do
  enable_api "$api"
done
section_close "APIs"

section_open "2. Setting up IAM"
create_sa "$SERVICE_ACCOUNT"
section_close "IAM"

section_open "3. Creating Storage Buckets"
create_bucket "$BUCKET_DOCS"
create_bucket "$BUCKET_PROFILES"
create_bucket "$BUCKET_REPORTS"
section_close "Storage"

section_open "4. Creating BigQuery Datasets"
create_dataset "clinical_trial"
create_dataset "clinical_trial_demo"
create_dataset "clinical_trial_multiregion"
section_close "BigQuery Datasets"

section_open "5. Setting up BigQuery Connections & IAM"
# Create LLM Connection
if bq ls --connection --project_id="$PROJECT_ID" --location=us-central1 | grep -q "llm-connection"; then
  log "Connection llm-connection already exists."
else
  run_command "bq mk --connection --project_id=$PROJECT_ID --location=us-central1 --connection_type=CLOUD_RESOURCE llm-connection"
fi

# Create AI Resources Connection
if bq ls --connection --project_id="$PROJECT_ID" --location=us | grep -q "cloud_ai_resources"; then
  log "Connection cloud_ai_resources already exists."
else
  run_command "bq mk --connection --project_id=$PROJECT_ID --location=us --connection_type=CLOUD_RESOURCE cloud_ai_resources"
fi

# Extract Service Accounts and grant permissions
if [ "$EXECUTE" = true ]; then
  SA_LLM=$(bq show --connection --project_id="$PROJECT_ID" --location=us-central1 --format=json llm-connection | grep -o 'bqcx-[^"]*')
  SA_AI=$(bq show --connection --project_id="$PROJECT_ID" --location=us --format=json cloud_ai_resources | grep -o 'bqcx-[^"]*')
  
  log "Granting permissions to Connection SAs: $SA_LLM, $SA_AI"
  for role in roles/aiplatform.user roles/storage.objectUser; do
    gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:$SA_LLM" --role="$role" --quiet > /dev/null
    gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:$SA_AI" --role="$role" --quiet > /dev/null
  done
  gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:$SA_AI" --role="roles/documentai.viewer" --quiet > /dev/null
else
  echo "  [DRY RUN] Extract Connection SAs and grant roles/aiplatform.user, roles/storage.objectUser, roles/documentai.viewer"
fi
section_close "Connections & IAM"

section_open "6. Loading Data & Tables"
# Load all AVRO files into clinical_trial dataset
for avro_file in ./sql/tables/*.avro; do
  if [ -f "$avro_file" ]; then
    table_name=$(basename "$avro_file" .avro)
    run_command "bq load --source_format=AVRO --project_id=$PROJECT_ID clinical_trial.$table_name '$avro_file'"
  fi
done

# Upload local files to GCS
# Assuming profiles are in data/generated_patient_profiles and reports are in data/generated_clinical_trials_reports
run_command "gsutil -m cp data/generated_patient_profiles/*.txt gs://$BUCKET_PROFILES/"
run_command "gsutil -m cp data/generated_clinical_trials_reports/new/*.pdf gs://$BUCKET_DOCS/" 2>/dev/null || warn "No PDF reports found in data/generated_clinical_trials_reports/new/"
section_close "Data Loading"

section_open "7. Creating Models & Knowledge Graph"
GRAPH_SQL="sql/setup_clinical_trial_graph.sql"
if [ -f "$GRAPH_SQL" ]; then
  run_command "bq query --use_legacy_sql=false < '$GRAPH_SQL'"
else
  warn "Graph setup SQL file $GRAPH_SQL not found."
fi
section_close "Models & Graph"

section_open "8. Executing Analytical Queries"
# Run the denormalized data query
SQL_FILE="sql/Clinical TRial Denormalized Data.sql"
if [ -f "$SQL_FILE" ]; then
  run_command "bq query --use_legacy_sql=false < '$SQL_FILE'"
else
  warn "SQL file $SQL_FILE not found."
fi

# Run the patient profile parsing query
PARSE_PROFILES_SQL="sql/Parse Patient Profiles.sql"
if [ -f "$PARSE_PROFILES_SQL" ]; then
  run_command "bq query --use_legacy_sql=false < '$PARSE_PROFILES_SQL'"
else
  warn "SQL file $PARSE_PROFILES_SQL not found."
fi
section_close "Analytical Queries"

printf "\n${BGREEN}Setup Complete!${NC}\n"
if [ "$EXECUTE" = false ]; then
  warn "This was a dry run. No changes were made to GCP."
fi

# --- APPENDIX: MANUAL INFRASTRUCTURE COMMANDS ---
# The following commands can be used to manually verify and provision resources:
# gcloud storage buckets create gs://${PROJECT_ID}-patient-profiles
# gcloud storage rsync data/generated_patient_profiles gs://${PROJECT_ID}-patient-profiles/ --recursive
