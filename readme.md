# Fifty GCP multi-agent workflows

50 independently runnable Google ADK applications for Google Cloud operations.
Start with [usecases.md](usecases.md) for the complete catalog, example prompts,
evidence requirements, repair strategies and verification criteria.

Each application is a `SequentialAgent` with five specialists:

```text
Investigator -> Planner -> Reviewer -> Executor -> Verifier
   evidence      JSON plan   JSON review  real API calls  result checks
```

Four stages use Gemini. The executor is deterministic Python: it executes the
reviewed structured actions, stops on failure or pending work, and records results
in ADK session state. Shared code keeps the 50 applications consistent; each has
its own GCP service scope and investigation/remediation/verification instructions.

## Install

Python 3.11+ is required. From the repository root:

```bash
cd fif-agents
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` and copy with
`Copy-Item .env.example .env`. Run commands below from `fif-agents/`.

The editable installation makes `fif_agents` importable by all ADK entry points.
ADK is pinned to `2.12.0`, the version used for local validation. The model is
configurable through `FIF_MODEL`; the default is `gemini-2.5-flash`. Model access
and regional availability depend on your account.

## Authentication option A: Vertex AI with Google ADC

Install the Google Cloud CLI, select your own project, and establish ADC:

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

Set these values in `.env`:

```dotenv
FIF_AUTH_MODE=vertex
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
FIF_MODEL=gemini-2.5-flash
```

This uses ADC for both the Vertex AI model and GCP tools. No Gemini key is needed.
On Cloud Run, Compute Engine or GKE, use an attached service account or Workload
Identity with the required permissions instead of interactive login. If you
already have an approved ADC credential file, `GOOGLE_APPLICATION_CREDENTIALS`
can point to it. Do not commit credential files.

## Authentication option B: Gemini API key plus ADC for GCP

Set these values in `.env`:

```dotenv
FIF_AUTH_MODE=api_key
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
FIF_MODEL=gemini-2.5-flash
```

Create a key through [Google AI Studio](https://aistudio.google.com/apikey).
Run the same ADC login commands from option A for the resource tools. A Gemini
key authenticates model requests; it does **not** authorize BigQuery, Dataform,
IAM or other GCP management requests. All use cases target GCP resources, but in
this mode model requests use the Gemini Developer API. Use Vertex mode if you
require model traffic to go through Vertex AI as well.

`FIF_AUTH_MODE` determines the backend even if the standard backend variable is
inconsistent. Existing shell variables take precedence over `.env`; restart ADK
after changing configuration. The loader reads this project's `.env` explicitly.

## Enable APIs and grant access

Billing and the relevant service APIs must be enabled in your project. For the
first two examples, an authorized administrator can run:

```bash
gcloud services enable aiplatform.googleapis.com bigquery.googleapis.com dataform.googleapis.com --project YOUR_PROJECT_ID
```

Enable additional APIs only for workflows you use. The service names appear in
the catalog and `fif_agents/gcp.py`. API calls use the caller's ADC identity; the
code does not grant itself permissions. Typical starting permissions are:

| Work | Typical access |
|---|---|
| Gemini on Vertex AI | `roles/aiplatform.user` |
| BigQuery inspection/dry runs/SELECT | `roles/bigquery.jobUser` on the job project plus dataset-level `roles/bigquery.dataViewer` |
| BigQuery metadata only | `roles/bigquery.metadataViewer` on relevant datasets |
| Dataform reads | `roles/dataform.viewer` or the equivalent scoped permissions |
| Dataform workspace edits/compilation | Scoped permissions including `dataform.workspaces.readFile`, `dataform.workspaces.writeFile`, `dataform.compilationResults.create` |
| Logs and metrics | `roles/logging.viewer`, `roles/monitoring.viewer` as needed |
| Other service changes | Resource-specific update permissions for the exact planned operation |

These are starting points, not a universal IAM recipe. Dataform invocation uses
its configured execution identity, which needs its own BigQuery permissions.
Inspect 403 errors for missing permissions; do not grant Owner to bypass them.

## Run

Check configuration and list the applications:

```bash
fif-agents doctor
fif-agents list
```

The doctor discovers local ADC and checks configuration without validating tokens
or making model requests. Start the browser interface, or a specific terminal app:

```bash
adk web agents --host 127.0.0.1 --port 8000
# Alternatively:
adk run agents/bigquery_schema_drift
adk run agents/dataform_sql_repair
```

Open `http://127.0.0.1:8000` for the browser UI and choose any of the 50 apps.
Run one of those commands at a time. Keep the local developer UI on loopback;
this repository does not add production authentication or a hosted deployment.

Example BigQuery prompt (replace placeholders with actual inputs):

```text
Compare table my-project.raw.orders against the following expected schema:
order_id STRING, amount NUMERIC, created_at TIMESTAMP.
This query fails after an upstream schema change: <paste the actual SQL>.
Inspect the live schema, explain the drift, produce corrected GoogleSQL,
dry-run it, and run it if query execution is enabled. Use location US.
```

Example Dataform prompt:

```text
Fix definitions/orders.sqlx in
projects/my-project/locations/us-central1/repositories/analytics/workspaces/dev.
The compilation error is: <paste actual error>.
Read the existing file and BigQuery table schemas. Preserve its config and
incremental behavior. Propose the corrected SQLX and compile after writing it.
```

Supply concrete resource names, error messages, desired behavior and relevant
time windows. The workflow reports missing inputs instead of guessing them.

## Preview, SQL execution and writes

The default `.env` allows metadata reads, logs and BigQuery dry runs:

```dotenv
FIF_ALLOW_WRITES=false
FIF_EXECUTE_QUERIES=false
FIF_BQ_LOCATION=US
FIF_BQ_MAX_BYTES=1000000000
```

The report contains a proposed plan; a gated action returns `preview` and stops
the sequence. To permit validated SELECT jobs, set `FIF_EXECUTE_QUERIES=true`.
To permit reviewed mutations, set `FIF_ALLOW_WRITES=true`, restart ADK and submit
the task again. These settings enable execution for the process, not one-off
approval dialogs. SELECT queries can incur charges. Non-SELECT SQL requires the
write flag. SQL scripts and unclassified statements are rejected; use individual
reviewed statements. Every SQL execution is dry-run first and carries a maximum
bytes-billed limit. Dry runs cannot establish semantic correctness or fully
predict cost for all data sources.

The executor supports GCP REST GET/POST/PATCH/PUT/DELETE for registered Google API
origins. API shapes come from official discovery metadata. BigQuery SQL and
Dataform file writes use dedicated paths. A reviewed generic API mutation can
still be consequential: the LLM review is not a security boundary. Limit the ADC
identity's IAM permissions to the intended resources. The configured project is
the default billing/job context, not an enforced cross-project access boundary.

Dataform edits carry the original file's SHA-256 to detect changes before writing;
`NEW` means a new file that must return 404 before creation. The check is optimistic,
not an atomic server-side compare-and-swap. After writing, create a compilation
result and inspect errors. SQLX is never sent directly to BigQuery. Creating a
compilation result is a write and requires the write flag. The original content
and rollback plan should be retained; this project does not automatically commit
files, run production workflows or roll back partially completed plans.

Submitted BigQuery jobs and generic API mutations stop execution before any
dependent action. Synchronous Dataform file writes and compilations can continue
in sequence. The verifier reads operation status. If work remains pending, the
report includes the job/operation ID; ask a follow-up to verify it and replan the
remaining steps. Never assume the rest of a plan ran. API responses are bounded;
tools expose pagination tokens and agents must narrow or page large responses.

## What is implemented and what remains environment-dependent

- 50 ADK entry points, each with five agents and case-specific instructions.
- Live ADC REST tools for 29 GCP APIs, official discovery lookup, read-only POST
  support for Logging and IAM, SQL dry runs/execution and Dataform file editing.
- Structured plans/reviews, deterministic execution, per-workflow action scope,
  stop-on-error/pending behavior, read-back verification and both auth modes.
- Offline tests use mocked GCP responses. No real cloud projects, credentials,
  service changes or model calls are needed for these tests.

Live results depend on your resource names, enabled APIs, IAM, model access and
service configuration. These are operational starting points, not 50 bespoke
production integrations. For example, Composer DAG source deployment and GKE
Kubernetes object changes are not implemented by their management APIs; those
workflows return patches or next steps. No arbitrary shell execution is exposed.
Long-running operation orchestration, durable approval storage and production
hosting are not included. Default ADK sessions are intended for local development;
configure durable ADK session storage separately if needed. Resource data included
in prompts is sent to the selected model backend.

ADK 2.12 emits a deprecation warning for `SequentialAgent`; it still supports
this interface and the pinned version is tested here. Review that migration
before upgrading the ADK pin.

## Files and verification

```text
agents/<use_case>/agent.py   50 discoverable ADK applications
fif_agents/catalog.py       50 evidence/remediation/verification contracts
fif_agents/workflow.py      specialist teams and shared-state handoffs
fif_agents/models.py        typed action, plan and review schemas
fif_agents/gcp.py           ADC transport, API discovery and read tools
fif_agents/tools.py         SQL, Dataform and reviewed-plan execution
fif_agents/config.py        .env loading and backend selection
fif_agents/cli.py           catalog and configuration doctor
tests/                     offline contract/execution tests
usecases.md                full catalog and example prompts
.env.example               both auth options and execution settings
```

```bash
python -m pytest -q
python -m compileall -q fif_agents agents
```

## Official references

- [ADK sequential agents and state handoffs](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)
- [ADK Gemini configuration](https://google.github.io/adk-docs/agents/models/google-gemini/)
- [Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc)
- [BigQuery jobs.insert](https://cloud.google.com/bigquery/docs/reference/rest/v2/jobs/insert)
- [Dataform REST API](https://cloud.google.com/dataform/reference/rest)
- [Dataform workspace readFile](https://cloud.google.com/dataform/reference/rest/v1/projects.locations.repositories.workspaces/readFile)
