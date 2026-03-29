import os
import pytest
from google.adk.agents import LlmAgent
from google.genai import types
from mcp_server.geospatial import get_region_coordinates
from mcp_server.main import get_renewable_forecast, convert_cloud_cost

# -------------------------------------------------------------
# Configuration & Masters Setup
# -------------------------------------------------------------
# The Testing Master explicitly evaluates whether the Output from 
# the GreenOps orchestrator actually successfully managed to hit
# the specialized Tools and produce a proper recommendation.

TESTING_MASTER_INSTRUCTION = """You are the specialized QA Testing Master.
Your sole job is to evaluate the text output of the GreenOps Orchestrator Agent.
Look for explicitly stated:
1. Optimal Spatial Region with a CFE percentage
2. Temporal Recommendation (e.g. delaying for wind/solar)
3. Financial Estimate (the converted cost)
4. Infrastructure Action (JSON payload or Git instruction)

If ANY of these four elements are missing, contradictory, or hallucinatory: Output exactly "FAIL:" followed by the exact issue perfectly so it can be corrected.
If it looks perfect, concise, and structured, output exactly: "PASS: All masters contributed successfully."
"""

testing_master = LlmAgent(
    model="gemini-2.5-pro", # Use the pro model for rigorous validation
    name="testing_master",
    instruction=TESTING_MASTER_INSTRUCTION,
)

# -------------------------------------------------------------
# Unit Tests (Individual Masters)
# -------------------------------------------------------------

def test_geospatial_mapping():
    """Unit Test for Spatial Mapping dependency."""
    coords = get_region_coordinates("europe-north2")
    assert coords is not None, "Testing Master: europe-north2 coordinates must exist."
    assert coords[0] == 60.1695
    assert coords[1] == 24.9354

def test_weather_master_tool():
    """Unit Test for the Temporal Weather Master Tool."""
    res = get_renewable_forecast("us-west1")
    assert "error" not in res, f"Testing Master: Weather API failed: {res}"
    assert res["region"] == "us-west1", "Testing Master: Wrong region returned by Weather API."
    assert len(res["forecasts"]) > 0, "Testing Master: No forecast data received."
    assert "wind_speed_kmh" in res["forecasts"][0], "Testing Master: Missing wind data."

def test_financial_master_tool():
    """Unit Test for the FinOps Master Tool."""
    res = convert_cloud_cost(amount=100.0, from_currency="USD", to_currency="AUD")
    assert "error" not in res, f"Testing Master: Frankfurter API failed: {res}"
    assert res["original_amount"] == 100.0, "Testing Master: Amount mutation error."
    assert "converted_amount" in res, "Testing Master: Failed to convert."
    assert res["converted_currency"] == "AUD", "Testing Master: Incorrect target currency."

# -------------------------------------------------------------
# Smoke Test (Integration via Runner)
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_full_mixture_of_masters_smoke():
    """Complete product smoke test evaluated by the autonomous Testing Master.
    
    NOTE: For this to run accurately, a standalone local MCP server should be running on localhost:8080.
    """
    try:
        from greenops_agent.agent import root_agent
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
    except ImportError as e:
        pytest.fail(f"Testing Master: Import error during integration setup: {e}")

    session_service = InMemorySessionService()
    session = await session_service.create_session(state={}, app_name="test_app", user_id="test_user")
    
    runner = Runner(
        app_name="test_app",
        agent=root_agent,
        session_service=session_service,
    )

    test_prompt = "I need to run a 24-hour ML training job covering $45 USD in compute costs. Should I use europe-north2 or us-central1 right now? Delay if needed for wind. And tell me the price in AUD. Please submit a PR json."
    content = types.Content(role="user", parts=[types.Part(text=test_prompt)])
    
    response_text = ""
    try:
        async for event in runner.run_async(session_id=session.id, user_id="test_user", new_message=content):
            if hasattr(event, 'content') and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text
    except Exception as e:
        # If the MCP server isn't running, this will typically raise an SSE error
        pytest.skip(f"Testing Master: MCP Server may be down, skipping integration chunk. Error: {e}")

    # Now, feed the output to the standalone Testing Master agent
    eval_content = types.Content(role="user", parts=[types.Part(text=f"Agent Output:\n{response_text}")])
    evaluator_runner = Runner(app_name="test_app", agent=testing_master, session_service=session_service)
    
    eval_session = await session_service.create_session(state={}, app_name="eval_app", user_id="eval_user")
    evaluation_text = ""
    async for event in evaluator_runner.run_async(session_id=eval_session.id, user_id="eval_user", new_message=eval_content):
        if hasattr(event, 'content') and event.content and event.content.parts:
             for part in event.content.parts:
                  if hasattr(part, 'text') and part.text:
                      evaluation_text += part.text
                      
    if "FAIL:" in evaluation_text:
        pytest.fail(f"Testing Master explicitly rejected the Orchestrator's work: {evaluation_text}")
    else:
        assert "PASS:" in evaluation_text, f"Testing Master did not output standard PASS sequence: {evaluation_text}"
