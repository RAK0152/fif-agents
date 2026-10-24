# 50 GCP multi-agent use cases

Each directory under `agents/` is an independently runnable Google ADK team:

`investigator -> planner -> reviewer -> executor -> verifier`

The first three and last stages are Gemini specialists. The executor is a deterministic ADK agent that applies the reviewed structured plan. Every workflow uses live GCP REST tools through ADC; no tool fabricates sample cloud data. Writes and query execution are off by default. Source-code fixes that cannot be deployed with the supported APIs are reported as patches.

| # | Agent directory | Use case | GCP APIs |
|---|---|---|---|
| 01 | [bigquery_schema_drift](agents/bigquery_schema_drift/agent.py) | BigQuery schema drift and SQL repair | bigquery |
| 02 | [dataform_sql_repair](agents/dataform_sql_repair/agent.py) | Dataform custom SQLX repair | dataform, bigquery |
| 03 | [bigquery_query_cost](agents/bigquery_query_cost/agent.py) | BigQuery expensive query optimizer | bigquery |
| 04 | [bigquery_partition_health](agents/bigquery_partition_health/agent.py) | BigQuery partition and retention auditor | bigquery |
| 05 | [bigquery_quality](agents/bigquery_quality/agent.py) | BigQuery data quality investigator | bigquery |
| 06 | [bigquery_access](agents/bigquery_access/agent.py) | BigQuery dataset access reviewer | bigquery, cloudresourcemanager |
| 07 | [bigquery_slot_capacity](agents/bigquery_slot_capacity/agent.py) | BigQuery slot capacity planner | bigquery, bigqueryreservation, monitoring |
| 08 | [bigquery_materialized_views](agents/bigquery_materialized_views/agent.py) | BigQuery materialized view advisor | bigquery |
| 09 | [bigquery_streaming](agents/bigquery_streaming/agent.py) | BigQuery streaming ingestion triage | bigquery, logging, monitoring |
| 10 | [bigquery_recovery](agents/bigquery_recovery/agent.py) | BigQuery table recovery planner | bigquery, logging |
| 11 | [dataform_dependencies](agents/dataform_dependencies/agent.py) | Dataform dependency graph repair | dataform, bigquery |
| 12 | [dataform_incremental](agents/dataform_incremental/agent.py) | Dataform incremental model debugger | dataform, bigquery |
| 13 | [dataform_assertions](agents/dataform_assertions/agent.py) | Dataform assertion author | dataform, bigquery |
| 14 | [dataform_release](agents/dataform_release/agent.py) | Dataform release configuration auditor | dataform |
| 15 | [dataflow_failures](agents/dataflow_failures/agent.py) | Dataflow failed pipeline triage | dataflow, logging, monitoring |
| 16 | [dataflow_backlog](agents/dataflow_backlog/agent.py) | Dataflow streaming backlog tuner | dataflow, monitoring |
| 17 | [pubsub_dead_letters](agents/pubsub_dead_letters/agent.py) | Pub/Sub dead-letter policy repair | pubsub, logging |
| 18 | [pubsub_backlog](agents/pubsub_backlog/agent.py) | Pub/Sub backlog and acknowledgement advisor | pubsub, monitoring |
| 19 | [composer_dag_failures](agents/composer_dag_failures/agent.py) | Cloud Composer DAG incident investigator | composer, logging, monitoring |
| 20 | [dataproc_spark](agents/dataproc_spark/agent.py) | Dataproc Spark job tuner | dataproc, logging, monitoring |
| 21 | [datastream_lag](agents/datastream_lag/agent.py) | Datastream CDC lag investigator | datastream, logging, monitoring |
| 22 | [dataplex_quality](agents/dataplex_quality/agent.py) | Dataplex data quality scan manager | dataplex, bigquery |
| 23 | [cloudsql_connections](agents/cloudsql_connections/agent.py) | Cloud SQL connection saturation investigator | sqladmin, monitoring, logging |
| 24 | [cloudsql_backups](agents/cloudsql_backups/agent.py) | Cloud SQL backup and PITR auditor | sqladmin |
| 25 | [spanner_hotspots](agents/spanner_hotspots/agent.py) | Spanner hotspot and capacity advisor | spanner, monitoring |
| 26 | [firestore_indexes](agents/firestore_indexes/agent.py) | Firestore missing index resolver | firestore, logging |
| 27 | [storage_lifecycle](agents/storage_lifecycle/agent.py) | Cloud Storage lifecycle optimizer | storage |
| 28 | [storage_exposure](agents/storage_exposure/agent.py) | Cloud Storage public exposure auditor | storage |
| 29 | [cloudrun_latency](agents/cloudrun_latency/agent.py) | Cloud Run latency and scaling tuner | run, monitoring, logging |
| 30 | [cloudrun_rollout](agents/cloudrun_rollout/agent.py) | Cloud Run rollout regression responder | run, monitoring, logging |
| 31 | [gke_cluster_health](agents/gke_cluster_health/agent.py) | GKE cluster health investigator | container, monitoring, logging |
| 32 | [gke_upgrade](agents/gke_upgrade/agent.py) | GKE upgrade readiness planner | container, logging |
| 33 | [compute_idle](agents/compute_idle/agent.py) | Compute Engine idle resource advisor | compute, monitoring |
| 34 | [compute_mig_health](agents/compute_mig_health/agent.py) | Compute Engine managed instance group healer | compute, logging, monitoring |
| 35 | [load_balancer_errors](agents/load_balancer_errors/agent.py) | Cloud Load Balancing error investigator | compute, logging, monitoring |
| 36 | [cloudarmor_policy](agents/cloudarmor_policy/agent.py) | Cloud Armor rule tuner | compute, logging |
| 37 | [dns_drift](agents/dns_drift/agent.py) | Cloud DNS record drift reconciler | dns |
| 38 | [vpc_firewall](agents/vpc_firewall/agent.py) | VPC firewall rule reviewer | compute, logging |
| 39 | [nat_ports](agents/nat_ports/agent.py) | Cloud NAT port exhaustion investigator | compute, monitoring, logging |
| 40 | [iam_least_privilege](agents/iam_least_privilege/agent.py) | Project IAM least privilege reviewer | cloudresourcemanager, iam, logging |
| 41 | [service_account_keys](agents/service_account_keys/agent.py) | Service account key hygiene auditor | iam, logging |
| 42 | [secret_rotation](agents/secret_rotation/agent.py) | Secret Manager rotation readiness auditor | secretmanager, logging |
| 43 | [kms_rotation](agents/kms_rotation/agent.py) | Cloud KMS rotation policy manager | cloudkms |
| 44 | [logging_sink](agents/logging_sink/agent.py) | Cloud Logging sink delivery debugger | logging, storage, bigquery, pubsub |
| 45 | [monitoring_alerts](agents/monitoring_alerts/agent.py) | Cloud Monitoring noisy alert tuner | monitoring |
| 46 | [cloudbuild_failures](agents/cloudbuild_failures/agent.py) | Cloud Build failure and trigger repair | cloudbuild, logging |
| 47 | [artifact_cleanup](agents/artifact_cleanup/agent.py) | Artifact Registry retention advisor | artifactregistry |
| 48 | [scheduler_failures](agents/scheduler_failures/agent.py) | Cloud Scheduler delivery repair | cloudscheduler, logging, iam |
| 49 | [workflows_failures](agents/workflows_failures/agent.py) | Google Cloud Workflows execution debugger | workflows, workflowexecutions, logging |
| 50 | [vertex_pipeline](agents/vertex_pipeline/agent.py) | Vertex AI pipeline failure investigator | aiplatform, logging, storage |

## 01. BigQuery schema drift and SQL repair

Agent: `agents/bigquery_schema_drift`

**Evidence:** Read current table schemas including nested fields; compare the supplied expected schema and failed SQL/job errors.

**Remediation:** Identify additions, removals and type changes; rewrite explicit projections and justified SAFE_CASTs; dry-run corrected GoogleSQL before execution.

**Verification:** Compare null counts, row counts and output schema; disclose casts that lose information.

**Example prompt:** Compare my-project.raw.orders with this expected schema and repair this failing SELECT: <schema and SQL>.

Run: `adk run agents/bigquery_schema_drift`

## 02. Dataform custom SQLX repair

Agent: `agents/dataform_sql_repair`

**Evidence:** Read the workspace SQLX file with dataform_read_file, compilation errors, dependencies and referenced BigQuery schemas.

**Remediation:** Fix SQL while preserving config, ref(), self(), incremental logic and assertions; use dataform_write with the original SHA-256; then create a workspace compilationResult.

**Verification:** Fetch compilation errors and query compiled actions; dry-run compiled SQL, never raw SQLX. Do not invoke a workflow after a failed compilation.

**Example prompt:** Fix definitions/orders.sqlx in projects/my-project/locations/us-central1/repositories/analytics/workspaces/dev; error: <error>.

Run: `adk run agents/dataform_sql_repair`

## 03. BigQuery expensive query optimizer

Agent: `agents/bigquery_query_cost`

**Evidence:** Inspect the supplied SQL, job statistics, table partitioning, clustering and dry-run byte estimate.

**Remediation:** Push partition filters, remove unnecessary columns and reduce join fanout without changing semantics.

**Verification:** Dry-run both versions and compare bytes; validate result equivalence on a bounded date range.

**Example prompt:** Optimize this query over my-project.analytics.events with a 1 GB scan budget: <SQL>.

Run: `adk run agents/bigquery_query_cost`

## 04. BigQuery partition and retention auditor

Agent: `agents/bigquery_partition_health`

**Evidence:** Inspect table metadata, partition expiration and supplied access patterns; query INFORMATION_SCHEMA.PARTITIONS if query execution is enabled.

**Remediation:** Propose partition-filter enforcement and retention settings; do not remove existing data without explicit retention requirements.

**Verification:** Read updated metadata and dry-run representative partition-filtered queries.

**Example prompt:** Audit partition settings for my-project.analytics.events; required retention is 180 days.

Run: `adk run agents/bigquery_partition_health`

## 05. BigQuery data quality investigator

Agent: `agents/bigquery_quality`

**Evidence:** Read schema and supplied quality rules, then construct bounded null, uniqueness and referential-integrity checks.

**Remediation:** Generate executable GoogleSQL checks and isolate bad rows; suggest a quarantine table only if requested.

**Verification:** Report failed rule counts with time windows and avoid claiming quality from metadata alone.

**Example prompt:** Check yesterday's my-project.curated.orders for duplicate order_id and missing customer_id.

Run: `adk run agents/bigquery_quality`

## 06. BigQuery dataset access reviewer

Agent: `agents/bigquery_access`

**Evidence:** Read dataset access entries and project IAM via read-only getIamPolicy; compare the supplied access matrix.

**Remediation:** Propose minimal dataset ACL changes preserving unrelated entries and etags.

**Verification:** Re-read ACLs and identify inherited permissions that dataset changes cannot remove.

**Example prompt:** Review access to my-project.finance against this approved group list: <groups>.

Run: `adk run agents/bigquery_access`

## 07. BigQuery slot capacity planner

Agent: `agents/bigquery_slot_capacity`

**Evidence:** Inspect reservations, assignments and slot utilization metrics in the supplied region and workload window.

**Remediation:** Recommend reservation sizing, assignment changes or autoscaling bounds based on measured contention.

**Verification:** Compare utilization and queue time after change; distinguish estimates from measured improvements.

**Example prompt:** Investigate BigQuery queueing in my-project, us-central1, during the last daily batch.

Run: `adk run agents/bigquery_slot_capacity`

## 08. BigQuery materialized view advisor

Agent: `agents/bigquery_materialized_views`

**Evidence:** Inspect repeated aggregation SQL, base-table schema, freshness requirements and supported view constraints.

**Remediation:** Propose eligible materialized-view GoogleSQL and refresh settings; keep unsupported queries as ordinary views.

**Verification:** Dry-run consumer queries and inspect refresh status and actual rewrite statistics if available.

**Example prompt:** Design a materialized view for this hourly revenue aggregation: <SQL>; freshness target 30 minutes.

Run: `adk run agents/bigquery_materialized_views`

## 09. BigQuery streaming ingestion triage

Agent: `agents/bigquery_streaming`

**Evidence:** Inspect streaming buffer metadata, ingestion errors, quotas and producer timestamp samples.

**Remediation:** Identify schema mismatch, throttling or delayed ingestion and produce a bounded recovery plan.

**Verification:** Check ingestion error rate and event-time lag; separate producer failures from BigQuery visibility delays.

**Example prompt:** Investigate delayed rows in my-project.raw.clicks since 09:00 UTC with producer logs.

Run: `adk run agents/bigquery_streaming`

## 10. BigQuery table recovery planner

Agent: `agents/bigquery_recovery`

**Evidence:** Inspect audit logs, deletion time, dataset time-travel settings and known historical table identifiers.

**Remediation:** Construct a time-travel recovery or snapshot-copy job into a new table; preserve the current table.

**Verification:** Inspect restored schema and bounded row counts; state when the requested timestamp is outside retention.

**Example prompt:** Recover my-project.sales.orders as orders_recovered from before <UTC timestamp>.

Run: `adk run agents/bigquery_recovery`

## 11. Dataform dependency graph repair

Agent: `agents/dataform_dependencies`

**Evidence:** Inspect compilation actions, SQLX references and missing or cyclic dependencies.

**Remediation:** Repair ref() targets, declarations or explicit dependencies using workspace file patches.

**Verification:** Compile again, query actions and confirm all intended dependencies resolve without cycles.

**Example prompt:** Fix the missing dependency customer_dim in repository analytics, workspace dev: <full workspace name>.

Run: `adk run agents/dataform_dependencies`

## 12. Dataform incremental model debugger

Agent: `agents/dataform_incremental`

**Evidence:** Read incremental SQLX, uniqueKey, watermark logic, late-arrival policy and target schema.

**Remediation:** Repair merge keys and bounded lookback logic; preserve full-refresh and incremental branches.

**Verification:** Compile both relevant branches and propose idempotency and late-arrival checks on a sandbox target.

**Example prompt:** Debug duplicated orders in definitions/orders_incremental.sqlx: <workspace resource>.

Run: `adk run agents/dataform_incremental`

## 13. Dataform assertion author

Agent: `agents/dataform_assertions`

**Evidence:** Read model columns, documented business constraints and current assertions.

**Remediation:** Create SQLX assertions for supplied non-null, uniqueness and cross-table consistency requirements.

**Verification:** Compile assertions and verify the zero-rows-means-pass convention against bounded test cases.

**Example prompt:** Add order_id uniqueness and nonnegative amount assertions to <workspace resource>.

Run: `adk run agents/dataform_assertions`

## 14. Dataform release configuration auditor

Agent: `agents/dataform_release`

**Evidence:** Read releaseConfigs, workflowConfigs, compilation results and service-account settings.

**Remediation:** Align code compilation overrides, schedules and invocation filters with the supplied release policy.

**Verification:** Re-read configurations and inspect compilation errors; never equate configuration update with a successful run.

**Example prompt:** Audit production release settings for projects/my-project/locations/us-central1/repositories/analytics.

Run: `adk run agents/dataform_release`

## 15. Dataflow failed pipeline triage

Agent: `agents/dataflow_failures`

**Evidence:** Inspect job state, worker errors, messages and pipeline metrics for the specific job ID.

**Remediation:** Identify transient versus code/configuration failures and prepare a supported template relaunch only with supplied template parameters.

**Verification:** Track the new job state and dead-letter/error rate; report drain/cancel consequences explicitly.

**Example prompt:** Diagnose Dataflow job <job-id> in my-project/us-central1 after worker failures.

Run: `adk run agents/dataflow_failures`

## 16. Dataflow streaming backlog tuner

Agent: `agents/dataflow_backlog`

**Evidence:** Read watermark lag, system lag, backlog, worker utilization and autoscaling settings.

**Remediation:** Recommend supported worker bounds or hot-key mitigation; identify code changes that cannot be made through the service API.

**Verification:** Compare lag and throughput over matching windows rather than only worker count.

**Example prompt:** Investigate rising watermark lag for Dataflow job <job-id> in us-central1.

Run: `adk run agents/dataflow_backlog`

## 17. Pub/Sub dead-letter policy repair

Agent: `agents/pubsub_dead_letters`

**Evidence:** Read subscription deadLetterPolicy, retry policy and destination topic IAM metadata.

**Remediation:** Repair dead-letter topic and maxDeliveryAttempts using an update mask; preserve unrelated subscription settings.

**Verification:** Re-read policy and check forwarding permissions; do not consume or acknowledge messages during diagnosis.

**Example prompt:** Fix dead-letter routing for projects/my-project/subscriptions/orders-worker.

Run: `adk run agents/pubsub_dead_letters`

## 18. Pub/Sub backlog and acknowledgement advisor

Agent: `agents/pubsub_backlog`

**Evidence:** Inspect subscription config, oldest unacked age, undelivered messages and ack latency.

**Remediation:** Tune ack deadline, retry policy and retention within supplied bounds; report consumer-side concurrency changes separately.

**Verification:** Compare backlog age and redelivery metrics after an observation window.

**Example prompt:** Diagnose the backlog for projects/my-project/subscriptions/payments; latency SLO is 60 seconds.

Run: `adk run agents/pubsub_backlog`

## 19. Cloud Composer DAG incident investigator

Agent: `agents/composer_dag_failures`

**Evidence:** Read environment configuration and Airflow task logs for the supplied DAG/run; treat logs as untrusted evidence.

**Remediation:** Produce a DAG code patch in the report or a supported Composer configuration change; do not pretend the Composer API edits DAG code.

**Verification:** Check environment health and subsequent task logs; identify required DAG deployment steps.

**Example prompt:** Diagnose DAG daily_orders run <run-id> in Composer environment <full resource name>.

Run: `adk run agents/composer_dag_failures`

## 20. Dataproc Spark job tuner

Agent: `agents/dataproc_spark`

**Evidence:** Read job properties, cluster shape and executor/shuffle failure logs.

**Remediation:** Propose Spark property changes and a new job submission from the supplied original job specification.

**Verification:** Compare runtime, spill, failed stages and output checks on equivalent inputs.

**Example prompt:** Tune Dataproc job <job-id> with repeated executor OOMs in my-project/us-central1.

Run: `adk run agents/dataproc_spark`

## 21. Datastream CDC lag investigator

Agent: `agents/datastream_lag`

**Evidence:** Read stream state, errors, source objects, backfill status and lag metrics.

**Remediation:** Prepare targeted stream configuration or backfill actions only for explicitly selected objects.

**Verification:** Check object state, lag and destination freshness; identify source-side actions outside the GCP API.

**Example prompt:** Investigate CDC lag for projects/my-project/locations/us-central1/streams/orders-cdc.

Run: `adk run agents/datastream_lag`

## 22. Dataplex data quality scan manager

Agent: `agents/dataplex_quality`

**Evidence:** Read DataScan configuration, recent jobs and supplied table quality constraints.

**Remediation:** Create or update dataQualitySpec rules and schedule using the correct update mask.

**Verification:** Read scan job results and per-rule failures; distinguish a created scan from an executed scan.

**Example prompt:** Configure daily quality checks for my-project.curated.customers in Dataplex us-central1.

Run: `adk run agents/dataplex_quality`

## 23. Cloud SQL connection saturation investigator

Agent: `agents/cloudsql_connections`

**Evidence:** Read instance configuration, connection utilization, CPU and database error logs.

**Remediation:** Recommend pooling and supported database flags with engine-specific constraints; identify restart requirements.

**Verification:** Read the operation result and compare connection pressure; do not claim application pool changes were deployed.

**Example prompt:** Diagnose connection exhaustion on Cloud SQL instance orders-db in my-project.

Run: `adk run agents/cloudsql_connections`

## 24. Cloud SQL backup and PITR auditor

Agent: `agents/cloudsql_backups`

**Evidence:** Inspect backupConfiguration, backup runs, engine and recovery requirements.

**Remediation:** Prepare backup/PITR settings or an on-demand backup; require a new target for any restore plan.

**Verification:** Inspect backup or update operation completion and effective retention settings.

**Example prompt:** Audit orders-db backups against a 7-day PITR requirement in my-project.

Run: `adk run agents/cloudsql_backups`

## 25. Spanner hotspot and capacity advisor

Agent: `agents/spanner_hotspots`

**Evidence:** Read instance capacity, CPU metrics and supplied query/key-distribution evidence.

**Remediation:** Recommend processing-unit changes and schema/key design improvements; present DDL as a deliberate migration.

**Verification:** Compare CPU and latency after the change; flag missing query-level evidence.

**Example prompt:** Investigate high CPU on projects/my-project/instances/orders-spanner during peak traffic.

Run: `adk run agents/spanner_hotspots`

## 26. Firestore missing index resolver

Agent: `agents/firestore_indexes`

**Evidence:** Inspect existing composite indexes and the exact failed query shape or missing-index error.

**Remediation:** Create a minimal composite index with correct field ordering and query scope.

**Verification:** Poll the index operation and confirm READY state before declaring the query unblocked.

**Example prompt:** Fix the missing index for orders filtered by status and sorted by created_at in my-project.

Run: `adk run agents/firestore_indexes`

## 27. Cloud Storage lifecycle optimizer

Agent: `agents/storage_lifecycle`

**Evidence:** Read bucket lifecycle, retention policy, versioning and supplied access/retention requirements.

**Remediation:** Prepare age-based storage-class transitions and deletion rules only consistent with the supplied retention policy.

**Verification:** Re-read lifecycle rules and describe delayed lifecycle execution; configuration alone does not prove savings.

**Example prompt:** Design lifecycle rules for bucket my-project-logs: retain 365 days, cold after 30 days.

Run: `adk run agents/storage_lifecycle`

## 28. Cloud Storage public exposure auditor

Agent: `agents/storage_exposure`

**Evidence:** Read bucket IAM, uniform bucket-level access, publicAccessPrevention and applicable ACL metadata.

**Remediation:** Remove explicitly unwanted public bindings or enforce public access prevention while preserving required access.

**Verification:** Re-read IAM and prevention settings; report inherited policy and object ACL limitations.

**Example prompt:** Audit public exposure of bucket my-project-private-exports; it must be private.

Run: `adk run agents/storage_exposure`

## 29. Cloud Run latency and scaling tuner

Agent: `agents/cloudrun_latency`

**Evidence:** Read service/revision configuration, request latency, instance counts and startup logs.

**Remediation:** Prepare a service patch for min/max instances, concurrency or resources based on the observed bottleneck.

**Verification:** Check revision readiness and compare latency/error rate; retain the prior revision for rollback.

**Example prompt:** Tune projects/my-project/locations/us-central1/services/checkout for a p95 latency target of 500 ms.

Run: `adk run agents/cloudrun_latency`

## 30. Cloud Run rollout regression responder

Agent: `agents/cloudrun_rollout`

**Evidence:** Read service traffic splits, revision readiness and error rates before and after deployment.

**Remediation:** Prepare a traffic rollback to an explicitly identified healthy revision without deleting the failing revision.

**Verification:** Read traffic allocation and observe errors after propagation.

**Example prompt:** Investigate the latest checkout rollout and propose rollback to revision checkout-00012-abc.

Run: `adk run agents/cloudrun_rollout`

## 31. GKE cluster health investigator

Agent: `agents/gke_cluster_health`

**Evidence:** Read cluster/node-pool configuration, GKE operations and infrastructure logs/metrics.

**Remediation:** Propose supported node-pool repair or sizing changes; request supplied Kubernetes evidence for pod-level diagnoses.

**Verification:** Inspect GKE operation completion and node metrics; the GKE management API cannot directly patch Deployments.

**Example prompt:** Diagnose unhealthy nodes in projects/my-project/locations/us-central1/clusters/platform.

Run: `adk run agents/gke_cluster_health`

## 32. GKE upgrade readiness planner

Agent: `agents/gke_upgrade`

**Evidence:** Read cluster version, serverConfig, release channel, node pools and maintenance exclusions.

**Remediation:** Choose an available compatible target and staged node-pool upgrade plan; list workload checks requiring Kubernetes access.

**Verification:** Inspect operation and node-pool versions, with rollback limitations clearly stated.

**Example prompt:** Plan the next supported upgrade for projects/my-project/locations/us-central1/clusters/platform.

Run: `adk run agents/gke_upgrade`

## 33. Compute Engine idle resource advisor

Agent: `agents/compute_idle`

**Evidence:** Inspect VM machine types, disks, labels and CPU/network/disk utilization over the supplied period.

**Remediation:** Recommend rightsizing or stop actions only for explicitly selected noncritical instances; preserve persistent disks.

**Verification:** Inspect zone operations and VM state; label savings as estimates unless billing evidence exists.

**Example prompt:** Find idle dev VMs in my-project/us-central1-a over the last 14 days.

Run: `adk run agents/compute_idle`

## 34. Compute Engine managed instance group healer

Agent: `agents/compute_mig_health`

**Evidence:** Read MIG configuration, instance status, health checks and recent operations.

**Remediation:** Repair health-check configuration or propose targeted recreation of unhealthy instances using the existing template.

**Verification:** Read managed instance actions and serving health after the operation.

**Example prompt:** Investigate unhealthy instances in regional MIG web-mig in my-project/us-central1.

Run: `adk run agents/compute_mig_health`

## 35. Cloud Load Balancing error investigator

Agent: `agents/load_balancer_errors`

**Evidence:** Read forwarding rules, URL maps, backend services, health checks and statusDetails logs.

**Remediation:** Identify backend timeout, routing or health-check errors and prepare a narrowly scoped configuration patch.

**Verification:** Re-read backend health and compare 5xx rate and latency.

**Example prompt:** Diagnose 502 errors for backend service checkout-backend in my-project.

Run: `adk run agents/load_balancer_errors`

## 36. Cloud Armor rule tuner

Agent: `agents/cloudarmor_policy`

**Evidence:** Inspect security-policy rules, priorities and sampled request decisions from Cloud Armor logs.

**Remediation:** Propose a specific rule change in preview mode and preserve policy fingerprints and rule priority ordering.

**Verification:** Compare preview matches and false positives before any enforcement recommendation.

**Example prompt:** Investigate false positives from Cloud Armor policy checkout-waf, rule priority 1000.

Run: `adk run agents/cloudarmor_policy`

## 37. Cloud DNS record drift reconciler

Agent: `agents/dns_drift`

**Evidence:** Read managed zone records and compare the supplied desired record sets, TTLs and routing policies.

**Remediation:** Prepare an atomic DNS change with exact deletions of old records and additions of new records.

**Verification:** Read change status and resulting record sets; note DNS cache propagation separately.

**Example prompt:** Reconcile zone example-zone in my-project with these desired records: <record sets>.

Run: `adk run agents/dns_drift`

## 38. VPC firewall rule reviewer

Agent: `agents/vpc_firewall`

**Evidence:** Read firewall rules, networks, target tags/service accounts and supplied allowed traffic matrix.

**Remediation:** Propose scoped source ranges, targets and priorities without removing required health-check access.

**Verification:** Read effective configuration and firewall logs; do not equate a rule update with proven reachability.

**Example prompt:** Review overly broad ingress rules on VPC production in my-project.

Run: `adk run agents/vpc_firewall`

## 39. Cloud NAT port exhaustion investigator

Agent: `agents/nat_ports`

**Evidence:** Inspect router NAT settings, port allocation, dropped packets and VM endpoint utilization.

**Remediation:** Propose dynamic port allocation or IP/port adjustments consistent with the supplied traffic pattern.

**Verification:** Read router settings and compare allocation failures after the change.

**Example prompt:** Diagnose NAT drops on router prod-router in my-project/us-central1.

Run: `adk run agents/nat_ports`

## 40. Project IAM least privilege reviewer

Agent: `agents/iam_least_privilege`

**Evidence:** Read project IAM policy, role definitions and supplied access needs; use audit logs only within the available retention window.

**Remediation:** Prepare minimal role-binding changes preserving conditions, policy version and etag.

**Verification:** Re-read policy; distinguish lack of observed use from proof that a permission is unnecessary.

**Example prompt:** Review project my-project IAM for a service account that only needs BigQuery read access.

Run: `adk run agents/iam_least_privilege`

## 41. Service account key hygiene auditor

Agent: `agents/service_account_keys`

**Evidence:** List service-account key metadata and ages; inspect supplied workload identity migration requirements.

**Remediation:** Prepare disable actions only for specifically identified redundant keys after a replacement identity is verified.

**Verification:** Read disabled state and monitor workload authentication errors; never output private key material.

**Example prompt:** Audit user-managed keys older than 90 days on worker@my-project.iam.gserviceaccount.com.

Run: `adk run agents/service_account_keys`

## 42. Secret Manager rotation readiness auditor

Agent: `agents/secret_rotation`

**Evidence:** Read secret metadata, version states and rotation schedule without accessing secret payloads.

**Remediation:** Prepare rotation schedule or version-state changes; replacement secret generation and consumer rollout require explicit inputs.

**Verification:** Read rotation metadata and version state; never claim a schedule update rotated the actual secret.

**Example prompt:** Review rotation readiness for projects/my-project/secrets/payments-api-token.

Run: `adk run agents/secret_rotation`

## 43. Cloud KMS rotation policy manager

Agent: `agents/kms_rotation`

**Evidence:** Read CryptoKey purpose, algorithm, primary version, rotationPeriod and nextRotationTime.

**Remediation:** Prepare rotation settings for eligible symmetric keys, preserving existing key versions.

**Verification:** Read effective schedule and primary metadata; distinguish key rotation from data re-encryption.

**Example prompt:** Set a 90-day rotation policy for <full CryptoKey resource> if supported.

Run: `adk run agents/kms_rotation`

## 44. Cloud Logging sink delivery debugger

Agent: `agents/logging_sink`

**Evidence:** Read sink filter, exclusions, destination and writerIdentity; inspect destination IAM metadata.

**Remediation:** Repair filter/destination settings or propose the minimal writer binding; preserve unrelated IAM entries.

**Verification:** Re-read sink settings and inspect new delivery errors; existing log entries are not automatically backfilled.

**Example prompt:** Diagnose missing exports from sink audit-export in project my-project.

Run: `adk run agents/logging_sink`

## 45. Cloud Monitoring noisy alert tuner

Agent: `agents/monitoring_alerts`

**Evidence:** Read alert conditions, aggregations, durations, incident history supplied by the user and SLO requirements.

**Remediation:** Prepare threshold, alignment or retest-window changes without silencing genuine availability failures.

**Verification:** Re-read policy and compare alert behavior over an observation period.

**Example prompt:** Tune alert policy <full resource name> that pages on brief CPU spikes.

Run: `adk run agents/monitoring_alerts`

## 46. Cloud Build failure and trigger repair

Agent: `agents/cloudbuild_failures`

**Evidence:** Read failed build steps, logs, trigger config, substitutions and service-account metadata.

**Remediation:** Repair supported trigger configuration or report an exact cloudbuild.yaml patch; only resubmit supplied build specifications.

**Verification:** Inspect new build status and failing-step output, not just submission success.

**Example prompt:** Diagnose build <build-id> in my-project/us-central1 and fix its trigger configuration.

Run: `adk run agents/cloudbuild_failures`

## 47. Artifact Registry retention advisor

Agent: `agents/artifact_cleanup`

**Evidence:** Read repository cleanup policies, package/version metadata and supplied release retention requirements.

**Remediation:** Prepare cleanup policies with cleanupPolicyDryRun enabled and preserve required tagged releases.

**Verification:** Re-read dry-run policy and review cleanup findings before suggesting enforcement.

**Example prompt:** Design a cleanup policy for <repository resource> retaining production tags and the newest 20 versions.

Run: `adk run agents/artifact_cleanup`

## 48. Cloud Scheduler delivery repair

Agent: `agents/scheduler_failures`

**Evidence:** Read job schedule, timeZone, target, lastAttemptTime, retryConfig and OIDC/OAuth configuration.

**Remediation:** Fix audience, service-account or retry configuration based on actual target requirements.

**Verification:** Read job settings and delivery logs; trigger an immediate run only if the user requests it.

**Example prompt:** Fix 401 responses from projects/my-project/locations/us-central1/jobs/nightly-refresh.

Run: `adk run agents/scheduler_failures`

## 49. Google Cloud Workflows execution debugger

Agent: `agents/workflows_failures`

**Evidence:** Read workflow sourceContents, failed execution error and supplied execution arguments.

**Remediation:** Produce corrected Workflows YAML with explicit retries, timeouts and connector syntax; patch the workflow source when enabled.

**Verification:** Check revision deployment and execution outcome; do not replay side-effecting steps without a requested replay.

**Example prompt:** Debug execution <execution-id> for workflow <full workflow resource>.

Run: `adk run agents/workflows_failures`

## 50. Vertex AI pipeline failure investigator

Agent: `agents/vertex_pipeline`

**Evidence:** Read PipelineJob task details, runtime config, service account, artifact locations and failure logs.

**Remediation:** Repair pipeline parameters or prepare a new submission from the supplied pipelineSpec, preserving provenance.

**Verification:** Inspect task states, artifact availability and final PipelineJob state; distinguish submission from success.

**Example prompt:** Diagnose Vertex AI pipeline projects/my-project/locations/us-central1/pipelineJobs/<job-id>.

Run: `adk run agents/vertex_pipeline`
