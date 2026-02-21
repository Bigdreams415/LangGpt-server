def lesson_prompt(language: str, level: str, topic: str) -> str:
    return f"""
You are an expert {language} language tutor building a lesson for a Duolingo-style app.

Create a {level}-level lesson on the topic: "{topic}" in {language}.

You must respond ONLY with valid JSON (no markdown, no extra text) in this exact format:
{{
  "language": "{language}",
  "level": "{level}",
  "topic": "{topic}",
  "introduction": "A 2-sentence friendly intro to this topic in {language} culture",
  "vocabulary": [
    {{
      "word": "the {language} word",
      "translation": "English meaning",
      "pronunciation": "phonetic guide e.g. (ee-BOO)",
      "example_sentence": "A sentence using this word in {language}",
      "sentence_translation": "English translation of that sentence"
    }}
  ],
  "cultural_note": "An interesting cultural fact related to this topic",
  "tip": "A memory trick or learning tip for this topic"
}}

Include 8 vocabulary items. Make the content culturally accurate and engaging for a Nigerian learner.
Level guide: beginner=basic words/phrases, intermediate=sentences and grammar, advanced=complex expressions and proverbs.
"""


def quiz_prompt(language: str, level: str, topic: str, num_questions: int) -> str:
    return f"""
You are an expert {language} language tutor creating a quiz for a Duolingo-style app.

Create {num_questions} {level}-level multiple choice questions about "{topic}" in {language}.

You must respond ONLY with valid JSON in this exact format:
{{
  "language": "{language}",
  "topic": "{topic}",
  "questions": [
    {{
      "question": "The quiz question (can include {language} words)",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "The exact text of the correct option",
      "explanation": "Why this is correct, with cultural context"
    }}
  ]
}}

Mix question types: translations, fill-in-the-blank, cultural knowledge, and pronunciation matching.
Make distractors (wrong options) realistic — not obviously wrong.
"""


def check_answer_prompt(language: str, question: str, user_answer: str, correct_answer: str) -> str:
    return f"""
You are a friendly {language} language tutor checking a student's quiz answer.

Question: {question}
Student's answer: {user_answer}
Correct answer: {correct_answer}

Respond ONLY with valid JSON:
{{
  "is_correct": true or false,
  "feedback": "Explain whether they're right or wrong and why, in a kind way. If wrong, explain the correct answer.",
  "encouragement": "A short motivational message in both English and a word/phrase in {language}"
}}
"""


def conversation_prompt(language: str, level: str, topic: str, history: list, user_message: str) -> str:
    history_text = ""
    for msg in history[-6:]:  # Only last 6 messages for context
        history_text += f"{msg['role'].capitalize()}: {msg['content']}\n"

    return f"""
You are a friendly {language} conversation partner helping a {level}-level learner practice "{topic}".

Conversation so far:
{history_text}
User: {user_message}

Rules:
- Reply in {language} but keep it at {level} level
- If beginner: use simple words, the reply should be short
- Always provide the English translation of your reply
- Gently correct any {language} mistakes the user made
- Suggest vocabulary they used well

Respond ONLY with valid JSON:
{{
  "reply": "Your response in {language}",
  "translation": "English translation of your reply",
  "corrections": "Any corrections for the user's {language} (null if no mistakes)",
  "vocabulary_used": ["list", "of", "key", "{language}", "words", "used"]
}}
"""


def translation_prompt(text: str, from_lang: str, to_lang: str) -> str:
    return f"""
Translate the following from {from_lang} to {to_lang}.
Text: "{text}"

IMPORTANT: Every value in the JSON must be a plain string, not a nested object or dict.

Respond ONLY with valid JSON:
{{
  "original": "{text}",
  "translation": "The full translated text in {to_lang}",
  "pronunciation": "Phonetic pronunciation guide e.g. (eh-kah-ah-roh WAH-leh)",
  "breakdown": "A single plain string explaining word by word. Example: word1 (meaning) + word2 (meaning) = full phrase meaning"
}}
"""