"""
A script to generate OpenMRS 3 forms from a metadata file in Excel.
"""
import json
import os
import re
import time
import pandas as pd

# Load the metadata
METADATA_FILE = 'metadata.xlsx'
# Adjust header to start from row 2
option_sets = pd.read_excel(METADATA_FILE, sheet_name='OptionSets', header=1)
sheets = [
    'F01-MHPSS Baseline', 
    'F02-MHPSS Follow-up', 
    'F03-mhGAP Baseline', 
    'F04-mhGAP Follow-up', 
    'F05-MH Closure', 
    'F06-PHQ-9',
    'OptionSets'
    ]

# Define a global list to store all questions and answers
ALL_QUESTIONS_ANSWERS = []

# Function to fetch options for a given option set
def get_options(option_set_name):
    """
    Fetch options for a given option set name.
    
    Args:
        option_set_name (str): The name of the option set.

    Returns:
        list: A list of dictionaries containing option set details.
    """
    return option_sets[option_sets['OptionSet name'] == option_set_name].to_dict(orient='records')

def find_question_concept_by_label(questions_answers, question_label):
    " Find question concept by label. "
    for question in questions_answers:
        if question.get('question_id') == manage_id(question_label):
            return question.get('question_id')
    return manage_id(question_label)

def find_answer_concept_by_label(questions_answers, question_id, answer_label):
    " Find answer concept by label. "
    for question in questions_answers:
        if question.get('question_id') == manage_id(question_id):
            for answer in question.get('questionOptions').get('answers', []):
                if answer.get('label') == answer_label:
                    return answer.get('concept')
    return manage_id(answer_label)

def safe_json_loads(s):
    """
    Safe json loads.
    """
    try:
        return json.loads(s)
    except (ValueError, TypeError):
        return None

def manage_rendering(rendering, validation_format):
    """
    Manage rendering options.
    """
    if rendering == 'coded':
        rendering = 'radio'
    elif rendering == 'coded' and validation_format == 'multiple choice':
        rendering = 'radio'
    elif rendering == 'coded' and validation_format == 'select extended':
        rendering = 'radio'
    elif rendering == 'boolean':
        rendering = 'radio'
    elif rendering == 'numeric':
        rendering = 'numeric'
    elif rendering == 'text':
        rendering = 'text'
    return rendering

def manage_label(original_label):
    """
    Manage labels.

    Args:
        original_label (str): The original label.

    Returns:
        str: The cleaned label.
    """
    # Clean the label
    label = remove_prefixes(original_label)
    # Remove any other non-alphanumeric characters except spaces, (), -, _, /, ., <, and >
    label = re.sub(r'[^a-zA-Z0-9\s\(\)\-_\/\.<>]', '', label)
    # Remove leading ". " prefixes
    label = re.sub(r'^\.\s*', '', label)
    return label

# Manage IDs
def manage_id(original_id, id_type="question", question_id="None", all_questions_answers=None):
    """
    Manage IDs.

    Args:
        original_id (str): The original ID.
        id_type (str, optional): The ID type. Defaults to "question".
        question_id (str, optional): The question ID. Defaults to "None".
        all_questions_answers (list, optional): A list of all questions and their answers. 
        Defaults to None.

    Returns:
        str: The cleaned ID.
    """
    if all_questions_answers is None:
        all_questions_answers = []
    cleaned_id = remove_prefixes(original_id)
    cleaned_id = re.sub(r'\s*\(.*?\)', '', cleaned_id)
    # Replace "/" with "Or"
    cleaned_id = re.sub(r'/', ' Or ', cleaned_id)
    if not detect_range_prefixes(cleaned_id):
        # Replace "-" with a space
        cleaned_id = re.sub(r'-', ' ', cleaned_id)
        # Replace "_" with a space
        cleaned_id = re.sub(r'_', ' ', cleaned_id)
    # Replace "-"
    cleaned_id = re.sub(r'-', 'To', cleaned_id)
    # Replace "<"
    cleaned_id = re.sub(r'<', 'Less Than', cleaned_id)
    # Replace "<"
    cleaned_id = re.sub(r'>', 'More Than', cleaned_id)
    cleaned_id = camel_case(cleaned_id)
    # Remove any other non-alphanumeric characters
    cleaned_id = re.sub(r'[^a-zA-Z0-9_-]', '', cleaned_id)
    # Remove leading and trailing underscores
    cleaned_id = re.sub(r'^_+|_+$', '', cleaned_id)
    # Replace multiple underscores with a single underscore
    cleaned_id = re.sub(r'_+', '_', cleaned_id)
    cleaned_id = cleaned_id[0].lower() + cleaned_id[1:]
    if id_type == "answer" and cleaned_id == 'other':
        cleaned_id = question_id+cleaned_id.capitalize()
        #print(cleaned_id)
    if all_questions_answers is not None:
        duplicate_count = 1
        original_cleaned_id = cleaned_id
        while any(q['question_id'] == cleaned_id for q in all_questions_answers):
            cleaned_id = f"{original_cleaned_id}_{duplicate_count}"
            duplicate_count += 1
    return cleaned_id

def remove_prefixes(text):
    """
    Remove numerical prefixes from the beginning of the string.
    Examples of prefixes: "1. ", "1.1 ", "1.1.1 ", etc.

    Parameters:
    text (str): The input string from which to remove prefixes.

    Returns:
    str: The string with the prefixes removed.
    """
    if not detect_range_prefixes(text):
        # Convert text to string before using re.sub
        text = str(text)
        # Use re.sub to remove the matched prefix
        text = re.sub(r'^\d+(\.\d+)*\s*', '', text)
    return text

def detect_range_prefixes(text):
    """
    Detect ranges in the beginning of the string.
    """
    pattern = r"(\d+-\d+|\> \d+|< \d+|\d+ - \d+|\d+-\d+)"
    matches = re.findall(pattern, str(text))  # Convert text to string
    return bool(matches)

def camel_case(text):
    """
    Camel case a string.
    """
    words = text.split()
    camel_case_text = words[0].lower()  # Move this line outside the function
    for word in words[1:]:
        camel_case_text += word.capitalize()
    return camel_case_text

def build_skip_logic_expression(expression: str, questions_answers) -> str:
    """
    Build a skip logic expression from an expression string.

    Args:
        expression (str): An expression string.

    Returns:
        str: A skip logic expression.
    """
    # Regex pattern to match the required parts
    pattern = r"\[([^\]]+)\]\s*(<>|!==|==)\s*'([^']*)'"
    uuid_pattern = r'[a-fA-F0-9]{8}-' \
                '[a-fA-F0-9]{4}-' \
                '[a-fA-F0-9]{4}-' \
                '[a-fA-F0-9]{4}-' \
                '[a-fA-F0-9]{12}|' \
                '[a-fA-F0-9]{32}'
    match = re.search(pattern, expression)

    if match:
        original_question_label, operator, original_cond_answer = match.groups()
        if operator == '<>':
            operator = '!=='
        elif operator != '!==':
            return 'Only conditional operator "different than" noted !== is supported'
        # Check if original_question_label is a 36 character UUID
        if re.match(uuid_pattern, original_question_label):
            question_id = original_question_label
        else:
            question_id = find_question_concept_by_label(questions_answers, original_question_label)
        # Check if original_cond_answer is a 36 character UUID
        if re.match(uuid_pattern, original_cond_answer):
            cond_answer = original_cond_answer
        else:
            cond_answer = find_answer_concept_by_label(
                questions_answers, original_question_label, original_cond_answer
                )
        return f"{question_id} {operator} '{cond_answer}'"

    return "Invalid expression format"

def generate_question(row, columns, question_translations):
    """
    Generate a question JSON from a row of the OptionSets sheet.

    Args:
        row (pandas.Series): A row of the OptionSets sheet.
        columns (list): A list of column names in the OptionSets sheet.

    Returns:
        dict: A question JSON.
    """

    if row.isnull().all() or pd.isnull(row['Question']):
        return None  # Skip empty rows or rows with empty 'Question'

    # Manage values and default values
    original_question_label = (row['Label if different'] if 'Label if different' in columns and
                            pd.notnull(row['Label if different']) else row['Question'])
    question_label_translation = (
        row['Translation - Question'] if 'Translation - Question' in columns and
                            pd.notnull(row['Translation - Question']) else None
                            )

    question_label = manage_label(original_question_label)
    question_id = manage_id(original_question_label)

    question_concept_id = (row['External ID'] if 'External ID' in columns and
                        pd.notnull(row['External ID']) else question_id)

    question_datatype = (row['Datatype'].lower() if pd.notnull(row['Datatype']) else 'radio')

    validation_format = (row['Validation (format)'] if 'Validation (format)' in columns and
                        pd.notnull(row['Validation (format)']) else '')

    question_required = (str(row['Mandatory']).lower() == 'true' if 'Mandatory' in columns and
                        pd.notnull(row['Mandatory']) else False)

    question_rendering = manage_rendering(question_datatype, validation_format)

    # Build the question JSON
    question = {
        "id": question_id,
        "label": question_label,
        "type": "obs",
        "required": question_required,
        "questionOptions": {
            "rendering": question_rendering,
            "concept": question_concept_id
        },
        "validators": safe_json_loads(validation_format)
    }

    question_translations[question_label] = question_label_translation

    if 'Default value' in columns and pd.notnull(row['Default value']):
        question['default'] = row['Default value']

    if 'Question' in columns and pd.notnull(row['Question']):
        question['questionInfo'] = question_label

    if 'Calculation' in columns and pd.notnull(row['Calculation']):
        question['questionOptions']['calculate'] = {"calculateExpression": row['Calculation']}

    if 'Skip logic' in columns and pd.notnull(row['Skip logic']):
        question['hide'] = {"hideWhenExpression": build_skip_logic_expression(
            row['Skip logic'], ALL_QUESTIONS_ANSWERS
            )}

    if 'OptionSet name' in columns and pd.notnull(row['OptionSet name']):
        options = get_options(row['OptionSet name'])
        question['questionOptions']['answers'] = [
            {
                "label": manage_label(opt['Answers']),
                "concept": (opt['External ID'] if 'External ID' in columns and 
                                pd.notnull(opt['External ID'])
                                else manage_id(opt['Answers'], id_type="answer",
                                                question_id=question_id,
                                                all_questions_answers=ALL_QUESTIONS_ANSWERS)),
            }
            for opt in options
        ]

        ALL_QUESTIONS_ANSWERS.append({
            "question_id": question['id'],
            "question_label": question['label'],
            "questionOptions": {
                "concept": question['questionOptions']['concept'],
                "answers": question['questionOptions']['answers']
            }
        })

    # Rename the variable inside the 'with' statement
    with open('all_questions_answers.json', 'w', encoding='utf-8') as file:
        json.dump(ALL_QUESTIONS_ANSWERS, file, indent=4)

    return question

def generate_form(sheet_name, form_translations):
    """
    Generate a form JSON from a sheet of the OptionSets sheet.

    Args:
        sheet_name (str): The name of the sheet in the OptionSets sheet.

    Returns:
        dict: A form JSON.
    """
    form_data = {
        "name": sheet_name,
        "description": "MSF Form - "+sheet_name,
        "version": "1",
        "published": True,
        "uuid": "",
        "processor": "EncounterFormProcessor",
        "encounter": "Consultation",
        "retired": False,
        "referencedForms": [],
        "pages": []
    }

    # Adjust header to start from row 2
    df = pd.read_excel(METADATA_FILE, sheet_name=sheet_name, header=1)
    columns = df.columns.tolist()

    # concept_ids is defined here, not inside the function
    concept_ids_set = set()

    pages = df['Page'].unique()

    # Keep track of total questions and answers
    count_total_questions = 0
    count_total_answers = 0

    for page in pages:
        page_df = df[df['Page'] == page]

        form_data["pages"].append({
            "label": f"{page}", 
            "sections": []
        })

        for section in page_df['Section'].unique():
            section_df = page_df[page_df['Section'] == section]
            section_label = (
                section_df['Section'].iloc[0] if pd.notnull(section_df['Section'].iloc[0])
                            else '')

            questions = [generate_question(row, columns, form_translations)
                        for _, row in section_df.iterrows()
                        if not row.isnull().all() and pd.notnull(row['Question'])]

            questions = [q for q in questions if q is not None]

            count_total_questions += len(questions)
            count_total_answers += sum(
                len(q['questionOptions']['answers']) if 'answers' in q['questionOptions']
                else 0 for q in questions
                )

            form_data["pages"][-1]["sections"].append({
                "label": section_label,
                "isExpanded": False,
                "questions": questions
            })

    return form_data, concept_ids_set, count_total_questions, count_total_answers

def generate_translation_file(form_name, language, translations_list):
    """
    Generate a translation file JSON.

    Args:
        form_name (str): The name of the form.
        language (str): The language of the translations.
        translations (dict): A dictionary containing the translations.

    Returns:
        dict: A translation file JSON.
    """
    translation_file = {
        "uuid": "",
        "form": form_name,
        "description": f"{language.capitalize()} Translations for '{form_name}'",
        "language": language,
        "translations": translations_list
    }

    return translation_file

# Generate forms and save as JSON
OUTPUT_DIR = './generated_form_schemas'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the data
all_concept_ids = set()
all_forms = []
TOTAL_QUESTIONS = 0
TOTAL_ANSWERS = 0

# Start the timer
start_time = time.time()

for sheet in sheets:
    translations_data = {}
    form, concept_ids, total_questions, total_answers = generate_form(sheet, translations_data)
    translations = generate_translation_file(sheet, 'ar', translations_data)
    json_data = json.dumps(form, indent=4)
    translations_json_data = json.dumps(translations, indent=4)
    try:
        json.loads(json_data)  # Validate JSON format
        with open(os.path.join(OUTPUT_DIR, f"{sheet}.json"), 'w', encoding='utf-8') as f:
            f.write(json_data)
        print(f"Configuration file for form {sheet} generated successfully!")
        json.loads(translations_json_data)  # Validate JSON format
        with open(
            os.path.join(OUTPUT_DIR, f"{sheet}_translation_ar.json"), 'w', encoding='utf-8'
            ) as f:
            f.write(translations_json_data.encode('utf-8').decode('unicode_escape'))
        print(f"Translation file for form {sheet} generated successfully!")
        print()
    except json.JSONDecodeError as e:
        print(f"JSON format error in form generated from sheet {sheet}: {e}")
        print(f"JSON format error in translations form generated from sheet {sheet}: {e}")
    all_concept_ids.update(concept_ids)
    all_forms.append(form)
    TOTAL_QUESTIONS += total_questions
    TOTAL_ANSWERS += total_answers

# Count the number of forms generated
FORMS_GENERATED = len(sheets)

# End the timer
end_time = time.time()

# Calculate the total time taken
total_time = end_time - start_time

# Print the completion message with the number of forms generated
print("Forms generation completed!")
print(f"{FORMS_GENERATED} forms generated in {total_time:.2f} seconds")
print(f"Total number of questions across all forms: {TOTAL_QUESTIONS}")
print(f"Total number of answers across all forms: {TOTAL_ANSWERS}")
