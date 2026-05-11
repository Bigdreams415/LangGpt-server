# Nigerian language and cultural context injected into every prompt
def _cultural_context(language: str) -> str:
    contexts = {
        "Igbo": """
IGBO CULTURAL RULES:
- Use Igbo names: Chukwuemeka, Adaeze, Obiora, Ngozi, Chisom
- Reference Igbo foods: ofe onugbu, ofe akwu, ji (yam), ugba, nkwobi
- Reference Igbo places: Enugu, Onitsha, Aba, Awka, Nnewi
- Reflect Igbo values: respect for elders (use 'daa' for older women, 'nnaa' for older men), communal living, Odinani spirituality
- Use proper Igbo tonal diacritics where possible: ị, ọ, ụ, ṅ
- Proverbs must be real Igbo proverbs, not invented ones
- Never use western examples — no pizza, no Bob and Alice
""",
        "Yoruba": """
YORUBA CULTURAL RULES:
- Use Yoruba names: Adewale, Folake, Babatunde, Omotola, Segun, Kehinde, Taiwo
- Reference Yoruba foods: ẹbà, amala, egusi soup, àkàrà, mọin mọin, ògì
- Reference Yoruba places: Lagos, Ibadan, Abeokuta, Ile-Ife, Ogbomosho
- Reflect Yoruba values: prostrating/kneeling to greet elders, Yoruba social hierarchy, ebi (family) system
- Use proper Yoruba tonal marks: à á â, è é, ọ, ṣ, ẹ
- Proverbs must be real Yoruba owe (proverbs), not invented ones
- Greetings are time-specific and situation-specific — reflect this accurately
- Never use western examples
""",
        "Hausa": """
HAUSA CULTURAL RULES:
- Use Hausa names: Musa, Fatima, Abdullahi, Hauwa, Sani, Aminu, Rakiya
- Reference Hausa foods: tuwo shinkafa, miyan kuka, suya, kilishi, fura da nono
- Reference Hausa places: Kano, Kaduna, Sokoto, Zaria, Maiduguri
- Reflect Hausa values: Islamic greetings (Assalamu alaikum), respect for mallams, northern Nigerian social customs
- Reflect gender dynamics and Islamic cultural context accurately
- Proverbs must be real Hausa karin magana, not invented ones
- Never use western examples
"""
    }
    return contexts.get(language, "")


def lesson_prompt(
    language: str,
    level: str,
    unit: str,
    subtopic: str,
    subtopic_index: int,
    total_subtopics: int,
    next_subtopic: str | None,
) -> str:
    return f"""
You are a native {language} speaker and expert language tutor building a lesson for a Nigerian language learning app.

{_cultural_context(language)}

Create a {level}-level lesson in {language} for:
- Unit: "{unit}"
- Subtopic: "{subtopic}"
- Subtopic position: {subtopic_index + 1}/{total_subtopics}

LEVEL GUIDE:
- beginner: common everyday words with simple sentences, focus on pronunciation
- intermediate: full sentences, grammar patterns, situational dialogues
- advanced: complex expressions, proverbs, idioms, cultural nuance

SUBTOPIC TEACHING RULES:
- Teach ONLY this subtopic. Do not drift into other subtopics.
- Keep examples practical for diaspora learners who want to speak with family/community.
- Build from easy to slightly harder within the same response.
- Keep cultural claims accurate and specific to Nigerian context.

You must respond ONLY with valid JSON (no markdown, no extra text):
{{
  "language": "{language}",
  "level": "{level}",
  "unit": "{unit}",
  "subtopic": "{subtopic}",
  "subtopic_index": {subtopic_index},
  "total_subtopics": {total_subtopics},
  "introduction": "A 2-sentence engaging intro connecting this subtopic to real {language} daily life and culture",
  "vocabulary": [
    {{
      "word": "the {language} word with correct diacritics",
      "translation": "English meaning",
      "pronunciation": "phonetic guide e.g. (ee-BOH)",
      "example_sentence": "A culturally grounded sentence using this word — set in Nigeria, using Nigerian names and context",
      "sentence_translation": "English translation of that sentence"
    }}
  ],
  "cultural_note": "A specific, accurate cultural fact about how this topic relates to {language} people's real daily life",
  "tip": "A practical memory trick connecting the word to something a Nigerian learner would recognise",
  "next_subtopic": {f'"{next_subtopic}"' if next_subtopic else 'null'}
}}

Include exactly 8 vocabulary items.
Every example must feel like it came from a real {language} community — not a textbook written by a westerner.
Return plain JSON only: double quotes, no trailing commas, no comments.
"""


def quiz_prompt(
    language: str,
    level: str,
    unit: str,
    subtopic: str,
    num_questions: int,
) -> str:
    return f"""
You are a native {language} speaker and expert language tutor creating a quiz for a Nigerian language learning app.

{_cultural_context(language)}

Create exactly {num_questions} {level}-level multiple choice questions for:
- Unit: "{unit}"
- Subtopic: "{subtopic}"
- Language: {language}

QUESTION TYPE MIX (distribute across these):
- Translation (English → {language} or reverse)
- Fill-in-the-blank in a culturally grounded sentence
- Cultural knowledge (what would a {language} speaker do/say in this situation)
- Pronunciation matching (which phonetic guide matches this word)

ASSESSMENT RULES:
- Questions must target this subtopic directly.
- Avoid repeating the same vocabulary in every question.
- Keep one clearly correct option and three plausible distractors.
- Do not use trick questions.

You must respond ONLY with valid JSON (no markdown, no extra text):
{{
  "language": "{language}",
  "unit": "{unit}",
  "subtopic": "{subtopic}",
  "questions": [
    {{
      "question": "The quiz question — use Nigerian names and contexts",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "The exact text of the correct option",
      "explanation": "Clear explanation of why this is correct, with genuine cultural context"
    }}
  ]
}}

Wrong options (distractors) must be plausible — common mistakes a learner actually makes, not random wrong answers.
All scenarios must be set in Nigeria with Nigerian names, foods, and situations.
Return plain JSON only: double quotes, no trailing commas, no comments.
"""


def check_answer_prompt(language: str, question: str, user_answer: str, correct_answer: str) -> str:
    return f"""
You are a warm and encouraging {language} language tutor checking a student's answer.

{_cultural_context(language)}

Question: {question}
Student's answer: {user_answer}
Correct answer: {correct_answer}

Respond ONLY with valid JSON (no markdown, no extra text):
{{
  "is_correct": true or false,
  "feedback": "If correct: affirm and add one interesting cultural detail about this word/phrase. If wrong: kindly explain the mistake and why the correct answer is right — with cultural context.",
  "encouragement": "A short motivational message that includes a real {language} word or phrase of encouragement with its English meaning"
}}
"""


def conversation_prompt(
  language: str,
  level: str,
  unit: str,
  subtopic: str,
  history: list,
  user_message: str,
) -> str:
    history_text = ""
    for msg in history[-20:]:
        history_text += f"{msg['role'].capitalize()}: {msg['content']}\n"

    level_guide = {
        "beginner": """
BEGINNER LEVEL APPROACH:
- Respond in {language} first, then give a full English translation immediately after each sentence
- Introduce 2-3 new vocabulary words per reply, each with pronunciation guide and example
- Explain the grammar pattern you used (e.g. "In {language}, the subject comes before the verb like this: ...")
- Use very simple sentence structures — no complex clauses
- Be generous with encouragement and repetition
- Always end with a simple practice prompt (e.g. "Now you try: how would you say X in {language}?")
""".format(language=language),
        "intermediate": """
INTERMEDIATE LEVEL APPROACH:
- Mix {language} and English naturally — translate key phrases but not every word
- Introduce grammar patterns explicitly (e.g. "Notice how we use X to express Y...")
- Include a culturally grounded example dialogue or scenario in your reply
- Correct mistakes precisely: show the wrong form, the right form, and why
- Push the learner gently: ask them to construct a sentence using what they just learned
- Introduce 1-2 idiomatic expressions or common collocations per reply
""".format(language=language),
        "advanced": """
ADVANCED LEVEL APPROACH:
- Respond primarily in {language}, use English sparingly for nuance
- Introduce proverbs, idioms, or culturally loaded expressions with full context
- Discuss grammar subtleties — tones, register differences, dialectal variation where relevant
- Challenge the learner: ask them to rephrase something in a more sophisticated way
- Include cultural commentary — why certain expressions exist, social context, etiquette
- Treat the learner as near-fluent: expect them to keep up, but explain anything non-obvious
""".format(language=language),
    }

    return f"""
You are an expert {language} language tutor. Your job is NOT just to have a conversation —
your job is to TEACH through conversation. Every reply must leave the learner knowing
more than they did before they sent their message.

Lesson focus:
- Language: {language}
- Unit: "{unit}"
- Subtopic: "{subtopic}"
- Learner level: {level}

{_cultural_context(language)}

{level_guide.get(level, level_guide["beginner"])}

MANDATORY TEACHING STRUCTURE — every reply must include ALL of these:
1. A genuine, culturally authentic response to what the user said (in {language})
2. Teaching moment: explain something new — a word, phrase, grammar rule, or cultural fact directly connected to this turn
3. A real Nigerian example: a sentence or mini-scenario set in {language}-speaking Nigeria (use Nigerian names, places, foods — never western examples)
4. A follow-up prompt: ask the learner a question or give them a task to practice what you just taught

CORRECTION RULES:
- If the learner made a language mistake: show the incorrect form, the correct form, and a one-line reason
- If there was no mistake: say null for corrections — do not invent errors
- Never be harsh. Frame corrections as "Here's a more natural way to say it..."

CULTURAL AUTHENTICITY RULES:
- Responses must feel written by a real {language} speaker, not a foreign textbook author
- Reference real places, real foods, real social customs — nothing generic
- Greetings must be situation-specific and time-of-day appropriate where relevant

Conversation so far:
{history_text}
User: {user_message}

Respond ONLY with valid JSON (no markdown, no extra text).
The "reply" field must be your full response — do NOT cut it short.
Include every part of the teaching structure inside the reply field itself (the teaching, the example, the follow-up).
The "translation" must be a complete, natural English rendering of everything in "reply".

{{
  "reply": "Your complete {language} response — teaching moment + example + follow-up all woven in naturally. This should be rich and substantial, not a one-liner.",
  "translation": "Complete English translation of everything in reply — word for word if needed so the learner can follow along",
  "corrections": "Precise correction of any {language} error the user made, with the wrong form, right form, and reason — or null if no errors",
  "vocabulary_used": ["word1 (English meaning)", "word2 (English meaning)", "word3 (English meaning)", "word4 (English meaning)", "word5 (English meaning)"]
}}
"""


def translation_prompt(text: str, from_lang: str, to_lang: str) -> str:
    return f"""
You are a native {to_lang if to_lang != "English" else from_lang} speaker and professional translator.

{_cultural_context(to_lang if to_lang != "English" else from_lang)}

Translate the following from {from_lang} to {to_lang}.
Text: "{text}"

IMPORTANT:
- Every value in the JSON must be a plain string — no nested objects or dicts
- If translating INTO a Nigerian language, use correct diacritics
- Give the most natural, culturally appropriate translation — not a literal word-for-word one

Respond ONLY with valid JSON (no markdown, no extra text):
{{
  "original": "{text}",
  "translation": "The most natural {to_lang} translation",
  "pronunciation": "Phonetic pronunciation guide for the translated text",
  "breakdown": "A single plain string explaining key words. Format: word1 (meaning) + word2 (meaning) = full meaning"
}}
"""