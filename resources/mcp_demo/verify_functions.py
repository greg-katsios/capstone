#!/usr/bin/env python3
"""
Quick verification script to test that all functions work correctly.
"""

import sys
import json

# Import the functions from participant_server
from participant_server import (
    PARTICIPANT,
    generate_survey_response,
    play_trust_game,
    generate_interview_response
)

def test_survey_responses():
    """Test all survey question types."""
    print("Testing survey functions...")

    # Test likert
    response = generate_survey_response("Test question", "likert")
    assert " - " in response, "Likert response should have format 'N - Label'"
    print(f"  [OK] Likert: {response}")

    # Test yes/no
    response = generate_survey_response("Test question", "yes_no")
    assert response in ["Yes", "No"], "Yes/no response should be Yes or No"
    print(f"  [OK] Yes/No: {response}")

    # Test open-ended
    response = generate_survey_response("Test question", "open_ended")
    assert len(response) > 0, "Open-ended response should not be empty"
    print(f"  [OK] Open-ended: {response[:50]}...")

    print("  All survey tests passed!\n")

def test_trust_game():
    """Test trust game function."""
    print("Testing trust game...")

    result = play_trust_game(50, "Test context")

    assert "amount_you_sent" in result
    assert result["amount_you_sent"] == 50
    assert result["amount_received_by_participant"] == 150
    assert "amount_returned_to_you" in result
    assert "participant_reasoning" in result

    print(f"  [OK] Trust game works")
    print(f"  [OK] Sent $50, participant received $150")
    print(f"  [OK] Participant returned ${result['amount_returned_to_you']}")
    print(f"  [OK] Reasoning: {result['participant_reasoning'][:50]}...")
    print("  Trust game test passed!\n")

def test_interview():
    """Test interview function."""
    print("Testing interview...")

    response = generate_interview_response("Test topic")

    assert len(response) > 0, "Interview response should not be empty"
    assert "Test topic" in response, "Interview should mention the topic"

    print(f"  [OK] Interview works")
    print(f"  [OK] Response length: {len(response)} characters")
    print("  Interview test passed!\n")

def test_participant_profile():
    """Test that participant profile is properly defined."""
    print("Testing participant profile...")

    required_keys = ["id", "age", "gender", "education", "occupation", "personality", "values"]
    for key in required_keys:
        assert key in PARTICIPANT, f"Missing key: {key}"

    personality_traits = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
    for trait in personality_traits:
        assert trait in PARTICIPANT["personality"], f"Missing trait: {trait}"
        value = PARTICIPANT["personality"][trait]
        assert 0 <= value <= 1, f"Trait {trait} should be 0-1, got {value}"

    values = ["fairness", "trust", "risk_aversion"]
    for value_name in values:
        assert value_name in PARTICIPANT["values"], f"Missing value: {value_name}"
        value = PARTICIPANT["values"][value_name]
        assert 0 <= value <= 1, f"Value {value_name} should be 0-1, got {value}"

    print(f"  [OK] All required keys present")
    print(f"  [OK] All personality traits valid (0-1)")
    print(f"  [OK] All values valid (0-1)")
    print("  Profile test passed!\n")

def main():
    """Run all tests."""
    print("=" * 60)
    print("MCP Server Function Verification")
    print("=" * 60)
    print()

    try:
        test_participant_profile()
        test_survey_responses()
        test_trust_game()
        test_interview()

        print("=" * 60)
        print("SUCCESS: ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("The MCP server functions are working correctly.")
        print("You can now use the server with:")
        print("  npx @modelcontextprotocol/inspector python participant_server.py")
        print()
        return 0

    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"FAILED: TEST FAILED: {e}")
        print("=" * 60)
        return 1
    except Exception as e:
        print()
        print("=" * 60)
        print(f"ERROR: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
