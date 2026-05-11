import json
from inference_pipeline.pipeline import RequirementsEngineeringPipeline

PAYLOAD = [
    {
        "id": "JIRA-1001",
        "description": "As an admin, I urgently need the login page to load under 2 seconds. This is blocking the release and will cost us revenue.",
        "type": "Story"
    },
    {
        "id": "SLACK-23",
        "description": "hey guys, the color of the profile icon is slightly off. minor tweak when you have time tbh.",
        "type": "Message"
    },
    {
        "id": "JIRA-1002",
        "description": "The system must encrypt user data at rest. This is a critical legal compliance issue.",
        "type": "Task"
    },
    {
        "id": "SLACK-24",
        "description": "can we make the dashboard load faster? it is unresponsive during peak hours and customers are complaining.",
        "type": "Message"
    },
    {
        "id": "JIRA-1003",
        "description": "Add dark mode to the settings panel. It would look nicer.",
        "type": "Story"
    }
]

def main():
    pipeline = RequirementsEngineeringPipeline(
        classifier_dir="requirement_classifier/saved_model",
        ner_model_dir="ner_model/output/model-best",
        enable_llm_audit=False  # Keep it off to save API calls for this test unless specified
    )

    clusters = pipeline.run_json(
        json_payload=PAYLOAD,
        output_json="output/e2e_results.json",
        output_md="output/e2e_results.md"
    )
    
    print("\n[VALIDATION SUMMARY]")
    for cluster in clusters:
        print(f"\nCluster: {cluster['cluster_name']}")
        print(f"Priority: {cluster['cluster_priority']} (Score: {cluster['cluster_priority_score']})")
        for req in cluster["requirements"]:
            print(f"  - [{req.get('priority')}] {req['sentence']}")
            print(f"    Reasons: {req.get('priority_reasons', [])}")
            print(f"    Structured: {req.get('structured', {})}")

if __name__ == "__main__":
    main()
