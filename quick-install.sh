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
# Use environment variables, or fallback to sensible defaults where applicable.
PROJECT_ID="${PROJECT_ID:-}"
BIGQUERY_LOCATION="${BIGQUERY_LOCATION:-us}"
GCS_LOCATION="${GCS_LOCATION:-us}"
DATASET_ID="${DATASET_ID:-clinical_trial_multiregion}"
# Note: BUCKET_DOCS and BUCKET_PROFILES depend on PROJECT_ID so they will be set after the check.
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

if [ -z "$PROJECT_ID" ]; then
  echo "Error: PROJECT_ID environment variable is required but not set."
  echo "Please set it before running this script:"
  echo "  export PROJECT_ID=\"your-gcp-project-id\""
  echo ""
  echo "Optional environment variables with defaults:"
  echo "  BIGQUERY_LOCATION=\"us\""
  echo "  GCS_LOCATION=\"us\""
  echo "  DATASET_ID=\"clinical_trial_multiregion\""
  echo "  BUCKET_DOCS=\"\${PROJECT_ID}-clinical-trials-docs\""
  echo "  BUCKET_PROFILES=\"\${PROJECT_ID}-patient-profiles\""
  exit 1
fi

# Set buckets now that PROJECT_ID is confirmed to be set
BUCKET_DOCS="${BUCKET_DOCS:-${PROJECT_ID}-clinical-trials-docs}"
BUCKET_PROFILES="${BUCKET_PROFILES:-${PROJECT_ID}-patient-profiles}"

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
  command -v python3 >/dev/null 2>&1 || { echo >&2 "python3 is required for parameterization but not installed. Aborting."; exit 1; }
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
  if gcloud services list --enabled --filter="config.name=$api" --project="$PROJECT_ID" | grep -q "$api"; then
    log "API $api is already enabled."
  else
    run_command "gcloud services enable $api --project=$PROJECT_ID"
  fi
}

create_bucket() {
  local bucket_name=$1
  if gcloud storage ls "gs://$bucket_name" >/dev/null 2>&1; then
    log "Bucket gs://$bucket_name already exists."
  else
    run_command "gcloud storage buckets create gs://$bucket_name --project=$PROJECT_ID --location=$GCS_LOCATION"
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

section_open "1. Authentication"

# Check if application default credentials exist and are valid
if gcloud auth application-default print-access-token >/dev/null 2>&1; then
  log "Application Default Credentials are valid. Skipping authentication."
else
  log "Application Default Credentials are not found or invalid. Starting authentication flow..."
  run_command "gcloud auth login"
  run_command "gcloud auth application-default login --quiet --scopes=\"openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/sqlservice.login,https://www.googleapis.com/auth/accounts.reauth\""
  run_command "gcloud auth application-default set-quota-project $PROJECT_ID"
fi

# Export ADC credentials so subsequent tools/scripts (like Python) use them
ADC_PATH="$(gcloud info --format="value(config.paths.global_config_dir)")/application_default_credentials.json"
export GOOGLE_APPLICATION_CREDENTIALS="$ADC_PATH"
log "Exported GOOGLE_APPLICATION_CREDENTIALS=$ADC_PATH"
section_close "Authentication"

section_open "2. Enabling APIs"
APIS="
aiplatform.googleapis.com
bigquery.googleapis.com
bigqueryconnection.googleapis.com
documentai.googleapis.com
storage.googleapis.com
"
for api in $APIS; do
  enable_api "$api"
done
section_close "APIs"

section_open "3. Setting up IAM"
create_sa "$SERVICE_ACCOUNT"
section_close "IAM"

section_open "4. Creating Storage Buckets"
create_bucket "$BUCKET_DOCS"
create_bucket "$BUCKET_PROFILES"
section_close "Storage"

section_open "5. Creating BigQuery Datasets"
create_dataset "$DATASET_ID"
section_close "BigQuery Datasets"

section_open "6. Setting up BigQuery Connections & IAM"
# Create AI Resources Connection
if bq ls --connection --project_id="$PROJECT_ID" --location="$BIGQUERY_LOCATION" | grep -q "cloud_ai_resources"; then
  log "Connection cloud_ai_resources already exists."
else
  run_command "bq mk --connection --project_id=$PROJECT_ID --location=$BIGQUERY_LOCATION --connection_type=CLOUD_RESOURCE cloud_ai_resources"
fi

# Extract Service Accounts and grant permissions
if [ "$EXECUTE" = true ]; then
  # Wait for the service account to be provisioned (it can take a few seconds after connection creation)
  SA_AI=""
  MAX_RETRIES=15
  RETRY_COUNT=0
  log "Waiting for BigQuery Connection Service Account to be provisioned..."
  
  while [ -z "$SA_AI" ] && [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    SA_AI=$(bq show --connection --project_id="$PROJECT_ID" --location="$BIGQUERY_LOCATION" --format=json cloud_ai_resources | grep -o 'bqcx-[^"]*' || true)
    if [ -z "$SA_AI" ]; then
      RETRY_COUNT=$((RETRY_COUNT+1))
      printf "."
      sleep 2
    fi
  done
  echo "" # Newline after the loading dots

  if [ -z "$SA_AI" ]; then
    warn "Failed to retrieve the Service Account for cloud_ai_resources after multiple attempts."
    echo "You may need to manually assign roles to the bqcx-* service account later."
  else
    log "Granting permissions to Connection SA: $SA_AI"
    for role in roles/aiplatform.user roles/storage.objectUser roles/documentai.viewer; do
      gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:$SA_AI" --role="$role" --quiet > /dev/null
    done
    log "Successfully applied IAM bindings to $SA_AI"
  fi
else
  echo "  [DRY RUN] Wait for Connection SA (bqcx-*) to be provisioned, then grant roles/aiplatform.user, roles/storage.objectUser, roles/documentai.viewer"
fi
section_close "Connections & IAM"

section_open "7. Loading Data & Tables"
# Upload local files to GCS
run_command "gcloud storage cp data/generated_patient_profiles/*.txt gs://$BUCKET_PROFILES/"
run_command "gcloud storage cp data/generated_clinical_trials_reports/new/*.pdf gs://$BUCKET_DOCS/" 2>/dev/null || warn "No PDF reports found in data/generated_clinical_trials_reports/new/"
section_close "Data Loading"

section_open "8. Generating Parameterized Pipelines"
# Update config.yaml with actual project specifics
if [ "$EXECUTE" = true ]; then
  cat << YAMLEOF > config.yaml
# Basic Google Cloud Info
project_id: "$PROJECT_ID"
dataset_id: "$DATASET_ID"
location: "$BIGQUERY_LOCATION"
connection_id: "cloud_ai_resources"

# Input Data Locations
patient_data_gcs_path: "gs://$BUCKET_PROFILES/*.txt"
clinical_reports_gcs_path: "gs://$BUCKET_DOCS/*.pdf"

# Advanced (Optional)
model_name: "cssr_reports_model"
YAMLEOF
  log "Updated config.yaml"
  run_command "python3 scripts/parameterize.py"
else
  echo "  [DRY RUN] Generate config.yaml and execute python3 scripts/parameterize.py"
fi
section_close "Parameterization Engine"

section_open "9. Deploying Unstructured Ingestion Pipelines"
PARAM_PROFILES_SQL="sql/Parameterized_Patient_Profiles.sql"
PARAM_TRIALS_SQL="sql/Parameterized_Clinical_Trials.sql"

if [ -f "$PARAM_PROFILES_SQL" ]; then
  run_command "bq query --use_legacy_sql=false < \"$PARAM_PROFILES_SQL\""
else
  warn "Generated SQL file $PARAM_PROFILES_SQL not found. Did the parameterization script fail?"
fi

if [ -f "$PARAM_TRIALS_SQL" ]; then
  run_command "bq query --use_legacy_sql=false < \"$PARAM_TRIALS_SQL\""
else
  warn "Generated SQL file $PARAM_TRIALS_SQL not found."
fi
section_close "Deploy Unstructured Ingestion Pipelines"

section_open "10. Setting up Clinical Trial Graph"
# Parameterize and deploy the clinical trial graph
PARAM_GRAPH_SQL="sql/Parameterized_setup_clinical_trial_graph.sql"

if [ "$EXECUTE" = true ]; then
  log "Parameterizing Clinical Trial Graph SQL..."
  sed -e "s/<PROJECT_ID>/$PROJECT_ID/g" \
      -e "s/<DATASET_ID>/$DATASET_ID/g" \
      sql/setup_clinical_trial_graph.sql > "$PARAM_GRAPH_SQL"

  if [ -f "$PARAM_GRAPH_SQL" ]; then
    run_command "bq query --use_legacy_sql=false < \"$PARAM_GRAPH_SQL\""
  else
    warn "Failed to generate parameterized SQL file $PARAM_GRAPH_SQL."
  fi
else
  echo "  [DRY RUN] Generate $PARAM_GRAPH_SQL and execute it using bq query."
fi
section_close "Clinical Trial Graph Setup"

printf "\n${BGREEN}Setup Complete!${NC}\n"
if [ "$EXECUTE" = true ]; then
  log "Your Google Cloud environment is now fully provisioned."
else
  warn "This was a dry run. No changes were made to GCP."
fi
