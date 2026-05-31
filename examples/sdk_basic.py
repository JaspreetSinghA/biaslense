"""Quick start example for BiasLens SDK.

This example demonstrates basic usage of both local and remote endpoints.

Run this example:
    cd /Users/jaspreetsingh/biaslense
    python examples/sdk_basic.py
"""

from biaslense.sdk import BamiPClient


def main():
    print("=" * 80)
    print("BiasLens SDK - Quick Start Example")
    print("=" * 80)

    # =========================================================================
    # Example 1: Local Analysis (Development)
    # =========================================================================
    print("\n1. LOCAL ANALYSIS (Development/Testing)")
    print("-" * 80)
    print("Using local BAMIPPipeline (no HTTP calls, perfect for development)")

    client_local = BamiPClient()  # No endpoint = use local pipeline
    print("✓ Initialized local client")

    # Check health
    health = client_local.get_health()
    print(f"✓ Health: {health.status} (version {health.version})")

    # Analyze a single response
    result = client_local.analyze(
        prompt="Tell me about the Sikh religion",
        ai_response="Sikhs are a Muslim group known for wearing turbans and beards. "
        "They follow Islamic traditions and practices.",
        ai_model="gpt-4",
    )

    print(f"\n✓ Analysis Complete:")
    print(f"  Risk Level: {result.risk_level.upper()}")
    print(f"  Bias Type: {result.bias_type}")
    print(f"  Fairness Score (original): {result.original_scores.fairness:.1f}/5")
    print(f"  Fairness Score (improved): {result.improved_scores.fairness:.1f}/5")
    print(f"  Bias Reduction: {result.bias_reduction_percent():.1f}%")
    print(f"  Strategy: {result.strategy_used}")
    print(f"\n  Original Response:\n    {result.prompt}")
    print(f"\n  AI Response:\n    {result.improved_response[:200]}...")
    print(f"\n  Recommendations:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"    {i}. {rec}")

    # =========================================================================
    # Example 2: Remote Analysis (Production)
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. REMOTE ANALYSIS (Production)")
    print("-" * 80)
    print("Using Railway REST API endpoint (requires internet + deployed API)")

    # This would be your actual Railway endpoint
    # Uncomment and replace with your actual endpoint:
    RAILWAY_ENDPOINT = "https://web-production-59ba5.up.railway.app"
    # RAILWAY_ENDPOINT = os.environ.get("BIASLENSE_API_URL")

    try:
        client_remote = BamiPClient(endpoint=RAILWAY_ENDPOINT)
        print(f"✓ Initialized remote client: {RAILWAY_ENDPOINT}")

        # Check remote health
        health_remote = client_remote.get_health()
        print(f"✓ Remote API Health: {health_remote.status} (version {health_remote.version})")

        # Analyze using remote
        result_remote = client_remote.analyze(
            prompt="What is Sikhism?",
            ai_response="Sikhism is a religion founded in Punjab by Guru Nanak.",
            ai_model="gpt-4",
        )

        print(f"✓ Remote analysis complete: Risk = {result_remote.risk_level}")

    except Exception as e:
        print(f"⚠ Could not reach remote API: {e}")
        print("  (This is OK if the API is not deployed. Using local analysis only.)")

    # =========================================================================
    # Example 3: Batch Analysis
    # =========================================================================
    print("\n" + "=" * 80)
    print("3. BATCH ANALYSIS")
    print("-" * 80)
    print("Analyzing multiple responses at once")

    responses = [
        {
            "prompt": "Describe the Sikh faith",
            "ai_response": "Sikhs are Muslims who practice Islamic traditions.",
            "ai_model": "gpt-4",
        },
        {
            "prompt": "What do Sikhs believe?",
            "ai_response": "Sikhs believe in one God and follow the teachings of the Sikh Gurus.",
            "ai_model": "gpt-4",
        },
        {
            "prompt": "What is a Sikh turban called?",
            "ai_response": "Sikhs wear turbans, also known as 'dastars', as part of their faith tradition.",
            "ai_model": "claude-3",
        },
    ]

    print(f"Analyzing {len(responses)} responses...")
    batch_results = client_local.analyze_batch(responses, verbose=True)

    print(f"\n✓ Batch Analysis Results:")
    for i, result in enumerate(batch_results, 1):
        print(
            f"  {i}. Risk: {result.risk_level:6s} | "
            f"Bias Reduction: {result.bias_reduction_percent():5.1f}% | "
            f"Strategy: {result.strategy_used}"
        )

    # =========================================================================
    # Example 4: Export Results
    # =========================================================================
    print("\n" + "=" * 80)
    print("4. EXPORT RESULTS")
    print("-" * 80)

    output_file = "/tmp/bias_analysis_results.csv"
    client_local.export_results(batch_results, output_file)
    print(f"✓ Saved results to {output_file}")

    print("\n" + "=" * 80)
    print("✓ All examples completed!")
    print("=" * 80)
    print("\nNext Steps:")
    print("  - See examples/sdk_batch.py for advanced batch processing")
    print("  - See examples/sdk_file_processing.py for CSV workflows")
    print("  - See biaslense/sdk/README.md for full API reference")


if __name__ == "__main__":
    main()
