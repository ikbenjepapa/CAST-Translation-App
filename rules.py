import random
import re

def fix_units_in_translation(text):
    
    unit_replacements = {
        # Square Units
        "mm²": "sq.mm",
        "cm²": "sq.cm",
        "m²": "sq.m",
        "km²": "sq.km",
        "in²": "sq.in",
        "ft²": "sq.ft",
        "yd²": "sq.yd",
        "mi²": "sq.mi",
        "dm²": "sq.dm",
        "hm²": "sq.hm",

        # Linear Units
        "millimeter": "mm",
        "centimeter": "cm",
        "meter": "m",
        "kilometer": "km",
        "inch": "in",
        "foot": "ft",
        "yard": "yd",
        "millimeters": "mm",
        "centimeters": "cm",
        "meters": "m",
        "kilometers": "km",
        "inches": "in",
        "feet": "ft",
        "yards": "yd",

        # Cubic Units
        "mm³": "cu.mm",
        "cm³": "cu.cm",
        "m³": "cu.m",
        "km³": "cu.km",
        "in³": "cu.in",
        "ft³": "cu.ft",
        "yd³": "cu.yd",
        "mi³": "cu.mi",

        # Volume Units
        "milliliter": "ml",
        "liter": "l",
        "kiloliter": "kl",
        "gallon": "gal",
        "milliliters": "ml",
        "liters": "l",
        "kiloliters": "kl",
        "gallons": "gal",

        #count
        "pieces":"pcs",
    }

    for old_unit, new_unit in unit_replacements.items():
        # \b ensures the match is for full words only
        text = re.sub(rf"\b{re.escape(old_unit)}\b", new_unit, text, flags=re.IGNORECASE)
    
    return text

def remove_commas_from_names(text):
    """
    Remove commas (,) from product names or text.
    """
    return text.replace(",", "")

def fix_units_in_translation2(text):
    """
    Replace unwanted unit formats in the translated text with consistent 'sq.xxx' or linear unit formats.
    """
    unit_replacements = {
        # Square Units
        "mm²": "sq.mm",
        "cm²": "sq.cm",
        "m²": "sq.m",
        "km²": "sq.km",
        "in²": "sq.in",
        "ft²": "sq.ft",
        "yd²": "sq.yd",
        "mi²": "sq.mi",
        "dm²": "sq.dm",
        "hm²": "sq.hm",
    }
    
    for old_unit, new_unit in unit_replacements.items():
        text = text.replace(old_unit, new_unit)
    
    return text

def replace_transitional_phrases(text):
    """
    Replace transitional phrases with random alternatives.
    """
    # Define a list of alternatives
    transitions = ["What's more,", "Furthermore,", "Moreover,"]

    # List of transitional phrases to replace
    phrases_to_replace = ["Additionally,"]

    # Replace each phrase with a random alternative
    for phrase in phrases_to_replace:
        if phrase in text:
            text = text.replace(phrase, random.choice(transitions))
    
    return text


# Start of Description Rules
def apply_description_rules(translation):
    """
    Apply formatting rules for 'DESCRIPTION' translations.
    """
    # Rule 1: Convert to lowercase
    translation = translation.lower()

    # Rule 2:Ensure consistent unit formatting
    translation = fix_units_in_translation(translation)

    # Rule 3: Convert to uppercase
    translation = translation.upper()

    # Rule 4: Remove commas from names
    translation = remove_commas_from_names(translation)
    
    return translation


# Start of Conent Rules
def apply_content_rules(translation):
    """
    Apply formatting rules for 'CONTENT' translations.
    """
    # Rule 1: Ensure consistent unit formatting
    translation = fix_units_in_translation2(translation)

    # Rule 2: Replace transitional phrases with random alternatives
    translation = replace_transitional_phrases(translation)

    return translation
