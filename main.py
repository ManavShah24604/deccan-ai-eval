import csv
import openai
import json
import time


def evaluate_responses(input_csv, output_csv, rubrics, rubric_weights, api_key):
    openai.api_key = api_key
    i = 0
    with open(input_csv, mode='r', encoding='utf-8') as file:
        print(i)
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames + ['Score']  # Adding score to output fields

        with open(output_csv, mode='a', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if file.tell() == 0:
                writer.writeheader()

            for row in reader:
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
                        total_score *= 10
                        row['Score'] = total_score
                        break  # Exit retry loop on success
                    except Exception as e:
                        print("error ", e)
                        attempts += 1
                        if attempts < 3:
                            time.sleep(1)  # Wait 1 second before retrying
                        else:
                            row['Score'] = "Error"

                writer.writerow(row)
        print(i)
        i += 1

    print(f"Evaluation completed. Results appended to {output_csv}")


# Example usage
evaluate_responses(
    input_csv='New English Intructions and Response - Instruction folowing (New) - Responses.csv',
    output_csv='result.csv',
    rubrics=['Rule_Adherence','Extra_corrections' ],
    rubric_weights=[0.6, 0.4],
)
