"""
example_run.py — Full Improved Pipeline Demo
===============================================
Demonstrates all improvements: better NER (ACTION entity), Agglomerative
clustering, multi-signal prioritization, requirement structuring,
explainability, and dynamic summarization.

Usage:
    python -m inference_pipeline.example_run
"""

from inference_pipeline.pipeline import RequirementsEngineeringPipeline


SAMPLE_TEXT = """
Users are complaining that login is too slow during peak hours.
Good morning everyone.
We should improve login speed.
The meeting is scheduled for tomorrow.
Admin users need urgent access to the audit logs.
Can you send me the meeting notes?
The system must handle payment processing within 2 seconds.
Happy Friday!
Customers should receive email notifications when orders are shipped.
Let me know when you're free.
The dashboard must load within 3 seconds.
Please RSVP by Thursday.
The checkout flow needs to be more reliable during sales events.
The payment gateway must support multiple currencies.
It is critical that user passwords are encrypted at all times.
Who is bringing the cake?
Users must be able to export reports as PDF.
The search functionality should return results in under 1 second.
The login page must support single sign-on via OAuth.
The mobile app needs to work offline without data loss.
"""


def main():
    """Run the complete improved pipeline."""
    print()
    print("*" * 70)
    print("*  AI-based Requirements Engineering — IMPROVED PIPELINE DEMO    *")
    print("*" * 70)
    print()

    # Initialize pipeline
    pipeline = RequirementsEngineeringPipeline(
        classifier_dir="requirement_classifier/saved_model",
        ner_model_dir="ner_model/output/model-best",
        summarizer_model="t5-small",
        cluster_distance=0.65,
    )

    # Run the full pipeline
    clusters = pipeline.run(
        text=SAMPLE_TEXT,
        output_json="output/requirements.json",
        output_md="output/requirements.md",
        print_to_console=True,
    )

    # Print summary
    total_reqs = sum(len(c["requirements"]) for c in clusters)
    total_sentences = len(pipeline.segment_sentences(SAMPLE_TEXT))
    high = sum(1 for c in clusters if c.get("cluster_priority") == "HIGH")
    med = sum(1 for c in clusters if c.get("cluster_priority") == "MEDIUM")
    low = sum(1 for c in clusters if c.get("cluster_priority") == "LOW")

    print(f"\n  📊 Final Statistics:")
    print(f"     Input sentences    : {total_sentences}")
    print(f"     Requirements found : {total_reqs}")
    print(f"     Clusters formed    : {len(clusters)}")
    print(f"     Priority dist.     : {high} HIGH, {med} MEDIUM, {low} LOW")
    print(f"     Output files       : output/requirements.json")
    print(f"                          output/requirements.md")
    print()


if __name__ == "__main__":
    main()
