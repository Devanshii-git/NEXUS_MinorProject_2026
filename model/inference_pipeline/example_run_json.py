"""
example_run_json.py — Production-scale JSON Payload Integration Demo
======================================================================
Showcases how the upgraded RequirementsEngineeringPipeline ingests 
structured JSON payloads natively (from Jira, Slack, or Email), strips
noise/metadata, flattens the valuable context, and clusters the outputs.
"""

from inference_pipeline.pipeline import RequirementsEngineeringPipeline
import json

def generate_mock_jira_payload():
    return {
        "issue_tracker": "Jira",
        "ticket_id": "REQ-9941",
        "metadata": {
            "creator": "Product Owner",
            "timestamp": "2023-11-20T10:00:00Z",
            "noisy_url": "https://jira.company.com/browse/REQ-9941"
        },
        "summary": "Login timeout causes data loss",
        "description": "Users are complaining about login delays. <@U92384> It is critical to fix the payment bug. The system must handle 10000 users concurrently.",
        "comments": [
            {"user": "dev1", "text": "Urgent: security vulnerability found inside the dashboard loading script. Please fix ASAP."},
            {"user": "tester", "text": "Dashboard needs improvement. Also, users must login within 2 seconds."}
        ]
    }

def main():
    print("=" * 70)
    print("  SIMULATING PRODUCTION JSON INGESTION")
    print("=" * 70)

    # 1. Initialize Pipeline
    # Using low cluster distance for demo purposes so it splits logically
    pipeline = RequirementsEngineeringPipeline(
        cluster_distance=0.40,
        confidence_threshold=0.5
    )

    # 2. Grab Mock Jira JSON
    payload = generate_mock_jira_payload()
    
    print(f"\n[Incoming Payload]:")
    print(json.dumps(payload, indent=2))
    print("\n" + "-" * 70)

    # 3. Process the nested JSON straight into the ML pipeline using run_json!
    clusters = pipeline.run_json(
        json_payload=payload,
        output_json="output/real_world_requirements.json",
        output_md="output/real_world_requirements.md",
        print_to_console=True
    )

    if clusters:
        print("\n✓ Production integration test completed successfully.")

if __name__ == "__main__":
    main()
