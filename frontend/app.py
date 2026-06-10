import json
import os

import streamlit as st
import yaml
from google.cloud import bigquery  # noqa: E402
from google.cloud import storage  # noqa: E402

# Disable mTLS client certificate provider to avoid status code -11 error
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"

# Set page configuration for a premium analytics experience
st.set_page_config(
    page_title="Zero-Copy RAG & Knowledge Graph Orchestration on BigQuery",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Load styling from style.css
css_file = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_file):
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Helper: Load config defaults
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "app_config.yaml")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            pass

    # Fallback to example configuration template
    example_path = os.path.join(os.path.dirname(__file__), "app_config.example.yaml")
    if os.path.exists(example_path):
        try:
            with open(example_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            pass
    return {}


# Helper: Save config defaults (always writes to app_config.yaml to avoid editing template)
def save_config(updates):
    config_path = os.path.join(os.path.dirname(__file__), "app_config.yaml")
    example_path = os.path.join(os.path.dirname(__file__), "app_config.example.yaml")

    current_config = {}
    # Read existing app_config.yaml, or fall back to template as initial state
    for path in [example_path, config_path]:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    current_config.update(yaml.safe_load(f) or {})
            except Exception:
                pass

    changed = False
    for k, v in updates.items():
        if current_config.get(k) != v:
            current_config[k] = v
            changed = True
    if changed:
        try:
            with open(config_path, "w") as f:
                yaml.safe_dump(current_config, f)
        except Exception:
            pass


config = load_config()


# Helper: Get BigQuery Client
@st.cache_resource
def get_bq_client(project_id):
    try:
        # Default authentication uses active environment credentials
        return bigquery.Client(project=project_id)
    except Exception as e:
        st.sidebar.error(f"Authentication failed: {str(e)}")
        return None


# Helper: Get GCS Connection ID Format
def get_full_connection_id(conn_id, proj_id, loc):
    if not conn_id:
        return ""
    if conn_id.startswith("projects/"):
        return conn_id
    return f"projects/{proj_id}/locations/{loc}/connections/{conn_id}"


# Helper: Check if BigQuery Table or View exists
def check_table_exists(project, dataset, table):
    if not client:
        return False
    try:
        table_ref = client.dataset(dataset, project=project).table(table)
        client.get_table(table_ref)
        return True
    except Exception:
        return False


# Sidebar layout
st.sidebar.image(
    "https://www.gstatic.com/images/branding/gcpiconscolors/bigquery/v1/32px.svg",
    width=40,
)
st.sidebar.title("R&D Data Research")

# Clean placeholder resolution and fallback to environment variable for Cloud Run deployment
default_project = config.get("project_id", "")
if default_project == "<PROJECT_ID>" or not default_project:
    default_project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")

with st.sidebar.expander("⚙️ Configuration", expanded=False):
    project_id = st.text_input(
        "GCP Project ID", value=default_project, placeholder="Enter your GCP Project ID"
    )
    dataset_id = st.text_input(
        "BigQuery Dataset ID",
        value=config.get("dataset_id", "clinical_trial_multiregion"),
    )
    location = st.text_input("GCP Location", value=config.get("location", "us"))

    # Dynamic default bucket naming
    proj = project_id if project_id else "your-gcp-project"
    default_bucket_name = config.get("bucket_name", f"{proj}-clinical-trials-docs")
    bucket_name = st.text_input("GCS Bucket Name", value=default_bucket_name)
    folder_name = st.text_input("GCS Folder Name", value=config.get("folder_name", ""))
    connection_id = st.text_input(
        "Cloud AI Connection ID",
        value=config.get("connection_id", "cloud_ai_resources"),
    )

    table_name = st.text_input(
        "Master Table Name",
        value=config.get("table_name", "ClinicalTrialMasterData_embedded2"),
    )
    table_2_name = st.text_input(
        "Chunks Table Name", value=config.get("table_2_name", "ClinicalTrialChunks")
    )
    graph_name = st.text_input(
        "Property Graph Name", value=config.get("graph_name", "clinical_trial_graph")
    )
    vector_index_name = st.text_input(
        "Vector Index Name",
        value=config.get("vector_index_name", "clinical_trial_vector_index"),
    )
    docai_endpoint = st.text_input(
        "Document AI Endpoint",
        value=config.get("docai_endpoint", "gemini-2.5-flash"),
        help=(
            "Endpoint URL for AI.PARSE_DOCUMENT (e.g. "
            "projects/YOUR_PROJECT/locations/us/processors/YOUR_PROCESSOR_ID)"
        ),
    )

    # Save updates back to config.yaml dynamically
    updates = {
        "project_id": project_id,
        "dataset_id": dataset_id,
        "location": location,
        "bucket_name": bucket_name,
        "folder_name": folder_name,
        "connection_id": connection_id,
        "table_name": table_name,
        "table_2_name": table_2_name,
        "graph_name": graph_name,
        "vector_index_name": vector_index_name,
        "docai_endpoint": docai_endpoint,
    }

    config_updates = {}
    for k, v in updates.items():
        if config.get(k) != v:
            config_updates[k] = v

    if config_updates:
        save_config(config_updates)
        config.update(config_updates)

# Connection Status & Testing
client = None
connection_valid = False

if project_id:
    client = get_bq_client(project_id)
    if client:
        # Simple health check to verify access
        if st.sidebar.button("Test Connection"):
            with st.sidebar.spinner("Connecting..."):
                try:
                    # Test query
                    test_query = "SELECT 1"
                    query_job = client.query(test_query)
                    query_job.result()
                    st.sidebar.success("✅ Connection Successful!")
                    connection_valid = True
                except Exception as e:
                    st.sidebar.error(f"❌ Connection failed: {str(e)}")
else:
    st.sidebar.warning("Please configure your GCP Project ID in the sidebar.")

# Steps Navigation Menu
st.sidebar.markdown("---")
st.sidebar.subheader("Navigation Steps")
step_options = [
    "📊 Summary & Overview",
    "0️⃣ Step 0: Documents in GCS",
    "1️⃣ Step 1: Generate Object Table",
    "2️⃣ Step 2: Define Full Schema",
    "3️⃣ Step 3: Populate Full Table",
    "4️⃣ Step 4: AI.Search (Semantic & Hybrid)",
    "5️⃣ Step 5: Parse Documents (AI.PARSE_DOCUMENT)",
    "6️⃣ Step 6: Cross-Column Hybrid Search",
    "7️⃣ Step 7: Graph Generation & Traversal",
    "8️⃣ Step 8: Visualize the Graph",
    "9️⃣ Step 9: Advanced Graph Traversal",
    "🔟 Step 10: Scale - Vector Index",
]

if "selected_step" not in st.session_state:
    st.session_state.selected_step = "📊 Summary & Overview"

if st.session_state.selected_step not in step_options:
    st.session_state.selected_step = "📊 Summary & Overview"

default_idx = step_options.index(st.session_state.selected_step)
selected_step = st.sidebar.radio("Go to step:", step_options, index=default_idx)
st.session_state.selected_step = selected_step

# Helper for full connection path
full_connection_id = get_full_connection_id(connection_id, project_id, location)

# App Header
st.markdown(
    '<div class="main-header">Zero-Copy RAG & Knowledge Graph Orchestration on BigQuery</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Clinical Trial & Discovery Drug Analysis [Healthcare]</div>',
    unsafe_allow_html=True,
)

# Track session state step result
if (
    "current_step" not in st.session_state
    or st.session_state.current_step != selected_step
):
    st.session_state.current_step = selected_step
    st.session_state.step_result = None


# Helper to run BQ query and cache result
def run_bq_query(query, job_config=None):
    if not client:
        st.error("BigQuery client is not configured. Please set the GCP Project ID.")
        return None
    with st.spinner("Executing query..."):
        try:
            query_job = client.query(query, job_config=job_config)
            df = query_job.to_dataframe()
            st.session_state.step_result = df
            return df
        except Exception as e:
            err_msg = str(e)
            st.error(f"Error executing query: {err_msg}")

            # Show friendly assistance instructions for signature errors
            if (
                "Named argument mode not found in signature for call to function AI.SEARCH"
                in err_msg
            ):
                st.info(
                    "💡 **Self-Service Guide: Resolving AI.SEARCH Mode Error**\n\n"
                    "The `mode => 'hybrid'` argument is a preview feature in BigQuery. If you get a signature error, "
                    "your project's region does not support the preview hybrid mode parameter yet. Please change "
                    "the **Search Mode** in the settings to **semantic** and execute again."
                )
            elif (
                "Named argument lexical_search_columns not found in signature for call to function VECTOR_SEARCH"
                in err_msg
            ):
                st.info(
                    "💡 **Self-Service Guide: Resolving VECTOR_SEARCH Lexical Columns Error**\n\n"
                    "The `lexical_search_columns` argument is a preview feature in BigQuery. If you get a "
                    "signature error, your project's region does not support this preview feature yet. Please "
                    "change the **Search Type** in the settings to **Pure Vector Search** and execute again."
                )
            return None


# ----------------------------------------------------
# STEP 0: Documents in GCS
# ----------------------------------------------------
if selected_step.startswith("📊"):
    st.markdown(
        """
        <div class="glass-container">
            <h3 style="margin-top: 0; color: #38bdf8; font-weight: 700; font-size: 1.5rem;">🔬 Demo Overview</h3>
            <p style="line-height: 1.6; font-size: 1.05rem; margin-bottom: 0;">
                Welcome to the <strong>Healthcare Document Analytics & Zero-Copy RAG</strong> solution! This interactive demo showcases how to ingest, enrich, search, and traverse unstructured clinical study summary reports (CSSR) and patient profiles directly within BigQuery without moving or copying raw data. By integrating Document AI, Gemini, and BigQuery Graph, we transform unstructured PDFs into a structured Knowledge Graph for complex semantic and relational searches.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("### 🔑 Key Pillars of the Architecture")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="metric-card" style="height: 100%;">
                <div class="metric-title" style="color: #38bdf8;">📂 In-Place Storage</div>
                <div class="metric-value" style="font-size: 1.25rem; margin-bottom: 0.5rem; color: var(--card-value);">Zero-Copy Ingestion</div>
                <p style="color: var(--card-text); font-size: 0.9rem; line-height: 1.5; margin: 0;">
                    Raw PDF clinical trials and patient records remain securely in Google Cloud Storage. BigQuery Object Tables provide direct metadata access without duplicates.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="metric-card" style="height: 100%;">
                <div class="metric-title" style="color: #34d399;">🧠 In-Warehouse AI</div>
                <div class="metric-value" style="font-size: 1.25rem; margin-bottom: 0.5rem; color: var(--card-value);">Gemini Enrichment</div>
                <p style="color: var(--card-text); font-size: 0.9rem; line-height: 1.5; margin: 0;">
                    Uses native BigQuery AI functions (<code>AI.GENERATE</code> and <code>AI.PARSE_DOCUMENT</code>) to extract structured data from documents and compute text embeddings.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="metric-card" style="height: 100%;">
                <div class="metric-title" style="color: #a78bfa;">🕸️ Relational Graph</div>
                <div class="metric-value" style="font-size: 1.25rem; margin-bottom: 0.5rem; color: var(--card-value);">BigQuery Graph</div>
                <p style="color: var(--card-text); font-size: 0.9rem; line-height: 1.5; margin: 0;">
                    Connects clinical trials, drugs, and disorders into a unified Property Graph. Enables multi-hop traversal pipelines using Graph Query Language (GQL).
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### 🗺️ Navigation Roadmap")
    
    roadmap_html = """
    <div style="background-color: var(--roadmap-bg); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--roadmap-border);">
        <table style="width: 100%; border-collapse: collapse; font-family: inherit; color: var(--text-color);">
            <thead>
                <tr style="border-bottom: 2px solid var(--roadmap-header-border);">
                    <th style="text-align: left; padding: 0.75rem; color: #38bdf8; font-weight: 600;">Phase</th>
                    <th style="text-align: left; padding: 0.75rem; color: #38bdf8; font-weight: 600;">Step</th>
                    <th style="text-align: left; padding: 0.75rem; color: #38bdf8; font-weight: 600;">Core Concept</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid var(--roadmap-border);">
                    <td style="padding: 0.75rem;"><span class="badge badge-info">1. Setup</span></td>
                    <td style="padding: 0.75rem;"><strong>Steps 0 - 2</strong></td>
                    <td style="padding: 0.75rem; color: var(--roadmap-text);">Explore GCS PDFs, create BigQuery Object Tables, and define the master table schema with automatic embeddings.</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--roadmap-border);">
                    <td style="padding: 0.75rem;"><span class="badge badge-warning">2. Ingest</span></td>
                    <td style="padding: 0.75rem;"><strong>Steps 3 & 5</strong></td>
                    <td style="padding: 0.75rem; color: var(--roadmap-text);">Populate structured data using Vertex AI Gemini models and Layout Parser Document AI chunking.</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--roadmap-border);">
                    <td style="padding: 0.75rem;"><span class="badge badge-success">3. Retrieve</span></td>
                    <td style="padding: 0.75rem;"><strong>Steps 4, 6 & 10</strong></td>
                    <td style="padding: 0.75rem; color: var(--roadmap-text);">Perform semantic & hybrid vector search, cross-column lookups, and scale querying with IVF Vector Indexes.</td>
                </tr>
                <tr>
                    <td style="padding: 0.75rem;"><span class="badge badge-success">4. Graph</span></td>
                    <td style="padding: 0.75rem;"><strong>Steps 7 - 9</strong></td>
                    <td style="padding: 0.75rem; color: var(--roadmap-text);">Establish Property Graphs, visualize node-edge relationships, and traverse multi-hop paths using GQL.</td>
                </tr>
            </tbody>
        </table>
    </div>
    """
    st.markdown(roadmap_html, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="display: flex; justify-content: center; margin-top: 1rem; margin-bottom: 2rem;">
            <div class="glow-btn">
        """,
        unsafe_allow_html=True,
    )
    if st.button("Start Interactive Demo 🚀", type="primary", use_container_width=True):
        st.session_state.selected_step = "0️⃣ Step 0: Documents in GCS"
        st.rerun()
    st.markdown(
        """
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

elif selected_step.startswith("0️⃣"):
    st.header("Step 0: Documents in GCS")
    st.write(
        "We list the files in the GCS bucket and preview the text content of the first "
        "document to understand the raw files we are analyzing. This unstructured data "
        "will remain in-place in Google Cloud Storage."
    )

    st.subheader("Explore Documents")

    col1, col2 = st.columns([2, 3])
    with col1:
        with st.container(border=True):
            st.markdown("##### GCS Source URI")
            gcs_display_path = (
                f"gs://{bucket_name}/{folder_name}/"
                if folder_name
                else f"gs://{bucket_name}/"
            )
            st.write(f"`{gcs_display_path}`")
            run_gcs_list = st.button("List GCS Documents", type="primary")

        if run_gcs_list or st.session_state.step_result is not None:
            if run_gcs_list:
                try:
                    storage_client = storage.Client(project=project_id)
                    bucket = storage_client.bucket(bucket_name)
                    prefix = folder_name.strip()
                    if prefix and not prefix.endswith("/"):
                        prefix += "/"

                    blobs = list(
                        storage_client.list_blobs(bucket, prefix=prefix, max_results=10)
                    )
                    pdf_files = [
                        blob.name for blob in blobs if blob.name.endswith(".pdf")
                    ]

                    if not pdf_files:
                        blobs = list(storage_client.list_blobs(bucket, max_results=10))
                        pdf_files = [
                            blob.name for blob in blobs if blob.name.endswith(".pdf")
                        ]

                    st.session_state.step_result = pdf_files
                except Exception as e:
                    st.error(f"Error listing GCS: {str(e)}")
                    st.info("Check application credentials or bucket access rights.")

            if st.session_state.step_result:
                st.success(f"Listed {len(st.session_state.step_result)} PDF documents:")
                for name in st.session_state.step_result[:5]:
                    st.markdown(f"- `{name}`")
                if len(st.session_state.step_result) > 5:
                    st.write(f"... and {len(st.session_state.step_result) - 5} more.")

    with col2:
        if st.session_state.step_result:
            with st.container(border=True):
                st.markdown("##### First Page Preview")
                selected_pdf = st.selectbox(
                    "Select document to preview", st.session_state.step_result
                )
                preview_btn = st.button("Download & Render Preview")

            if preview_btn:
                with st.spinner("Downloading and rendering PDF first page..."):
                    try:
                        storage_client = storage.Client(project=project_id)
                        bucket = storage_client.bucket(bucket_name)
                        blob = bucket.blob(selected_pdf)
                        pdf_bytes = blob.download_as_bytes()

                        from pdf2image import convert_from_bytes

                        images = convert_from_bytes(
                            pdf_bytes, first_page=1, last_page=1
                        )
                        if images:
                            st.image(
                                images[0],
                                caption=f"First Page of {os.path.basename(selected_pdf)}",
                                width="stretch",
                            )
                        else:
                            st.warning("Could not convert PDF bytes to image.")
                    except Exception as e:
                        st.error(f"Could not preview PDF: {str(e)}")
                        st.info(
                            "Requires poppler-utils installed in the environment for pdf-to-image conversion."
                        )

# ----------------------------------------------------
# STEP 1: Generate Object Table
# ----------------------------------------------------
elif selected_step.startswith("1️⃣"):
    st.header("Step 1: Generate Object Table (Ingesting Data In-Place)")
    st.write(
        "Zero-Copy RAG relies on exposing files stored in GCS directly to BigQuery via "
        "Object Tables. We create an external object table in BigQuery to reference the raw "
        "documents in-place without copying them."
    )

    gcs_uri = (
        f"gs://{bucket_name}/{folder_name}/*"
        if folder_name
        else f"gs://{bucket_name}/*"
    )
    sql_1 = f"""
CREATE EXTERNAL TABLE IF NOT EXISTS `{project_id}.{dataset_id}.object_table`
WITH CONNECTION `{full_connection_id}`
OPTIONS (
  object_metadata = 'DIRECTORY',
  uris = ['{gcs_uri}']
);
    """

    st.subheader("SQL Blueprint")
    st.code(sql_1, language="sql")

    run_btn = st.button("Create Object Table", type="primary")
    if run_btn:
        run_bq_query(sql_1)

    if st.session_state.step_result is not None:
        st.success("Object table generated successfully.")
        st.subheader("Object Table Preview")
        preview_query = f"SELECT uri, size, content_type, updated FROM `{project_id}.{dataset_id}.object_table` LIMIT 5"
        df_preview = client.query(preview_query).to_dataframe()
        st.dataframe(df_preview, width="stretch")

# ----------------------------------------------------
# STEP 2: Define Full Schema
# ----------------------------------------------------
elif selected_step.startswith("2️⃣"):
    st.header("Step 2: Define Full Schema with Autonomous Embeddings")
    st.write(
        "We define the master table schema to house our structured fields. "
        "Crucially, we define the `ClinicalTrialMasterData_embedded` structural column with the "
        "`GENERATED ALWAYS AS (AI.EMBED(...))` syntax. BigQuery will automatically manage and "
        "generate 768-dimensional embeddings for the `StudyTitle` on updates."
    )

    sql_2 = f"""
CREATE TABLE IF NOT EXISTS `{project_id}.{dataset_id}.{table_name}` (
  uri STRING,
  Sponsor STRING,
  StudyTitle STRING,
  PreferredUMLSName ARRAY<STRING>,
  NCT_Number STRING,
  Phase STRING,
  Trial_Status STRING,
  Disease_Areas STRING,
  Targeted_Enrollment INT64,
  Company STRING,
  semantic_text STRING,
  name STRING,
  preferred_name STRING,
  semantic_type ARRAY<STRING>,
  definition STRING,
  mesh_code STRING,
  mesh_codes ARRAY<STRING>,
  hpo_codes ARRAY<STRING>,
  snomed_id STRING,
  snomed_hierarchy ARRAY<STRING>,
  drug_name STRING,
  atc_code STRING,
  atc_codes ARRAY<STRING>,
  rxnorm_code STRING,
  trade_names ARRAY<STRING>,
  ema_url ARRAY<STRING>,
  source_level INT64,
  drug_preferred_name STRING,
  drug_semantic_type ARRAY<STRING>,
  criteria_type STRING,
  criteria_text STRING,
  phase_id STRING,
  status_name STRING,
  status_description STRING,
  objectRef STRING,
  ClinicalTrialMasterData_embedded STRUCT<result ARRAY<FLOAT64>, status STRING>
    GENERATED ALWAYS AS (AI.EMBED(
      StudyTitle,
      connection_id => '{full_connection_id}',
      endpoint => 'text-embedding-005'
    ))
    STORED
    OPTIONS( asynchronous = TRUE )
);
    """

    st.subheader("SQL Blueprint")
    st.code(sql_2, language="sql")

    run_btn = st.button("Define Table Schema", type="primary")
    if run_btn:
        run_bq_query(sql_2)

    if st.session_state.step_result is not None:
        st.success(f"Master schema table `{table_name}` configured successfully.")

# ----------------------------------------------------
# STEP 3: Populate Full Table
# ----------------------------------------------------
elif selected_step.startswith("3️⃣"):
    st.header("Step 3: Populate Full Table using AI.GENERATE (Text Extraction)")
    st.write(
        "We populate the structured table by calling `AI.GENERATE` using the `gemini-2.5-flash` model. "
        "This reads the PDF files directly from GCS via Object Access URLs, extracts parameters "
        "(Sponsor, Phase, targeted enrollment, etc.), and maps them into our schema. "
        "embeddings are computed automatically on insert."
    )

    prompt_text = (
        "Extract the following fields from the clinical trial document: "
        "Sponsor, StudyTitle, PreferredUMLSName (as array), NCT_Number, Phase, "
        "Trial_Status, Disease_Areas, Targeted_Enrollment (as integer), Company, "
        "semantic_text, name, preferred_name, semantic_type (as array), definition, "
        "mesh_code, mesh_codes (as array), hpo_codes (as array), snomed_id, "
        "snomed_hierarchy (as array), drug_name, atc_code, atc_codes (as array), "
        "rxnorm_code, trade_names (as array), ema_url (as array), source_level (as integer), "
        "drug_preferred_name, drug_semantic_type (as array), criteria_type, "
        "criteria_text, phase_id, status_name, status_description."
    )
    schema_text = (
        "Sponsor STRING, StudyTitle STRING, PreferredUMLSName ARRAY<STRING>, "
        "NCT_Number STRING, Phase STRING, Trial_Status STRING, Disease_Areas STRING, "
        "Targeted_Enrollment INT64, Company STRING, semantic_text STRING, name STRING, "
        "preferred_name STRING, semantic_type ARRAY<STRING>, definition STRING, "
        "mesh_code STRING, mesh_codes ARRAY<STRING>, hpo_codes ARRAY<STRING>, "
        "snomed_id STRING, snomed_hierarchy ARRAY<STRING>, drug_name STRING, "
        "atc_code STRING, atc_codes ARRAY<STRING>, rxnorm_code STRING, "
        "trade_names ARRAY<STRING>, ema_url ARRAY<STRING>, source_level INT64, "
        "drug_preferred_name STRING, drug_semantic_type ARRAY<STRING>, "
        "criteria_type STRING, criteria_text STRING, phase_id STRING, "
        "status_name STRING, status_description STRING"
    )

    sql_3 = f"""
-- Check if table is empty before inserting
IF NOT EXISTS (SELECT 1 FROM `{project_id}.{dataset_id}.{table_name}` LIMIT 1) THEN
  INSERT INTO `{project_id}.{dataset_id}.{table_name}`
  (
    uri, Sponsor, StudyTitle, PreferredUMLSName, NCT_Number, Phase,
    Trial_Status, Disease_Areas, Targeted_Enrollment, Company, semantic_text,
    name, preferred_name, semantic_type, definition, mesh_code, mesh_codes,
    hpo_codes, snomed_id, snomed_hierarchy, drug_name, atc_code, atc_codes,
    rxnorm_code, trade_names, ema_url, source_level, drug_preferred_name,
    drug_semantic_type, criteria_type, criteria_text, phase_id, status_name,
    status_description, objectRef
  )
  SELECT
    uri, Sponsor, StudyTitle, PreferredUMLSName, NCT_Number, Phase,
    Trial_Status, Disease_Areas, Targeted_Enrollment, Company, semantic_text,
    name, preferred_name, semantic_type, definition, mesh_code, mesh_codes,
    hpo_codes, snomed_id, snomed_hierarchy, drug_name, atc_code, atc_codes,
    rxnorm_code, trade_names, ema_url, source_level, drug_preferred_name,
    drug_semantic_type, criteria_type, criteria_text, phase_id, status_name,
    status_description,
    uri AS objectRef
  FROM (
    SELECT
      uri,
      AI.GENERATE(
        prompt => STRUCT('{prompt_text}', OBJ.GET_ACCESS_URL(OBJ.MAKE_REF(uri, '{full_connection_id}'), 'r')),
        endpoint => 'gemini-2.5-flash',
        output_schema => '{schema_text}',
        connection_id => '{full_connection_id}'
      ).* EXCEPT (full_response, status)
    FROM
      `{project_id}.{dataset_id}.object_table`
  );
  SELECT 'Data inserted successfully.' AS status;
ELSE
  SELECT 'Table is not empty. Skipping insertion.' AS status;
END IF;
    """

    st.subheader("SQL Blueprint")
    st.code(sql_3, language="sql")

    st.warning(
        "⚠️ Running this step will invoke Vertex LLM on the files. "
        "This process may take a few minutes depending on the quantity of documents."
    )

    # Check prerequisites
    master_exists = check_table_exists(project_id, dataset_id, table_name)
    object_exists = check_table_exists(project_id, dataset_id, "object_table")

    if not master_exists:
        st.error(
            f"❌ **Prerequisite Missing**: The master table `{table_name}` "
            "does not exist. Please complete **Step 2** first."
        )
    if not object_exists:
        st.error(
            "❌ **Prerequisite Missing**: The object table `object_table` "
            "does not exist. Please complete **Step 1** first."
        )

    run_btn = st.button(
        "Populate Table (Extract via Gemini)",
        type="primary",
        disabled=not (master_exists and object_exists),
    )
    if run_btn:
        run_bq_query(sql_3)

    if st.session_state.step_result is not None:
        st.success("Table populated / checked.")
        st.subheader("Extracted Master Data Preview")
        preview_query = (
            f"SELECT uri, Sponsor, StudyTitle, Phase, Trial_Status, "
            f"Targeted_Enrollment FROM `{project_id}.{dataset_id}.{table_name}` LIMIT 5"
        )
        df_preview = client.query(preview_query).to_dataframe()
        st.dataframe(df_preview, width="stretch")

# ----------------------------------------------------
# STEP 4: AI.Search (Semantic & Hybrid Search)
# ----------------------------------------------------
elif selected_step.startswith("4️⃣"):
    st.header("Step 4: AI.Search (Semantic Search without Vector Databases)")
    st.write(
        "We execute a native `AI.SEARCH` query directly inside BigQuery. This resolves semantic "
        "similarity between the generated text embedding and the query string natively "
        "without replicating data to an external vector database."
    )

    search_query = st.text_input(
        "Semantic Search Query", value="Cancer treated by MK-3475"
    )
    search_mode = st.selectbox(
        "Search Mode",
        ["semantic", "hybrid"],
        help="Hybrid combines vector search with keyword matching (Preview feature)",
    )

    if search_mode == "hybrid":
        st.warning(
            """
        💡 **Note on Hybrid Search Mode:**

        The `mode => 'hybrid'` parameter is a BigQuery preview feature.
        If executing the search fails with:
        *`Named argument mode not found in signature for call to function AI.SEARCH`*,
        your current BigQuery project/region does not support this preview feature yet.
        Simply switch the **Search Mode** back to **semantic**.
        """
        )

    # Omit mode parameter for standard semantic search to prevent signature errors
    mode_clause = ", mode => 'hybrid'" if search_mode == "hybrid" else ""
    sql_4 = f"""
SELECT
  base.StudyTitle,
  distance
FROM AI.SEARCH(
  TABLE `{project_id}.{dataset_id}.{table_name}`,
  'StudyTitle',
  @search_query{mode_clause},
  top_k => 10
)
    """

    st.subheader("SQL Query")
    st.code(sql_4, language="sql")

    # Check prerequisites
    master_exists = check_table_exists(project_id, dataset_id, table_name)
    if not master_exists:
        st.warning(
            f"⚠️ **Prerequisite Table Missing**: The master table `{table_name}` "
            "does not exist. Please complete **Step 2** (create schema) and "
            "**Step 3** (populate table) first."
        )

    run_btn = st.button("Execute Search", type="primary", disabled=not master_exists)
    if run_btn:
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("search_query", "STRING", search_query)
            ]
        )
        run_bq_query(sql_4, job_config=job_config)

    if st.session_state.step_result is not None:
        st.subheader("Search Results")
        if st.session_state.step_result.empty:
            st.warning(
                "No matches found. Ensure the master table is populated and embeddings are updated."
            )
        else:
            st.dataframe(st.session_state.step_result, width="stretch")

# ----------------------------------------------------
# STEP 5: Parse Documents (AI.PARSE_DOCUMENT chunking)
# ----------------------------------------------------
elif selected_step.startswith("5️⃣"):
    st.header("Step 5: [Optional] Parse Documents using AI.PARSE_DOCUMENT")
    st.write(
        "For complex, multi-page documents, we use `AI.PARSE_DOCUMENT` to chunk the text "
        "layout-aware, and then generate embeddings for those chunks. This enables chunk-level retrieval."
    )

    st.info(
        "💡 **Self-Service Guide: Resolving Document AI Parser Endpoint Errors**\n\n"
        "If running this step fails with an endpoint support error (such as *Gemini endpoint is not supported*), "
        "you must provision a dedicated Layout Parser processor:\n\n"
        "1. Open the **Google Cloud Console** for your project.\n"
        "2. Navigate to **Document AI** via the search bar or menu.\n"
        "3. Click on **Explore Processors** or **Processor Library**.\n"
        "4. Search for and select the **Layout Parser** processor type (currently in preview/pre-GA).\n"
        "5. Click **Create Processor**, set a name, and choose your region (e.g., `us`).\n"
        "6. Once created, copy the processor's **Endpoint ID path** (formatted as: "
        "`projects/YOUR_PROJECT_NUMBER/locations/us/processors/YOUR_PROCESSOR_ID`).\n"
        "7. Paste this full path into the **Document AI Endpoint** field in the sidebar "
        "**⚙️ Configuration** menu and click **Parse and Chunk Documents** again."
    )

    sql_5 = f"""
CREATE TABLE IF NOT EXISTS `{project_id}.{dataset_id}.{table_2_name}` AS
WITH parsed_docs AS (
  SELECT
    parsed.uri,
    parsed.content AS chunks
  FROM AI.parse_document(
    (SELECT * FROM `{project_id}.{dataset_id}.object_table` LIMIT 100),
    endpoint => '{docai_endpoint}'
  ) AS parsed
),
chunks_with_metadata AS (
  SELECT
    t1.StudyTitle AS study_name,
    t1.Sponsor AS sponsor,
    p.chunks,
    AI.EMBED(p.chunks, connection_id => '{full_connection_id}', endpoint => 'text-embedding-005').result AS embedding
  FROM parsed_docs p
  JOIN `{project_id}.{dataset_id}.{table_name}` AS t1
  ON p.uri = t1.uri
  WHERE p.chunks IS NOT NULL AND p.chunks != ''
)
SELECT * FROM chunks_with_metadata
WHERE ARRAY_LENGTH(embedding) = 768;
    """

    st.subheader("SQL Blueprint")
    st.code(sql_5, language="sql")

    st.info("ℹ️ AI.PARSE_DOCUMENT performs deep visual document layout chunking.")

    # Check prerequisites
    master_exists = check_table_exists(project_id, dataset_id, table_name)
    object_exists = check_table_exists(project_id, dataset_id, "object_table")

    if not master_exists:
        st.error(
            f"❌ **Prerequisite Missing**: The master table `{table_name}` "
            "does not exist. Please complete **Step 2** first."
        )
    if not object_exists:
        st.error(
            "❌ **Prerequisite Missing**: The object table `object_table` "
            "does not exist. Please complete **Step 1** first."
        )

    run_btn = st.button(
        "Execute Document Chunk Parsing",
        type="primary",
        disabled=not (master_exists and object_exists),
    )
    if run_btn:
        run_bq_query(sql_5)

    if st.session_state.step_result is not None:
        st.success("Document chunking and parsing completed successfully.")
        st.subheader("Parsed Chunks Preview")
        preview_query = (
            f"SELECT study_name, sponsor, SUBSTR(chunks, 1, 150) AS chunk_text "
            f"FROM `{project_id}.{dataset_id}.{table_2_name}` LIMIT 5"
        )
        df_preview = client.query(preview_query).to_dataframe()
        st.dataframe(df_preview, width="stretch")

# ----------------------------------------------------
# STEP 6: Cross-Column Hybrid Search
# ----------------------------------------------------
elif selected_step.startswith("6️⃣"):
    st.header("Step 6: [Optional] Cross-Column Hybrid Search")
    st.write(
        "Demonstrates cross-column hybrid querying using BigQuery's native `VECTOR_SEARCH`. "
        "We perform vector search against chunk embeddings combined with lexical keyword matching "
        "against the `sponsor` column for specific targeted lookups."
    )

    search_type = st.selectbox(
        "Search Type",
        ["Pure Vector Search", "Hybrid Search (Preview)"],
        help="Hybrid search combines vector search with keyword matching (requires preview allowlist)",
    )
    semantic_query = st.text_input(
        "Semantic Search Query", value="chronic disease studies by AstraZeneca"
    )

    if search_type == "Hybrid Search (Preview)":
        lexical_query = st.text_input(
            "Lexical Filter Query (Sponsor Name)", value="AstraZeneca"
        )
        lexical_clause = """,
  lexical_search_columns => ["sponsor"],
  lexical_search_query_value => @lexical_query"""
        st.warning(
            """
        💡 **Note on Hybrid Search Mode:**

        The `lexical_search_columns` parameter is a BigQuery preview feature.
        If executing the search fails with:
        *`Named argument lexical_search_columns not found in signature for call to function VECTOR_SEARCH`*,
        your current BigQuery project/region does not support this preview feature yet.
        Simply switch the **Search Type** back to **Pure Vector Search**.
        """
        )
    else:
        lexical_query = ""
        lexical_clause = ""

    sql_6 = f"""
SELECT
  base.study_name,
  base.sponsor,
  base.chunks,
  distance
FROM VECTOR_SEARCH(
  TABLE `{project_id}.{dataset_id}.{table_2_name}`,
  "embedding",
  query_value => AI.EMBED(
    @semantic_query,
    connection_id => '{full_connection_id}',
    endpoint => 'text-embedding-005'
  ).result{lexical_clause},
  top_k => 10
)
ORDER BY distance ASC;
    """

    st.subheader("SQL Query")
    st.code(sql_6, language="sql")

    # Check prerequisites
    chunks_table_exists = check_table_exists(project_id, dataset_id, table_2_name)
    if not chunks_table_exists:
        st.warning(
            f"⚠️ **Prerequisite Table Missing**: The chunks table `{table_2_name}` "
            f"does not exist in dataset `{dataset_id}`. "
            "Please complete **Step 5** first to parse documents and generate the chunks table."
        )

    run_btn = st.button(
        "Execute Cross-Column Search", type="primary", disabled=not chunks_table_exists
    )
    if run_btn:
        query_params = [
            bigquery.ScalarQueryParameter("semantic_query", "STRING", semantic_query)
        ]
        if search_type == "Hybrid Search (Preview)":
            query_params.append(
                bigquery.ScalarQueryParameter("lexical_query", "STRING", lexical_query)
            )

        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        run_bq_query(sql_6, job_config=job_config)

    if st.session_state.step_result is not None:
        st.subheader("Search Results")
        if st.session_state.step_result.empty:
            st.warning(
                "No matches found. Ensure the chunks table from Step 5 is created."
            )
        else:
            st.dataframe(st.session_state.step_result, width="stretch")

# ----------------------------------------------------
# STEP 7: Graph Generation & Traversal
# ----------------------------------------------------
elif selected_step.startswith("7️⃣"):
    st.header("Step 7: Graph Generation and Traversal")
    st.write(
        "We construct the views representing our nodes and edges (Trial, Drug, Sponsor) and "
        "define the BigQuery property graph structure. This registers entities and relationship edges "
        "natively to execute Graph Query Language (GQL) statements."
    )

    sql_views = f"""
-- 1. Create Views for Graph Nodes and Edges
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.drug_nodes` AS
SELECT DISTINCT drug_name AS drug_name
FROM `{project_id}.{dataset_id}.{table_name}`
WHERE drug_name IS NOT NULL;

CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.trial_drug_edges` AS
SELECT DISTINCT NCT_Number AS trial_id, drug_name AS drug_name
FROM `{project_id}.{dataset_id}.{table_name}`
WHERE drug_name IS NOT NULL AND NCT_Number IS NOT NULL;

CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.sponsor_nodes` AS
SELECT DISTINCT Sponsor AS sponsor_name
FROM `{project_id}.{dataset_id}.{table_name}`
WHERE Sponsor IS NOT NULL;

CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.trial_sponsor_edges` AS
SELECT DISTINCT NCT_Number AS trial_id, Sponsor AS sponsor_name
FROM `{project_id}.{dataset_id}.{table_name}`
WHERE Sponsor IS NOT NULL AND NCT_Number IS NOT NULL;
    """

    sql_graph = f"""
-- 2. Define Property Graph Structure
CREATE OR REPLACE PROPERTY GRAPH `{project_id}.{dataset_id}.{graph_name}`
NODE TABLES (
  `{project_id}.{dataset_id}.{table_name}`
    KEY (NCT_Number)
    LABEL Trial
    PROPERTIES (NCT_Number, StudyTitle, Disease_Areas, Phase),

  `{project_id}.{dataset_id}.drug_nodes`
    KEY (drug_name)
    LABEL Drug
    PROPERTIES (drug_name),

  `{project_id}.{dataset_id}.sponsor_nodes`
    KEY (sponsor_name)
    LABEL Sponsor
    PROPERTIES (sponsor_name)
)
EDGE TABLES (
  `{project_id}.{dataset_id}.trial_drug_edges`
    KEY (trial_id, drug_name)
    SOURCE KEY (trial_id) REFERENCES `{project_id}.{dataset_id}.{table_name}` (NCT_Number)
    DESTINATION KEY (drug_name) REFERENCES `{project_id}.{dataset_id}.drug_nodes` (drug_name)
    LABEL TestsDrug,

  `{project_id}.{dataset_id}.trial_sponsor_edges`
    KEY (trial_id, sponsor_name)
    SOURCE KEY (trial_id) REFERENCES `{project_id}.{dataset_id}.{table_name}` (NCT_Number)
    DESTINATION KEY (sponsor_name) REFERENCES `{project_id}.{dataset_id}.sponsor_nodes` (sponsor_name)
    LABEL SponsoredBy
);
    """

    st.subheader("SQL Blueprint - View Definitions")
    st.code(sql_views, language="sql")

    st.subheader("SQL Blueprint - Property Graph Creation")
    st.code(sql_graph, language="sql")

    # Check prerequisites
    master_exists = check_table_exists(project_id, dataset_id, table_name)
    if not master_exists:
        st.warning(
            f"⚠️ **Prerequisite Table Missing**: The master table `{table_name}` "
            "does not exist. Please complete **Step 2** and **Step 3** first."
        )

    run_btn = st.button(
        "Generate Views and Property Graph", type="primary", disabled=not master_exists
    )
    if run_btn:
        with st.spinner("Executing setup..."):
            try:
                # Execute views first
                for statement in sql_views.split(";"):
                    if statement.strip():
                        client.query(statement).result()
                # Execute graph next
                client.query(sql_graph).result()
                st.session_state.step_result = True
                st.success("Successfully generated views and property graph!")
            except Exception as e:
                st.error(f"Error creating graph components: {str(e)}")

# ----------------------------------------------------
# STEP 8: Visualize the Graph
# ----------------------------------------------------
elif selected_step.startswith("8️⃣"):
    st.header("Step 8: Visualize the Graph")
    st.write(
        "We execute graph GQL pattern matching to identify relationships between trials, sponsors, and drugs. "
        "We construct and render the resulting subgraph interactively using Vis.js."
    )

    # Check if client connection is available to retrieve trial nodes list
    trial_options = []
    if client:
        try:
            trial_df = client.query(
                f"SELECT DISTINCT StudyTitle "
                f"FROM `{project_id}.{dataset_id}.{table_name}` "
                "WHERE StudyTitle IS NOT NULL LIMIT 40"
            ).to_dataframe()
            trial_options = list(trial_df["StudyTitle"])
        except Exception:
            pass

    if not trial_options:
        trial_options = ["Select or type trial title (Run Steps 1-3 first)"]

    selected_trial = st.selectbox(
        "Search / Select Trial Node for Traversal", trial_options
    )

    sql_viz = f"""
SELECT * FROM GRAPH_TABLE(
  `{project_id}.{dataset_id}.{graph_name}`
  MATCH (s:Sponsor)<-[:SponsoredBy]-(t:Trial)-[:TestsDrug]->(d:Drug)
  WHERE t.StudyTitle = @trial_title
  RETURN t.StudyTitle AS trial_title, s.sponsor_name AS sponsor, d.drug_name AS drug
) LIMIT 10
    """

    st.subheader("GQL Subgraph Traversal Query")
    st.code(sql_viz, language="sql")

    # Check prerequisites
    graph_exists = check_table_exists(project_id, dataset_id, "drug_nodes")
    if not graph_exists:
        st.warning(
            "⚠️ **Property Graph Missing**: The clinical trial property graph components "
            "do not exist. Please complete **Step 7** first."
        )

    run_btn = st.button("Visualize Subgraph", type="primary", disabled=not graph_exists)
    if run_btn:
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("trial_title", "STRING", selected_trial)
            ]
        )
        run_bq_query(sql_viz, job_config=job_config)

    if st.session_state.step_result is not None:
        df = st.session_state.step_result
        if df.empty:
            st.warning(
                f"No relationships matched for '{selected_trial}'. "
                "Ensure graph nodes are generated and relationships exist."
            )

            # Fallback layout preview using general relationships
            st.info("Attempting general query for sample preview...")
            try:
                sample_query = f"""
                SELECT t.StudyTitle AS trial_title, s.sponsor_name AS sponsor, d.drug_name AS drug
                FROM GRAPH_TABLE(
                  `{project_id}.{dataset_id}.{graph_name}`
                  MATCH (s:Sponsor)<-[:SponsoredBy]-(t:Trial)-[:TestsDrug]->(d:Drug)
                ) LIMIT 5
                """
                df = client.query(sample_query).to_dataframe()
            except Exception:
                pass

        if not df.empty:
            st.success(f"Traversed {len(df)} connections. Rendering subgraph below:")

            # Process results to build Vis.js nodes and edges
            nodes = []
            edges = []
            seen_nodes = set()

            for _, row in df.iterrows():
                trial = row["trial_title"]
                drug = row["drug"]
                sponsor = row["sponsor"]

                # Add central trial node
                if trial and trial not in seen_nodes:
                    short_trial = trial[:25] + "..." if len(trial) > 25 else trial
                    nodes.append(
                        {
                            "id": trial,
                            "label": short_trial,
                            "color": {
                                "background": "#6366f1",
                                "border": "#4f46e5",
                                "highlight": {
                                    "background": "#818cf8",
                                    "border": "#6366f1",
                                },
                            },
                            "font": {
                                "color": "#f8fafc",
                                "size": 15,
                                "bold": True,
                                "face": "Inter, sans-serif",
                            },
                            "shape": "dot",
                            "size": 32,
                            "title": f"Trial: {trial}",
                        }
                    )
                    seen_nodes.add(trial)

                # Add drug node
                if drug and drug not in seen_nodes:
                    nodes.append(
                        {
                            "id": drug,
                            "label": drug,
                            "color": {
                                "background": "#0d9488",
                                "border": "#0f766e",
                                "highlight": {
                                    "background": "#14b8a6",
                                    "border": "#0d9488",
                                },
                            },
                            "font": {
                                "color": "#cbd5e1",
                                "size": 14,
                                "face": "Inter, sans-serif",
                            },
                            "shape": "dot",
                            "size": 24,
                            "title": f"Drug: {drug}",
                        }
                    )
                    seen_nodes.add(drug)

                # Add sponsor node
                if sponsor and sponsor not in seen_nodes:
                    nodes.append(
                        {
                            "id": sponsor,
                            "label": sponsor,
                            "color": {
                                "background": "#ec4899",
                                "border": "#db2777",
                                "highlight": {
                                    "background": "#f472b6",
                                    "border": "#ec4899",
                                },
                            },
                            "font": {
                                "color": "#cbd5e1",
                                "size": 14,
                                "face": "Inter, sans-serif",
                            },
                            "shape": "dot",
                            "size": 24,
                            "title": f"Sponsor: {sponsor}",
                        }
                    )
                    seen_nodes.add(sponsor)

                # Add edges
                if trial and drug:
                    edges.append(
                        {"from": trial, "to": drug, "label": "tests", "arrows": "to"}
                    )
                if trial and sponsor:
                    edges.append(
                        {
                            "from": trial,
                            "to": sponsor,
                            "label": "sponsored by",
                            "arrows": "to",
                        }
                    )

            # JSON serialization
            nodes_json = json.dumps(nodes)
            edges_json = json.dumps(edges)

            # Custom HTML template for Vis.js Graph Rendering
            html_template = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="preconnect" href="https://fonts.googleapis.com">
                <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
                      rel="stylesheet">
                <script type="text/javascript"
                        src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
                <style type="text/css">
                    body {{
                        margin: 0;
                        padding: 0;
                        overflow: hidden;
                        background-color: #0f172a;
                    }}
                    #mynetwork {{
                        width: 100%;
                        height: 500px;
                        background-color: #0f172a;
                        border: 1px solid #334155;
                        border-radius: 12px;
                    }}
                    #legend {{
                        position: absolute;
                        top: 16px;
                        left: 16px;
                        background-color: rgba(15, 23, 42, 0.85);
                        backdrop-filter: blur(8px);
                        -webkit-backdrop-filter: blur(8px);
                        border: 1px solid #334155;
                        border-radius: 8px;
                        padding: 12px 16px;
                        font-family: 'Inter', sans-serif;
                        font-size: 13px;
                        color: #94a3b8;
                        display: flex;
                        flex-direction: column;
                        gap: 8px;
                        pointer-events: none;
                        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
                    }}
                    .legend-item {{
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }}
                    .legend-dot {{
                        display: inline-block;
                        width: 12px;
                        height: 12px;
                        border-radius: 50%;
                        border: 1.5px solid;
                    }}
                </style>
            </head>
            <body>
            <div id="mynetwork"></div>
            <div id="legend">
                <div class="legend-item">
                    <span class="legend-dot"
                          style="background-color: #6366f1; border-color: #4f46e5;"></span>
                    Clinical Trial
                </div>
                <div class="legend-item">
                    <span class="legend-dot"
                          style="background-color: #0d9488; border-color: #0f766e;"></span>
                    Tested Drug
                </div>
                <div class="legend-item">
                    <span class="legend-dot"
                          style="background-color: #ec4899; border-color: #db2777;"></span>
                    Sponsor
                </div>
            </div>
            <script type="text/javascript">
                var nodes = new vis.DataSet({nodes_json});
                var edges = new vis.DataSet({edges_json});
                var container = document.getElementById('mynetwork');
                var data = {{ nodes: nodes, edges: edges }};
                var options = {{
                    nodes: {{
                        shape: 'dot',
                        borderWidth: 2,
                        shadow: {{
                            enabled: true,
                            color: 'rgba(0, 0, 0, 0.4)',
                            size: 6,
                            x: 3,
                            y: 3
                        }}
                    }},
                    edges: {{
                        width: 2,
                        color: {{
                            color: '#334155',
                            highlight: '#6366f1',
                            hover: '#818cf8'
                        }},
                        font: {{
                            size: 12,
                            color: '#64748b',
                            face: 'Inter, sans-serif',
                            strokeWidth: 3,
                            strokeColor: '#0f172a'
                        }},
                        arrows: {{
                            to: {{
                                enabled: true,
                                scaleFactor: 0.8
                            }}
                        }},
                        smooth: {{
                            type: 'dynamic'
                        }}
                    }},
                    physics: {{
                        barnesHut: {{
                            gravitationalConstant: -5500,
                            centralGravity: 0.08,
                            springLength: 220,
                            springConstant: 0.04
                        }},
                        minVelocity: 0.75
                    }},
                    interaction: {{
                        hover: true,
                        tooltipDelay: 150
                    }}
                }};
                var network = new vis.Network(container, data, options);
            </script>
            </body>
            </html>
            """

            # Render Vis.js Component
            st.components.v1.html(html_template, height=520, scrolling=False)
            st.dataframe(df, width="stretch")

# ----------------------------------------------------
# STEP 9: Advanced Graph Traversal
# ----------------------------------------------------
elif selected_step.startswith("9️⃣"):
    st.header("Step 9: Advanced Graph Traversal & Generative Insights")
    st.write(
        "Demonstrates combined hybrid search and multi-hop graph traversal. "
        "We semantically find metabolic disease trials, traverse the graph to identify other trials "
        "testing identical drugs, and summarize the cross-trial insight using `AI.GENERATE`."
    )

    disease_query = st.text_input(
        "Semantic Disease Lookup Query", value="Metabolic diseases"
    )
    search_mode = st.selectbox(
        "Search Mode",
        ["semantic", "hybrid"],
        help="Hybrid combines vector search with keyword matching (requires preview allowlist)",
    )

    if search_mode == "hybrid":
        st.warning(
            """
        💡 **Note on Hybrid Search Mode:**

        The `mode => 'hybrid'` parameter is a BigQuery preview feature.
        If executing the search fails with:
        *`Named argument mode not found in signature for call to function AI.SEARCH`*,
        your current BigQuery project/region does not support this preview feature yet.
        Simply switch the **Search Mode** back to **semantic**.
        """
        )

    # Omit mode parameter for standard semantic search to prevent signature errors
    mode_clause = ", mode => 'hybrid'" if search_mode == "hybrid" else ""

    sql_9 = f"""
WITH relevant_trials AS (
  SELECT base.NCT_Number
  FROM AI.SEARCH(
    TABLE `{project_id}.{dataset_id}.{table_name}`,
    'StudyTitle',
    @disease_query{mode_clause},
    top_k => 10
  )
),
graph_data AS (
  SELECT * FROM GRAPH_TABLE(
    `{project_id}.{dataset_id}.{graph_name}`
    MATCH (t:Trial)-[:TestsDrug]->(d:Drug)<-[:TestsDrug]-(other:Trial)
    WHERE t.Phase = 'Phase 3'
    RETURN
      t.NCT_Number AS t_nct,
      t.StudyTitle AS source_trial,
      d.drug_name AS drug,
      other.StudyTitle AS related_trial,
      other.NCT_Number AS other_nct,
      other.Disease_Areas AS related_disease
  )
),
raw_results AS (
  SELECT DISTINCT
    gd.source_trial,
    gd.drug,
    gd.related_trial,
    gd.related_disease
  FROM graph_data gd
  JOIN relevant_trials rt ON gd.t_nct = rt.NCT_Number
  WHERE gd.t_nct != gd.other_nct
  QUALIFY ROW_NUMBER() OVER(PARTITION BY gd.drug ORDER BY gd.related_trial) <= 2
)
SELECT
  source_trial,
  drug,
  related_trial,
  related_disease,
  AI.GENERATE(
    prompt => 'Analyze these two clinical trials testing the same drug (' || drug || '). '
      || 'Provide a pithy, one-sentence cross-indication laymans insight starting with '
      || '"Based on the findings of these two studies...". '
      || 'Trial 1: ' || source_trial || ' | Trial 2: ' || related_trial,
    endpoint => 'gemini-2.5-flash',
    output_schema => 'summary STRING',
    connection_id => '{full_connection_id}'
  ).summary AS cross_trial_insight
FROM raw_results
LIMIT 5;
    """

    st.subheader("Advanced SQL + GQL Blueprint")
    st.code(sql_9, language="sql")

    # Check prerequisites
    master_exists = check_table_exists(project_id, dataset_id, table_name)
    graph_exists = check_table_exists(project_id, dataset_id, "drug_nodes")

    if not master_exists:
        st.warning(
            f"⚠️ **Prerequisite Table Missing**: The master table `{table_name}` "
            "does not exist. Please complete **Step 2** and **Step 3** first."
        )
    if not graph_exists:
        st.warning(
            "⚠️ **Property Graph Missing**: The property graph components do not exist. "
            "Please complete **Step 7** first."
        )

    run_btn = st.button(
        "Execute Traversal & Summarize",
        type="primary",
        disabled=not (master_exists and graph_exists),
    )
    if run_btn:
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("disease_query", "STRING", disease_query)
            ]
        )
        run_bq_query(sql_9, job_config=job_config)

    if st.session_state.step_result is not None:
        df = st.session_state.step_result
        st.subheader("Cross-Trial Layman Insights")
        if df.empty:
            st.warning(
                "No traversals found. Verify that multiple trials are associated with identical drug nodes."
            )
        else:
            for idx, row in df.iterrows():
                # Split diseases by comma and build individual badges
                diseases = []
                if row["related_disease"]:
                    diseases = [
                        d.strip()
                        for d in row["related_disease"].split(",")
                        if d.strip()
                    ]
                badges_html = " ".join(
                    [
                        (
                            f'<span class="badge badge-info" '
                            f'style="margin-top: 0.25rem; display: inline-block;">{d}</span>'
                        )
                        for d in diseases
                    ]
                )

                st.markdown(
                    f"""
                    <div class="metric-card" style="margin-bottom: 1.5rem;">
                        <div style="font-weight: 700; color: #38bdf8; font-size: 1.25rem; margin-bottom: 0.75rem;">
                            💊 Drug: {row['drug']}
                        </div>
                        <div style="font-size: 0.95rem; margin-bottom: 0.75rem; color: var(--card-text); line-height: 1.6;">
                            <div style="margin-bottom: 0.5rem;">
                                <strong style="color: var(--text-color);">Trial 1:</strong> {row['source_trial']}
                            </div>
                            <div style="margin-bottom: 0.5rem;">
                                <strong style="color: var(--text-color);">Trial 2:</strong> {row['related_trial']}
                            </div>
                            <div style="margin-top: 0.6rem;">
                                {badges_html}
                            </div>
                        </div>
                        <div class="accent-block" style="margin-top: 0.75rem; padding: 1rem;">
                            <h5 style="margin: 0 0 0.5rem 0; color: #38bdf8;
                                       font-size: 1rem; font-weight: 600;">
                                💡 Laymans Insight
                            </h5>
                            <p style="margin: 0; line-height: 1.6; font-size: 0.95rem;">
                                {row['cross_trial_insight']}
                            </p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ----------------------------------------------------
# STEP 10: Scale - Vector Index
# ----------------------------------------------------
elif selected_step.startswith("🔟"):
    st.header("Step 10: Scale - Creating a Vector Index")
    st.write(
        "To scale semantic search to millions of documents, you create an IVF (Inverted File) vector "
        "index on the embedding column. BigQuery uses this for efficient nearest-neighbor search."
    )

    sql_10 = f"""
-- Create Vector Index (IVF Type)
CREATE OR REPLACE VECTOR INDEX `{project_id}.{dataset_id}.{vector_index_name}`
ON `{project_id}.{dataset_id}.{table_name}`(ClinicalTrialMasterData_embedded)
OPTIONS(
  distance_type = 'COSINE',
  index_type = 'IVF'
);
    """

    st.subheader("SQL Query")
    st.code(sql_10, language="sql")

    st.info(
        "⚠️ Note: BigQuery requires a minimum of 5,000 rows to build IVF indexes. "
        "For smaller tables, search will run fine via flat scan."
    )

    # Check prerequisites
    master_exists = check_table_exists(project_id, dataset_id, table_name)
    row_count = 0
    if master_exists:
        try:
            count_df = client.query(
                f"SELECT COUNT(*) as cnt FROM `{project_id}.{dataset_id}.{table_name}`"
            ).to_dataframe()
            row_count = int(count_df.iloc[0]["cnt"])
        except Exception:
            pass

    if not master_exists:
        st.warning(
            f"⚠️ **Prerequisite Table Missing**: The master table `{table_name}` "
            "does not exist. Please complete **Step 2** first."
        )
    elif row_count < 5000:
        st.warning(
            f"⚠️ **Insufficient Rows for Indexing ({row_count}/5000)**: "
            "BigQuery requires a minimum of **5,000 rows** to build a vector index. "
            "Since your dataset has fewer rows, search will execute fine using a flat scan. "
            "The index creation button is disabled."
        )

    run_btn = st.button(
        "Create IVF Vector Index",
        type="primary",
        disabled=not (master_exists and row_count >= 5000),
    )
    if run_btn:
        run_bq_query(sql_10)

    if st.session_state.step_result is not None:
        st.success("Vector index registration complete (or checked).")

# ----------------------------------------------------
# Global Navigation Footer (Back / Next Buttons)
# ----------------------------------------------------
st.markdown("---")
nav_col1, nav_col2, nav_col3 = st.columns([1, 4, 1])

current_idx = step_options.index(selected_step)

with nav_col1:
    if current_idx > 0:
        if st.button("← Back", use_container_width=True):
            st.session_state.selected_step = step_options[current_idx - 1]
            st.rerun()

with nav_col2:
    if current_idx == 0:
        step_info = "Overview & Summary"
    else:
        step_name = selected_step.split(":", 1)[-1].strip() if ":" in selected_step else selected_step
        step_info = f"Step {current_idx - 1} of {len(step_options) - 1}: {step_name}"
        
    st.markdown(
        f"<div style='text-align: center; color: #94a3b8; font-size: 0.9rem; padding-top: 0.25rem; font-weight: 500;'>"
        f"{step_info}"
        f"</div>",
        unsafe_allow_html=True,
    )

with nav_col3:
    if current_idx > 0 and current_idx < len(step_options) - 1:
        if st.button("Next →", use_container_width=True, type="primary"):
            st.session_state.selected_step = step_options[current_idx + 1]
            st.rerun()


