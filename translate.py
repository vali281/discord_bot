from deep_translator import GoogleTranslator
from indic_transliteration.sanscript import transliterate
from indic_transliteration import sanscript  # Add this line

def translate_text(text, target_language="en"):
    """Translates text to the specified language using Google Translate."""
    try:
        # Auto-detect and translate
        translated_text = GoogleTranslator(source="auto", target=target_language).translate(text)

        # If translation doesn't change, try transliteration (Hinglish to Hindi) and re-translate
        if translated_text.lower() == text.lower():
            hindi_text = transliterate(text, sanscript.ITRANS, sanscript.DEVANAGARI)
            translated_text = GoogleTranslator(source="auto", target=target_language).translate(hindi_text)

        return translated_text
    except Exception as e:
        return f"Translation error: {e}"
