# Document Analytics on BigQuery Installation

## Welcome
Welcome to the Document Analytics on BigQuery setup tutorial! In this guide, you will deploy the necessary infrastructure to extract intelligent insights from your documents using BigQuery and Google's AI models.

**Estimated time to complete:** 10 minutes

**Prerequisites:**
* An active Google Cloud project with billing enabled.
* You must have `Editor` or `Owner` IAM roles on your selected project.

## Project Setup
First, you need to set your primary Google Cloud project. The installation script requires the `PROJECT_ID` environment variable to be set.

Replace `<YOUR_PROJECT_ID>` with your actual Google Cloud Project ID and run the following commands in your Cloud Shell terminal:

```sh
export PROJECT_ID="<YOUR_PROJECT_ID>"
gcloud config set project $PROJECT_ID
```

## Quick Infrastructure Install
Now, let's provision the core infrastructure. We will run an automated bash script that creates the required BigQuery datasets and Cloud Storage buckets for your document analytics pipeline.

First, make the installation script executable:

```sh
chmod +x ./quick-install.sh
```

Next, run the script to execute the resource creation:

```sh
./quick-install.sh --execute
```

**Tip:** You can run `./quick-install.sh` without the `--execute` flag first. This acts as a dry run, allowing you to preview exactly which resources will be created before any changes are made to your project.

## Audit Resources
Now that the installation script has finished, let's audit your newly created Google Cloud resources to ensure everything deployed correctly. 

You can use `gcloud` and `bq` to verify your infrastructure. Run the following commands to list your active storage buckets and BigQuery datasets:

```sh
gcloud storage buckets list
```

```sh
bq ls
```

**Tip:** If you have the [Gemini CLI](https://github.com/GoogleCloudPlatform/gemini-cli) installed in your Cloud Shell environment, you can also use it to seamlessly audit service account permissions, verify configuration, and query the resources you just deployed.

## Setup Clinical Trial Graph
With the infrastructure audited and in place, your graph database, LLM endpoints, and embedding models have also been automatically configured by the installation script!

Take a moment to review the SQL script in your editor to understand the models and the `DrugGraph` property graph structure that was deployed:

<walkthrough-editor-open-file filePath="sql/setup_clinical_trial_graph.sql"></walkthrough-editor-open-file>

**Optional:** If you wish to orchestrate the ingestion of unstructured data (like PDFs and text profiles) from GCS into BigQuery, you can run the provided Python script:

<walkthrough-editor-open-file filePath="scripts/orchestrate_ingestion.py"></walkthrough-editor-open-file>

```sh
pip install google-cloud-bigquery
python3 scripts/orchestrate_ingestion.py
```

## Next Steps in BigQuery Studio
Congratulations! You have successfully deployed the infrastructure and set up the foundation for document analytics. 🏆

To explore the generated knowledge graph and analyze your documents:
1. Navigate to **BigQuery Studio** in the Google Cloud Console.
2. Click on the **Notebooks** tab.
3. Import the demo notebook `Bigquery_knowledge_graph_demo.ipynb` (or `NEXT_DEMO_clinical_trials_platform.ipynb` from the `notebooks/` directory) directly into your environment.

**Don't forget to clean up:** To avoid incurring unnecessary charges to your Google Cloud account, please remember to delete the BigQuery datasets and Cloud Storage buckets used in this tutorial once you are finished exploring the solution.