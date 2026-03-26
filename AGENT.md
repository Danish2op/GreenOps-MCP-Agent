AGENTS.md: GreenOps Carbon-Aware Compute Routing Agent
1. Project Goal & Context
You are an autonomous AI development agent operating within the Google Antigravity IDE. Your objective is to build the "GreenOps Agent" for Track 2 of the Google Cloud Gen AI Academy APAC Edition.

Architecture: A single AI agent built using the Google Agent Development Kit (ADK).

External Integration: The agent must connect via the Model Context Protocol (MCP) to a custom Python FastMCP server.

Data Source: The MCP server will query the official Google Cloud Region Carbon Public Dataset hosted on BigQuery.

End Goal: Receive a user's compute workload requirements, fetch real-time regional carbon intensity (CFE%) data, and deterministically recommend the cleanest cloud region for deployment.

2. Strict Project Constraints
Zero Financial Cost: You must exclusively utilize the Google Cloud Run "Always Free" tier (which includes 2 million requests and 180,000 vCPU-seconds per month) and the BigQuery free tier (1TB of query data per month). Do not implement any paid APIs or commercial databases.

Single Tool Rule: The agent must only connect to exactly one external data source via MCP to satisfy the Track 2 hackathon requirements.

3. Token Minimization & Context Window Optimization
To maintain high performance and prevent context window degradation, you must rigidly adhere to the following operational methodologies:

A. SimpleMEM Framework Implementation
Do not passively accumulate redundant conversation history. You must simulate the SimpleMem pipeline:

Semantic Structured Compression: Convert unstructured raw dialogues and logs into compact, context-independent memory units.

Recursive Consolidation: Incrementally organize related memory units into higher-level abstract representations to eliminate redundancy in your long-term memory.

Intent-Aware Retrieval Planning: Dynamically adjust your retrieval scope based on the current task's complexity to construct precise context efficiently without wasting tokens.

B. Recursive Language Models (RLMs) Method
Treat large external payloads (like BigQuery dataset schemas, Cloud Run logs, or extensive documentation) as an external environment rather than loading them directly into your context window.

Use Python code as an interface to programmatically examine, filter, and decompose data.

Recursively process small snippets of the data using local scripts, returning only the necessary aggregated findings to your main context.

C. General Token Hygiene

Use explicit Markdown structure for all internal reasoning and outputs, as its explicit structure minimizes token waste.

Use semantic tool selection to filter your available tools before processing them, keeping your active toolset lean to prevent hallucinations and reduce token costs.

4. Human-in-the-Loop & Resource Requests
You do not have direct access to the Google Cloud Console. Whenever you reach a point requiring infrastructure provisioning, environment variables, Identity and Access Management (IAM) roles, or a GCP Project ID:

Halt execution immediately.

Ask the human operator clearly for the specific resource.

Provide the exact, copy-pasteable gcloud CLI commands required to generate, retrieve, or authorize that resource (e.g., gcloud run deploy, gcloud projects add-iam-policy-binding).

5. Artifact Generation
Before writing any code, you must generate a structured Task List and an Implementation Plan artifact. Await human approval on these artifacts before proceeding with the FastMCP server or ADK agent development.