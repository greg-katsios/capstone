#!/usr/bin/env python3
"""
MCP Server for Behavioral Research - Simulated Research Participant

This server simulates a research participant with specific demographics,
personality traits, and decision-making patterns. It's designed for
educational purposes to demonstrate how MCP servers work and how they
can be used in behavioral research.

"""

import json
import random
from typing import Any
from pydantic import AnyUrl
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    Resource,
    INVALID_PARAMS,
    INTERNAL_ERROR,
    TextResourceContents,
    ReadResourceResult
)


# Simulated Participant Profile
PARTICIPANT = {
    "id": "P001",
    "age": 28,
    "gender": "Non-binary",
    "education": "Bachelor's Degree",
    "occupation": "Software Developer",
    "personality": {
        "openness": 0.75,  # 0-1 scale (Big Five trait)
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

# Interaction history
interaction_history = []

# Create MCP server instance
server = Server("research-participant-server")


@server.list_resources()
async def list_resources() -> list[Resource]:
    """
    List available resources (data the LLM can access).
    In this case, we expose the participant's profile.
    """
    return [
        Resource(
            uri="participant://profile",
            name="Participant Profile",
            mimeType="application/json",
            description="Complete profile of the simulated research participant"
        )
    ]


@server.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """
    Read a specific resource.
    Returns the participant profile as JSON.
    """
    uri_str = str(uri)
    if uri_str == "participant://profile":
        return json.dumps(PARTICIPANT, indent=2)
    else:
        raise ValueError(f"Unknown resource: {uri_str}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List available tools (functions the LLM can call).
    These represent different research methods.
    """
    return [
        Tool(
            name="conduct_survey",
            description="Ask the participant a survey question and receive their response based on their personality and values",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The survey question to ask the participant"
                    },
                    "question_type": {
                        "type": "string",
                        "enum": ["likert", "open_ended", "yes_no"],
                        "description": "Type of question being asked"
                    }
                },
                "required": ["question", "question_type"]
            }
        ),
        Tool(
            name="play_trust_game",
            description="Play a trust game experiment with the participant. You send an amount, they decide how much to return.",
            inputSchema={
                "type": "object",
                "properties": {
                    "amount_sent": {
                        "type": "number",
                        "description": "Amount you send to the participant (0-100). This amount is tripled."
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context or framing for the game"
                    }
                },
                "required": ["amount_sent"]
            }
        ),
        Tool(
            name="conduct_interview",
            description="Have an open-ended conversation/interview with the participant on a specific topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic or question for the interview"
                    }
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="get_interaction_history",
            description="Retrieve the history of all interactions with this participant",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle tool calls from the LLM.
    This is where the actual research methods are implemented.
    """

    try:
        if name == "conduct_survey":
            # Validate inputs
            if "question" not in arguments or "question_type" not in arguments:
                raise ValueError("Missing required arguments: question and question_type")

            question = arguments["question"]
            question_type = arguments["question_type"]

            # Generate response based on personality and question type
            response = generate_survey_response(question, question_type)

            # Log interaction
            interaction_history.append({
                "type": "survey",
                "question": question,
                "response": response
            })

            return [TextContent(
                type="text",
                text=f"Participant Response:\n{response}"
            )]

        elif name == "play_trust_game":
            # Validate inputs
            if "amount_sent" not in arguments:
                raise ValueError("Missing required argument: amount_sent")

            amount_sent = float(arguments["amount_sent"])
            context = arguments.get("context", "")

            if amount_sent < 0 or amount_sent > 100:
                raise ValueError("amount_sent must be between 0 and 100")

            # Simulate trust game decision
            result = play_trust_game(amount_sent, context)

            # Log interaction
            interaction_history.append({
                "type": "trust_game",
                "amount_sent": amount_sent,
                "context": context,
                "result": result
            })

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "conduct_interview":
            # Validate inputs
            if "topic" not in arguments:
                raise ValueError("Missing required argument: topic")

            topic = arguments["topic"]

            # Generate interview response
            response = generate_interview_response(topic)

            # Log interaction
            interaction_history.append({
                "type": "interview",
                "topic": topic,
                "response": response
            })

            return [TextContent(
                type="text",
                text=f"Participant Response:\n\n{response}"
            )]

        elif name == "get_interaction_history":
            return [TextContent(
                type="text",
                text=json.dumps(interaction_history, indent=2)
            )]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


def generate_survey_response(question: str, question_type: str) -> str:
    """
    Generate a survey response based on participant personality.
    This is a simplified simulation - real implementations would be more sophisticated.
    """
    p = PARTICIPANT["personality"]
    v = PARTICIPANT["values"]

    if question_type == "likert":
        # Generate 1-5 Likert scale response
        # Higher openness and agreeableness tend toward positive responses
        base_score = 3
        modifier = (p["openness"] + p["agreeableness"]) / 2 - 0.5
        score = max(1, min(5, int(base_score + modifier * 2 + random.uniform(-0.5, 0.5))))

        likert_labels = {
            1: "Strongly Disagree",
            2: "Disagree",
            3: "Neutral",
            4: "Agree",
            5: "Strongly Agree"
        }

        return f"{score} - {likert_labels[score]}"

    elif question_type == "yes_no":
        # Generate yes/no based on agreeableness
        if random.random() < p["agreeableness"]:
            return "Yes"
        else:
            return "No"

    elif question_type == "open_ended":
        # Generate a text response reflecting personality
        if p["openness"] > 0.6:
            tone = "thoughtful and nuanced"
        elif p["conscientiousness"] > 0.6:
            tone = "structured and detailed"
        else:
            tone = "straightforward"

        return f"[This is a simulated {tone} response. In a real system, this would use the LLM to generate an actual response based on the participant's profile and the question: '{question}']"


def play_trust_game(amount_sent: float, context: str) -> dict:
    """
    Simulate participant's decision in a trust game.

    Trust game rules:
    1. Researcher sends amount (0-100)
    2. Amount is tripled
    3. Participant decides how much to return

    Decision is based on participant's trust and fairness values.
    """
    tripled_amount = amount_sent * 3

    # Calculate return amount based on participant values
    # Higher fairness -> return more (closer to fair split)
    # Higher trust -> return more
    # Some randomness for realism

    fairness_factor = PARTICIPANT["values"]["fairness"]
    trust_factor = PARTICIPANT["values"]["trust"]

    # Expected fair return would be to split the profit equally
    # Profit = tripled_amount - amount_sent
    # Fair split = amount_sent + (profit / 2) = amount_sent + (tripled_amount - amount_sent) / 2
    fair_return = amount_sent + (tripled_amount - amount_sent) / 2

    # Actual return is influenced by fairness and trust
    return_percentage = (fairness_factor * 0.7 + trust_factor * 0.3)
    random_factor = random.uniform(0.85, 1.15)  # Add 15% variance

    amount_returned = min(tripled_amount, fair_return * return_percentage * random_factor)

    # Participant's reasoning
    if return_percentage > 0.7:
        reasoning = "I believe in being fair and reciprocating trust. I want to return a generous amount."
    elif return_percentage > 0.5:
        reasoning = "I think it's important to be fair, but I also want to benefit from this opportunity."
    else:
        reasoning = "I'm being cautious. While I appreciate the gesture, I need to look out for myself."

    return {
        "amount_you_sent": amount_sent,
        "amount_received_by_participant": tripled_amount,
        "amount_returned_to_you": round(amount_returned, 2),
        "your_final_amount": round(100 - amount_sent + amount_returned, 2),
        "participant_final_amount": round(tripled_amount - amount_returned, 2),
        "participant_reasoning": reasoning,
        "context_provided": context if context else "None"
    }


def generate_interview_response(topic: str) -> str:
    """
    Generate an interview response based on personality traits.
    In a real system, this would use the LLM with a specific persona.
    """
    p = PARTICIPANT["personality"]

    # Adjust verbosity based on extraversion
    if p["extraversion"] > 0.6:
        length = "detailed and enthusiastic"
    elif p["extraversion"] < 0.4:
        length = "brief and thoughtful"
    else:
        length = "moderate"

    # Adjust style based on openness
    if p["openness"] > 0.6:
        style = "creative and explorative"
    else:
        style = "practical and concrete"

    return f"""[This is a simulated interview response. In a real implementation, this would use the LLM to generate an authentic response.]

The participant would provide a {length} response with a {style} perspective on the topic: "{topic}"

Their response would reflect:
- Openness to experience: {p['openness']:.2f} (higher = more abstract/creative thinking)
- Conscientiousness: {p['conscientiousness']:.2f} (higher = more structured responses)
- Extraversion: {p['extraversion']:.2f} (higher = more enthusiastic/verbose)
- Agreeableness: {p['agreeableness']:.2f} (higher = more positive/cooperative tone)
- Neuroticism: {p['neuroticism']:.2f} (higher = more concern/anxiety expressed)

Profile context: {PARTICIPANT['age']}-year-old {PARTICIPANT['gender']} {PARTICIPANT['occupation']} with {PARTICIPANT['education']}."""


async def main():
    """
    Main entry point for the MCP server.
    This runs the server using stdio transport.
    """
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
