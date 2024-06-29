import plotly.graph_objects as go
import numpy as np
import json
import re
import re


def split_string_to_chunk_words(s, chunk_size=20):  # average sentence length
    # Split the string into words
    words = s.split()
    # Split words into chunks of 10
    chunks = [" ".join(words[i:i + chunk_size])
              for i in range(0, len(words), chunk_size)]
    return chunks


def split_string_to_sentences(s, marks=[',', '.', '...']):
    import re

    # Adjust the pattern to match sentences including the specified punctuation marks at their end
    # The following pattern assumes that a sentence ends with one of the punctuation marks and may be followed by spaces
    # We use non-capturing groups (?:) for the marks to include them in the matches
    pattern = '(.*?(?:' + '|'.join(re.escape(mark) for mark in marks) + '))\s*'

    # Use re.findall to get sentences including their terminating punctuation
    sentences = re.findall(pattern, s)

    # Check if the last part of the string after the last punctuation mark is non-empty and add it as a sentence
    last_part = s[len(''.join(sentences)):].strip()
    if last_part:
        sentences.append(last_part)

    return sentences


def replace_quotes(text):
    # This pattern matches single quotes that are not immediately preceded by a letter (part of a contraction)
    # and not immediately followed by a letter or the end of a word (possessive or contraction at the end of a word).
    # It effectively targets single quotes used for quoting.
    pattern = r"(?<!\w)'(?!'\w|')"

    # Replace the matched single quotes with double quotes
    replaced_text = re.sub(pattern, '"', text)

    return replaced_text


def remove_newlines_and_spaces(text):
    # This regex will find any number of spaces (including none) around each newline character
    return re.sub(r'\s*\n\s*', '', text)


def extract_json_objects(text, **kwargs):
    text = remove_newlines_and_spaces(text)
    if "{" in text and "}" not in text:
        text = text + '}'
    try:
        json_obj = extract_json_objects_v3(text, **kwargs)
    except Exception as e:
        # print(e)
        try:
            json_obj = extract_json_objects_v2(text, **kwargs)
        except Exception as e:
            # print(e)
            json_obj = extract_json_objects_v1(text, **kwargs)
    return json_obj


def extract_json_objects_v1(text, replace_space=False, replace_newline=False, replace_quote=False):
    # Remove newline and optionally space characters for easier processing
    if replace_newline:
        text = text.replace('\n', "")
    if replace_space:
        text = text.replace(' ', "")
    if replace_quote:
        text = replace_quotes(text)

    # Remove markdown code block indicators and leading/trailing whitespace
    text = re.sub(r'(```json|```)', '', text).strip()
    text = text.replace('False', 'false')
    text = text.replace('True', 'true')

    # Attempt to find JSON structure using a regular expression
    # This regex looks for the JSON starting with either a '[' or '{'
    # and continues until the corresponding ']' or '}'
    match = re.search(r'(\{.*?\})', text, re.DOTALL)
    if match:
        json_part = match.group(0)
        return json.loads(json_part)


def extract_json_objects_v2(text, replace_space=False, replace_newline=True, replace_quote=True):
    # Remove newline and optionally space characters for easier processing
    if replace_newline:
        text = text.replace('\n', "")
    if replace_space:
        text = text.replace(' ', "")
    if replace_quote:
        text = replace_quotes(text)

    # Remove markdown code block indicators and leading/trailing whitespace
    text = re.sub(r'(```json|```)', '', text).strip()
    text = text.replace('False', 'false')
    text = text.replace('True', 'true')
    return json.loads(text)


def extract_json_objects_v3(text, replace_space=False, replace_newline=False, replace_quote=False):
    # Remove newline and optionally space characters for easier processing
    if replace_newline:
        text = text.replace('\n', "")
    if replace_space:
        text = text.replace(' ', "")
    if replace_quote:
        text = replace_quotes(text)

    code_pattern = re.compile(r'```(?:json)?(.*?)```', re.DOTALL)

    # Find all matches
    text = code_pattern.findall(text)[0]

    # Strip leading/trailing whitespace from each match
    text = text.strip()
    text = text.replace('False', 'false')
    text = text.replace('True', 'true')
    return json.loads(text)


def plot_population_history(p_history, save_html_path=None, display=False):
    x_data = {}
    y_data = {}
    hover_texts = {}

    # Collect data for each unique ID
    for i, p in enumerate(p_history):
        for u in p.units:
            if u.ID not in x_data:
                x_data[u.ID] = []
                y_data[u.ID] = []
                hover_texts[u.ID] = []
            x_data[u.ID].append(i)
            y_data[u.ID].append(u.fitness)
            hover_texts[u.ID].append(
                f'ID: {u.ID}' + '<br>' + f'fitness: {u.fitness}' + '<br>' + f'method: {u.mutant_method}')

    fig = go.Figure()

    # Add scatter plot for each unique ID
    for id in x_data:
        fig.add_trace(go.Scatter(
            x=x_data[id],
            y=y_data[id],
            mode='lines+markers',
            marker=dict(size=8, color=x_data[id],
                        colorscale='Viridis', showscale=False),
            text=hover_texts[id],
            hoverinfo='text',
            name=f'ID: {id}'
        ))

    # Add line plot for elites' fitness
    fig.add_trace(go.Scatter(
        x=list(range(len(p_history))),
        y=[max(p.elites, key=lambda elite: elite.fitness).fitness for p in p_history],
        mode='lines',
        name='Elites',
        line=dict(color='red', width=2)
    ))

    fig.update_layout(
        title='Fitness Over Iterations',
        xaxis_title='Iteration',
        yaxis_title='Fitness',
    )

    if save_html_path:
        fig.write_html(save_html_path)
    if display:
        fig.show()


if __name__ == '__main__':
    text = """
What an intriguing prompt! Let's dive into a thought experiment to challenge our assumptions about the problem specification.

Instead of simply presenting the problem, let's ask the user to write down all the relevant information and identify what's missing. This approach can help us uncover potential biases, assumptions, or gaps in our understanding.

Here's a possible story about spending 10 years to understand love:

"I've spent the last decade studying love, pouring over philosophical texts, conducting interviews with couples, and experimenting with different approaches to relationships. I've tried to understand the intricacies of romantic love, platonic love, and even self-love. I've read about the biology of attachment, the psychology of attachment styles, and the sociology of cultural norms surrounding love.

"I've also explored the concept of love through art, music, and literature. I've analyzed the works of poets like Rumi and Shakespeare, and musicians like The Beatles and Adele. I've watched films that portray love in all its forms, from romantic comedies to tragic dramas.

"Despite my efforts, I've come to realize that love is a complex, multifaceted phenomenon that defies easy explanation. It's a mix of emotions, thoughts, and behaviors that can't be reduced to a single formula or theory. I've learned that love is context-dependent, culturally relative, and highly subjective.

"However, my journey has also taught me that love is a fundamental human need, a driving force behind many of our actions and decisions. It's a source of joy, comfort, and meaning that can bring people together and transcend boundaries.

"In the end, I've come to understand that love is a mystery that can't be fully grasped, but it's a mystery that's worth exploring. It's a journey that requires patience, empathy, and self-awareness, but it's a journey that can lead to profound personal growth and fulfillment."

Now, let's revise the original instruction to incorporate this new perspective:

```
{
    "mutant": {
        "Instruction": "Spend 10 years exploring the concept of love, and write a story about your journey. Consider the complexities, nuances, and mysteries of love. Reflect on what you've learned, what you still don't understand, and how your understanding of love has evolved over time."
    }
}
```

This revised instruction encourages the user to embark on a deeper, more introspective journey to understand love, rather than simply presenting a solution. It invites them to explore the complexities of love, reflect on their own experiences, and share their insights in a narrative format.
"""
    json_obj = extract_json_objects(text=text)
    print(json_obj)
