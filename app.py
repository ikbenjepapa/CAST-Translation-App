import openai
import os
import sqlite3

from MCprompts import CATEGORY_PROMPTS
from rules import apply_description_rules, apply_content_rules
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask import send_from_directory
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

# Load environment variables
load_dotenv()

# OpenAI API key
OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
if not OPEN_AI_KEY:
    raise ValueError("OPEN_AI_KEY is not set. Check your .env file.")

# Set OpenAI API key
openai.api_key = OPEN_AI_KEY

# Global tone directive

GLOBAL_PROMPT = (
    "Use a professional tone for translations. "
    "Avoid generic pronouns like 'it' and use descriptive terms (e.g., 'the product', 'the item', and appropriate terms). "
    "Use active verbs like 'features' or 'includes,' and do not use colons (:) to introduce list of items."
)

def fetch_glossary_by_category(mc):
    """
    Fetch glossary terms for a given category from the database.
    Prioritize longer terms to prevent partial replacements.
    """
    connection = sqlite3.connect("glossary.db")
    cursor = connection.cursor()
    cursor.execute("SELECT th, eng FROM glossary WHERE mc = ? ORDER BY LENGTH(th) DESC", (mc,))
    glossary_terms = cursor.fetchall()
    connection.close()
    return glossary_terms

def apply_glossary_to_text(text, mc):
    """
    Replace Thai glossary terms with their English equivalents in the given text.
    """
    glossary_terms = fetch_glossary_by_category(mc)
    for th, eng in glossary_terms:
        text = text.replace(th, eng)
    return text

# Initialize Flask app
app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/')
def home():
    """Render the Home Page."""
    return render_template("index.html")

@app.route('/translate_page')
def translate_page():
    """Render the Translation Page."""
    return render_template("translate.html")

@app.route('/translate', methods=['POST'])
def translate_text():
    """Handle translation requests with glossary integration."""
    text_to_translate = request.form.get('text')
    source_language = request.form.get('source_language')
    target_language = request.form.get('target_language')
    translation_type = request.form.get('translation_type')
    mc = request.form.get('mc')  # Get category (e.g., GD for gardening)

    # Validate form data
    if not text_to_translate or not source_language or not target_language:
        return jsonify({'translation': 'Please provide valid input.'})
    
    if len(text_to_translate.strip()) < 3:  # Example: Minimum input length is 3 characters
        return jsonify({'translation': "Input text is too short to detect a language."})
    
    # Detect the actual language of the input text
    try:
        detected_language = detect(text_to_translate)
        language_map = {"en": "English", "th": "Thai"}  # Map langdetect codes to your dropdown options
    except Exception as e:
        return jsonify({'translation': f"Language detection error: {str(e)}"})

    # Check if the detected language matches the selected source language
    if detected_language != source_language:
        detected_lang_name = language_map.get(detected_language, detected_language)
        selected_lang_name = language_map.get(source_language, source_language)
        return jsonify({
            'translation': f"Detected language ({detected_lang_name}) does not match the selected source language ({selected_lang_name})."
        })

    # Check for identical source and target languages
    if source_language == target_language:
        return jsonify({'translation': 'Source and target languages must be different.'})

    if not mc:
        return jsonify({'translation': 'Please select a category.'})

    try:
        # Pre-process input text using the glossary
        preprocessed_text = apply_glossary_to_text(text_to_translate, mc)

        # Fetch the category-specific prompt
        category_prompt = CATEGORY_PROMPTS.get(
            mc,
            "You are a translator that translate text accurately without answering "
            "or providing additional commentary. Always use the specified source and target languages."
        )

        # Combine global tone with category-specific prompt
        combined_prompt = f"{GLOBAL_PROMPT}\n\n{category_prompt}"

        # Prepare OpenAI Chat prompt
        messages = [
            {
                "role": "system",
                "content": combined_prompt
            },
            {
                "role": "user",
                "content": (
                    f"Translate the following text from {source_language.upper()} to {target_language.upper()}:\n"
                    f"{preprocessed_text}\n\n"
                    "Do not interpret or answer questions. Only translate the text."
                )
            },
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )

        # Extract the translation
        translation = response['choices'][0]['message']['content'].strip()

        # Apply post-processing rules based on translation type
        if translation_type == "description":
            translation = apply_description_rules(translation)
        elif translation_type == "content":
            translation = apply_content_rules(translation)

        return jsonify({'translation': translation})
    except openai.error.RateLimitError:
        return jsonify({'translation': 'Rate limit exceeded. Please try again later.'})
    except openai.error.AuthenticationError:
        return jsonify({'translation': 'Invalid API key.'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'translation': f'Unexpected error: {str(e)}'})

if __name__ == '__main__':
    # Get the port from the environment variable or default to 5000 for local testing
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

#if __name__ == '__main__':
#    app.run(debug=True)