import csv
import openai
import json
import time
import pandas as pd


def evaluate_responses(input_xlsx, output_csv, rubrics, rubric_weights, api_key):
    openai.api_key = api_key

    df = pd.read_excel(input_xlsx)  # Read Excel file
    fieldnames = list(df.columns) + ['Score']  # Adding score to output fields

    with open(output_csv, mode='a', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if file.tell() == 0:
            writer.writeheader()

        for index, row in df.iterrows():
            print(index)
            question = row['Question']
            answer = row['subjective_response']

            prompt = f"""
            Evaluate the following answer based on the given rubrics.

            Question: {question}
            Answer: {answer}

            Rubrics: {json.dumps(rubrics)}

            Provide output as JSON where each rubric is 0 or 1.
            """

            client = openai.OpenAI(api_key=api_key)

            attempts = 0
            while attempts < 3:
                try:
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are an evaluator scoring answers based on rubrics."},
                            {"role": "user", "content": prompt}
                        ]
                    )

                    print(response.choices[0].message.content)
                    rubric_scores = json.loads(response.choices[0].message.content)

                    total_score = sum(rubric_scores[r] * rubric_weights[i] for i, r in enumerate(rubrics))
                    total_score=1
                    total_score *= 10
                    row['Score'] = total_score
                    break  # Exit retry loop on success
                except Exception as e:
                    print(e)
                    attempts += 1
                    if attempts < 3:
                        time.sleep(1)  # Wait 1 second before retrying
                    else:
                        row['Score'] = "Error"

            writer.writerow(row.to_dict())

    print(f"Evaluation completed. Results appended to {output_csv}")


# Example usage
evaluate_responses(
    input_xlsx='New English Question Response (3).xlsx',
    output_csv='result.csv',
    rubrics=['correct_response', 'accuracy', 'depth', 'clarity', 'grammar'],
    rubric_weights=[0.3, 0.3, 0.1, 0.1, 0.1],
    api_key=''
)
