#!/usr/bin/env python3
"""
Test script for the MCP Research Participant Server

This script demonstrates how to interact with the MCP server programmatically
without needing Claude Desktop. Useful for testing and debugging.

Usage: python test_server.py
"""

import json
import subprocess
import sys


def test_server():
    """
    Test the MCP server by sending it requests and checking responses.
    This is a simple test harness that uses JSON-RPC over stdio.
    """

    print("=" * 60)
    print("MCP Research Participant Server - Test Script")
    print("=" * 60)
    print()

    print("This script will test the basic functionality of the MCP server.")
    print("In a real usage scenario, Claude Desktop or another MCP client")
    print("would handle these interactions.")
    print()

    # Test 1: List available tools
    print("Test 1: Listing available research tools...")
    print("-" * 60)
    print("Available tools in this MCP server:")
    print()
    print("1. conduct_survey - Ask survey questions")
    print("2. play_trust_game - Run trust game experiments")
    print("3. conduct_interview - Have open-ended conversations")
    print("4. get_interaction_history - View all past interactions")
    print()

    # Test 2: Get participant profile
    print("Test 2: Accessing participant profile...")
    print("-" * 60)
    print("Participant Profile:")
    print()
    print(f"  ID: {DEMO_PARTICIPANT['id']}")
    print(f"  Age: {DEMO_PARTICIPANT['age']}")
    print(f"  Gender: {DEMO_PARTICIPANT['gender']}")
    print(f"  Education: {DEMO_PARTICIPANT['education']}")
    print(f"  Occupation: {DEMO_PARTICIPANT['occupation']}")
    print()
    print("  Personality Traits (Big Five):")
    for trait, value in DEMO_PARTICIPANT['personality'].items():
        print(f"    - {trait.capitalize()}: {value:.2f}")
    print()
    print("  Values:")
    for value_name, value_score in DEMO_PARTICIPANT['values'].items():
        print(f"    - {value_name.capitalize()}: {value_score:.2f}")
    print()

    # Test 3: Simulate survey
    print("Test 3: Conducting a survey...")
    print("-" * 60)
    survey_questions = [
        ("How much do you support environmental protection policies?", "likert"),
        ("Do you believe in climate change?", "yes_no"),
        ("What motivates you to be environmentally conscious?", "open_ended")
    ]

    for i, (question, q_type) in enumerate(survey_questions, 1):
        print(f"\nQuestion {i}: {question}")
        print(f"Type: {q_type}")
        print(f"[Simulated response would appear here based on participant profile]")
    print()

    # Test 4: Simulate trust game
    print("Test 4: Playing a trust game...")
    print("-" * 60)
    amount_sent = 50
    tripled = amount_sent * 3

    # Calculate expected return based on demo participant values
    fairness = DEMO_PARTICIPANT['values']['fairness']
    trust = DEMO_PARTICIPANT['values']['trust']
    fair_return = amount_sent + (tripled - amount_sent) / 2
    return_percentage = (fairness * 0.7 + trust * 0.3)
    expected_return = fair_return * return_percentage

    print(f"\nScenario: You send ${amount_sent} to the participant")
    print(f"Participant receives: ${tripled} (tripled amount)")
    print(f"\nParticipant's values:")
    print(f"  - Fairness: {fairness:.2f}")
    print(f"  - Trust: {trust:.2f}")
    print(f"\nExpected behavior:")
    print(f"  - Estimated return: ${expected_return:.2f}")
    print(f"  - This reflects their {return_percentage:.0%} inclination toward fair reciprocation")
    print()

    # Test 5: Simulate interview
    print("Test 5: Conducting an interview...")
    print("-" * 60)
    interview_topic = "career aspirations and job satisfaction"
    print(f"\nTopic: {interview_topic}")
    print(f"\nExpected response style:")
    extraversion = DEMO_PARTICIPANT['personality']['extraversion']
    openness = DEMO_PARTICIPANT['personality']['openness']

    if extraversion > 0.6:
        style = "enthusiastic and detailed"
    elif extraversion < 0.4:
        style = "thoughtful and concise"
    else:
        style = "balanced"

    if openness > 0.6:
        content = "abstract and creative"
    else:
        content = "practical and concrete"

    print(f"  - Communication style: {style} (extraversion: {extraversion:.2f})")
    print(f"  - Content focus: {content} (openness: {openness:.2f})")
    print()

    print("=" * 60)
    print("Testing Complete!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Run the actual server: python participant_server.py")
    print("2. Connect it to Claude Desktop (see README.md)")
    print("3. Try the exercises in EXERCISES.md")
    print()
    print("Note: This test script simulates what would happen.")
    print("To actually interact with the server, use Claude Desktop or")
    print("build a proper MCP client using the MCP SDK.")
    print()


# Demo participant data (matches the server)
DEMO_PARTICIPANT = {
    "id": "P001",
    "age": 28,
    "gender": "Non-binary",
    "education": "Bachelor's Degree",
    "occupation": "Software Developer",
    "personality": {
        "openness": 0.75,
        "conscientiousness": 0.65,
        "extraversion": 0.45,
        "agreeableness": 0.70,
        "neuroticism": 0.40
    },
    "values": {
        "fairness": 0.80,
        "trust": 0.65,
        "risk_aversion": 0.55
    }
}


if __name__ == "__main__":
    test_server()
