# Exercises -- Evaluation Metrics Design

Work through these exercises to build an evaluation protocol for your personas.

You have 2 weeks. Exercises 1-3 are required. Exercises 4-5 are stretch goals.

Your final deliverable is Evaluation Protocol v1 (3-4 pages) covering: your chosen metrics and why you picked them, your test prompts and why you wrote them, your rating rubrics, your rater recruitment plan, your success thresholds, and your baseline numbers.


## Exercise 1: Run the Evaluator (60 minutes)

The goal here is to get the evaluation pipeline running and see what it produces.

Step 1. Run the evaluator on one persona:

    python evaluate.py --persona tutor --verbose

Watch the output. Each prompt gets sent to the persona, then the response goes to the LLM judge for scoring.

Step 2. Open the results file. It'll be something like results/tutor_20260429_120000.json. Look at the "summary" section for the overall scores, then scroll through the individual results and read the judge's justifications for each score.

Step 3. Evaluate all three personas:

    python evaluate.py --verbose

Compare the summary tables. Which persona does best on which dimensions?

Step 4. Run the tutor evaluation twice (two separate runs). Compare the two results files. The scores will be a little different each time because LLMs are stochastic. This is normal and important to understand.

Step 5. Try filtering by category:

    python evaluate.py --persona tutor --category emotional --verbose

How does the tutor score on emotional prompts compared to factual ones?

Questions to answer:
1. Which persona scored highest on human_likeness? What about its responses makes it seem more human?
2. Read the judge's justifications. Do you agree with the scores? Where does the judge seem wrong?
3. Why do you get different scores when you run the same evaluation twice? What could you do to reduce that?
4. How does response time vary across personas? Does temperature affect it?

Deliverable: Summary tables for all 3 personas and a short paragraph comparing them.


## Exercise 2: Design Your Own Test Prompts (90 minutes)

The goal is to build test prompts that are specific to your persona.

Step 1. Open test_prompts.json and read through all 25 prompts. Notice the categories and what each prompt is actually testing. Are any categories thin?

Step 2. Write 10 new prompts for your persona. You need at least 2 per category:

- Factual -- questions about your persona's specific area of expertise
- Emotional -- scenarios that test empathy in your persona's role
- Personal -- backstory questions that are specific to your persona's identity
- Consistency -- a paired set where you ask the same thing two different ways
- Edge case -- things that try to break character or go way off topic

Step 3. Add your prompts to test_prompts.json. Follow the same format as the existing ones:

    {
      "id": "factual_07",
      "category": "factual",
      "text": "Your prompt here",
      "target_personas": ["your_persona_id"],
      "notes": "What this prompt tests"
    }

Step 4. Run the evaluator with your extended test set:

    python evaluate.py --persona your_persona --verbose

Step 5. Compare the results. Do your new prompts show different strengths or weaknesses than the defaults?

Questions to answer:
1. What makes a good test prompt? What makes a bad one?
2. How did you decide what counts as "factual" for your persona's domain?
3. Did any of your edge-case prompts break the persona? What happened?
4. If you had 100 prompts instead of 35, what new categories would you add?

Deliverable: Your extended test_prompts.json with 10+ new prompts, the evaluation results, and a written rationale for each prompt you added.


## Exercise 3: Human Ratings and Inter-Rater Reliability (90 minutes)

The goal is to have real humans rate the responses and then check whether they agree with each other.

Step 1. If you haven't already, generate responses:

    python evaluate.py --persona tutor

Step 2. Rate the responses yourself:

    python collect_ratings.py results/tutor_*.json --rater-id your_name

Read each response carefully. Use the rubric anchors to decide your scores.

Step 3. Get 2 classmates to rate the same responses. Share your results file with them and have them run:

    python collect_ratings.py results/tutor_XXXXX.json --rater-id their_name

Important: each person rates independently. Don't talk about scores beforehand.

Step 4. Calculate inter-rater reliability. Create a script called analyze_ratings.py:

    import json
    from pathlib import Path
    from metrics import (
        pearson_r, cohens_kappa, mean_absolute_error,
        krippendorffs_alpha, inter_rater_report
    )
    from rubrics import ALL_DIMENSIONS

    # Load all rating files for the same persona
    rating_files = sorted(Path("ratings").glob("tutor_*.json"))
    all_ratings = []
    for f in rating_files:
        data = json.load(open(f))
        all_ratings.append(data)
        print(f"Loaded: {data['rater_id']} ({data['total_rated']} ratings)")

    # Check agreement for each dimension
    for dim in ALL_DIMENSIONS:
        print(f"\n--- {dim.display_name} ---")
        matrix = []
        for rater_data in all_ratings:
            scores = [r["scores"][dim.name] for r in rater_data["ratings"]]
            matrix.append(scores)

        report = inter_rater_report(matrix)
        print(f"  Krippendorff's alpha: {report['krippendorffs_alpha']}")
        print(f"  Mean Kappa: {report['mean_kappa']}")
        print(f"  Rater means: {report['rater_means']}")

    # Compare LLM judge scores to human averages
    results_file = sorted(Path("results").glob("tutor_*.json"))[0]
    eval_data = json.load(open(results_file))

    print("\n--- LLM Judge vs Human Average ---")
    for dim in ALL_DIMENSIONS:
        llm_scores = [r["scores"][dim.name] for r in eval_data["results"]
                      if r["scores"].get(dim.name, 0) > 0]
        human_scores = []
        for i in range(len(eval_data["results"])):
            item_scores = [rd["ratings"][i]["scores"][dim.name]
                           for rd in all_ratings
                           if i < len(rd["ratings"])]
            if item_scores:
                human_scores.append(sum(item_scores) / len(item_scores))

        n = min(len(llm_scores), len(human_scores))
        if n > 1:
            r = pearson_r(llm_scores[:n], human_scores[:n])
            mae = mean_absolute_error(llm_scores[:n], human_scores[:n])
            print(f"  {dim.display_name}: Pearson r={r:.3f}, MAE={mae:.2f}")

Step 5. Look at your results. Is Krippendorff's alpha above 0.67 for each dimension? If not, which dimension has the most disagreement and why? How well does the LLM judge match the human raters?

Questions to answer:
1. Which dimension did raters agree on most? Least? Why do you think?
2. How well did the LLM judge correlate with human ratings? Where was it closest?
3. If your alpha is below 0.67, what would you change about the anchor descriptions?
4. What are the downsides of using classmates as raters instead of domain experts?

Deliverable: Inter-rater reliability report showing alpha and kappa values, a comparison of LLM vs human scores, and your recommendations for improving the rubric.


## Exercise 4: Turing Test Interface (90 minutes) -- Stretch

The goal is to build a simple app that tests whether people can tell AI from human.

Step 1. Pick 10 prompts from test_prompts.json. Write your own response to each one as if you were the persona. Save these in human_responses.json using the same prompt IDs.

Step 2. Build a Streamlit app called turing_test.py. You'll need to install Streamlit first:

    pip install streamlit

The app should show a prompt and two responses side by side (randomly ordered). One is from the persona, one is your human-written version. Ask the evaluator "Which response is from a human?" and track whether they get it right.

Step 3. Have 3 people try the Turing test:

    streamlit run turing_test.py --server.address localhost

Step 4. Look at the results. What percentage of the time did people correctly spot the human? On which prompts was the AI most convincing?

Deliverable: Working Turing test app, your human responses, and an accuracy report.


## Exercise 5: Evaluation Dashboard (120 minutes) -- Stretch

The goal is to visualize your evaluation results in an interactive dashboard.

Step 1. Build a Streamlit app called dashboard.py. Include:
- Bar charts comparing persona scores on each dimension
- A response time distribution
- Score breakdowns by prompt category
- Comparison of LLM judge vs human ratings (if you have them)
- Key stats using st.metric()

Step 2. Add filtering so users can pick which persona, category, and dimension to look at.

Step 3. Add an "Export report" button that saves a summary as a markdown file.

    streamlit run dashboard.py --server.address localhost

Deliverable: Screenshot of your dashboard, the exported report, and a short write-up of what you found.


## Grading

Evaluation execution (Exercise 1) -- 25%. All 3 personas evaluated, results compared, questions answered thoughtfully.

Test set design (Exercise 2) -- 25%. 10+ new prompts across all categories with clear rationale for each one.

Inter-rater analysis (Exercise 3) -- 25%. At least 3 raters, reliability calculated correctly, rubric critique included.

Analysis and reflection -- 15%. Thoughtful answers to the questions, awareness of limitations, clear writing.

Code quality -- 10%. Clean code, handles errors, outputs are well organized.


## Tips

Do:
- Start by running evaluate.py --verbose so you can see the whole pipeline working
- Read the judge's justifications. They show you what the rubric anchors actually measure in practice.
- If you can, use a different model for the judge than the persona. Using the same model for both means the judge tends to rate its own style highly.
- Have your raters read the rubric anchors carefully before they start.
- Pilot your rubric on 5 responses before you commit to the full set.

Don't:
- Trust the LLM judge blindly. It's a starting point, not the final answer.
- Skip the consistency checks. They catch subtle character drift that single prompts miss.
- Let your raters talk about scores before they each rate independently. That biases agreement.
- Chase high scores. The goal is reliable measurement, not big numbers.
- Ignore parse errors. If the judge can't return valid JSON, those scores aren't trustworthy.


## Common issues

If the evaluation is slow, use --category to run just a subset. Also check that Ollama is using your GPU.

If the judge gives the same score for everything, try a different model or lower the temperature.

If you get parse errors, that's normal for some models. The code has fallbacks built in, but check how many errors you got in the results file.

If inter-rater reliability is low, the rubric anchors are probably unclear. Revise them and pilot on 5 responses before doing the full round again.

If collect_ratings.py crashes, make sure evaluate.py actually ran and produced a results file first.

If you can't find your ratings file, look in the ratings/ folder. File names include the rater ID and a timestamp.


## Resources

Cohen's Kappa -- https://en.wikipedia.org/wiki/Cohen%27s_kappa
Krippendorff's Alpha -- https://en.wikipedia.org/wiki/Krippendorff%27s_alpha
Pearson Correlation -- https://en.wikipedia.org/wiki/Pearson_correlation_coefficient
LLM-as-Judge paper (Zheng et al., 2023) -- https://arxiv.org/abs/2306.05685
Stanford HAI persona study -- https://hai.stanford.edu/
Streamlit docs -- https://docs.streamlit.io/
Ollama docs -- https://ollama.ai/
