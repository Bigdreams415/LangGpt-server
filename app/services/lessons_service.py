from typing import List, Optional

from app.schemas.lessons_schemas import (
    LessonTopicResponse,
    LessonsListResponse,
    LessonDetailResponse,
)

# Full curriculum — 16 units, each with ordered subtopics.
# Structure per unit:
#   id               : matches LessonUnit enum value
#   title            : display name
#   emoji            : icon shown in UI
#   description      : short one-liner shown on the unit card
#   level            : beginner | intermediate | advanced
#   duration_minutes : estimated time to complete the FULL unit
#   subtopics        : ordered list — learner progresses through these in order.
#                      Each entry is a dict with:
#                        name             : display name of the subtopic
#                        description      : what the learner will be able to do
#                        duration_minutes : estimated time for this subtopic alone


TOPICS_METADATA = {

    "foundations": {
        "title": "Foundations",
        "emoji": "🔤",
        "description": "Master sounds, tones and pronunciation before anything else",
        "duration_minutes": 45,
        "level": "beginner",
        "subtopics": [
            {
                "name": "The alphabet & letter sounds",
                "description": "Learn every letter and the sound it makes",
                "duration_minutes": 6,
            },
            {
                "name": "Understanding tones (high, low, mid)",
                "description": "Discover how tone changes word meaning in Igbo and Yoruba",
                "duration_minutes": 7,
            },
            {
                "name": "Vowels & consonants",
                "description": "Identify vowel and consonant patterns in the language",
                "duration_minutes": 5,
            },
            {
                "name": "Basic pronunciation rules",
                "description": "Key rules that govern how words are read aloud",
                "duration_minutes": 5,
            },
            {
                "name": "Syllable patterns",
                "description": "Break words into syllables and say them correctly",
                "duration_minutes": 5,
            },
            {
                "name": "Common sound combinations",
                "description": "Practise tricky letter combinations unique to the language",
                "duration_minutes": 5,
            },
            {
                "name": "Recognizing written words",
                "description": "Train your eye to read simple words fluently",
                "duration_minutes": 5,
            },
            {
                "name": "Your very first words",
                "description": "Speak ten essential everyday words with confidence",
                "duration_minutes": 4,
            },
            {
                "name": "Listening & repeating practice",
                "description": "Sharpen your ear by listening and mimicking native patterns",
                "duration_minutes": 5,
            },
        ],
    },

    "greetings": {
        "title": "Greetings & Introductions",
        "emoji": "👋",
        "description": "Say hello, introduce yourself and show proper respect",
        "duration_minutes": 60,
        "level": "beginner",
        "subtopics": [
            {
                "name": "Basic hello & goodbye",
                "description": "The very first words — how to open and close any conversation",
                "duration_minutes": 5,
            },
            {
                "name": "Morning, afternoon & evening greetings",
                "description": "Time-specific greetings used throughout the day",
                "duration_minutes": 6,
            },
            {
                "name": "Asking 'How are you?'",
                "description": "The most natural follow-up to any hello",
                "duration_minutes": 5,
            },
            {
                "name": "Responding to 'How are you?'",
                "description": "You need to know what to say when someone asks you back",
                "duration_minutes": 5,
            },
            {
                "name": "Greeting elders & showing respect",
                "description": "Culturally critical — prostration, kneeling and respect language",
                "duration_minutes": 7,
            },
            {
                "name": "Introducing yourself (your name)",
                "description": "Tell people who you are in the language",
                "duration_minutes": 5,
            },
            {
                "name": "Where are you from?",
                "description": "Talk about your hometown, state and origin",
                "duration_minutes": 5,
            },
            {
                "name": "Introducing other people",
                "description": "Bring someone else into a conversation correctly",
                "duration_minutes": 5,
            },
            {
                "name": "Phone greetings",
                "description": "How to open and close a phone call the Nigerian way",
                "duration_minutes": 5,
            },
            {
                "name": "Greetings at special occasions",
                "description": "Weddings, funerals, naming ceremonies and more",
                "duration_minutes": 7,
            },
        ],
    },

    "numbers": {
        "title": "Numbers & Counting",
        "emoji": "🔢",
        "description": "Count, calculate and use numbers in real situations",
        "duration_minutes": 60,
        "level": "beginner",
        "subtopics": [
            {
                "name": "Numbers 1–10",
                "description": "The core ten — the foundation of all counting",
                "duration_minutes": 5,
            },
            {
                "name": "Numbers 11–20",
                "description": "Extend your range with teen numbers",
                "duration_minutes": 5,
            },
            {
                "name": "Tens: 20, 30, 40…100",
                "description": "Build up to one hundred in multiples of ten",
                "duration_minutes": 6,
            },
            {
                "name": "Building larger numbers (21–99)",
                "description": "Combine tens and units to form any number",
                "duration_minutes": 6,
            },
            {
                "name": "Hundreds & thousands",
                "description": "Scale up to large numbers used in prices and quantities",
                "duration_minutes": 6,
            },
            {
                "name": "Ordinal numbers (first, second…)",
                "description": "Say first, second, third — essential for lists and ranking",
                "duration_minutes": 5,
            },
            {
                "name": "Counting money",
                "description": "Use numbers the way you actually need them — with Naira",
                "duration_minutes": 7,
            },
            {
                "name": "Telling your age",
                "description": "A common question — answer it confidently",
                "duration_minutes": 4,
            },
            {
                "name": "Phone numbers & addresses",
                "description": "Read and recite digits in a natural way",
                "duration_minutes": 5,
            },
            {
                "name": "Numbers in everyday conversation",
                "description": "Put it all together with real-life number phrases",
                "duration_minutes": 5,
            },
        ],
    },

    "colors_descriptions": {
        "title": "Colors & Descriptions",
        "emoji": "🎨",
        "description": "Describe the world around you — colors, sizes and appearances",
        "duration_minutes": 50,
        "level": "beginner",
        "subtopics": [
            {
                "name": "Basic colors",
                "description": "Red, blue, green, yellow and the core palette",
                "duration_minutes": 5,
            },
            {
                "name": "Light & dark shades",
                "description": "Dark blue vs. light blue — how shades are expressed",
                "duration_minutes": 5,
            },
            {
                "name": "Describing objects by color",
                "description": "Put color words into real sentences",
                "duration_minutes": 5,
            },
            {
                "name": "Common adjectives (big, small, hot, cold)",
                "description": "The most useful describing words for everyday life",
                "duration_minutes": 6,
            },
            {
                "name": "Describing people's appearance",
                "description": "Talk about height, build, hair and facial features",
                "duration_minutes": 6,
            },
            {
                "name": "Describing places & spaces",
                "description": "Is it big? Small? Near? Far? Clean? Noisy?",
                "duration_minutes": 6,
            },
            {
                "name": "Comparing things (bigger than…)",
                "description": "Make comparisons the way a native speaker would",
                "duration_minutes": 6,
            },
            {
                "name": "Colors in cultural meaning",
                "description": "Why white means mourning and red means royalty",
                "duration_minutes": 7,
            },
        ],
    },

    "family": {
        "title": "Family & Relationships",
        "emoji": "👨‍👩‍👧‍👦",
        "description": "Talk about your family tree and the people closest to you",
        "duration_minutes": 60,
        "level": "beginner",
        "subtopics": [
            {
                "name": "Immediate family (mother, father)",
                "description": "The closest family members and how to address them",
                "duration_minutes": 5,
            },
            {
                "name": "Siblings (brother, sister)",
                "description": "Older and younger siblings — the distinction matters",
                "duration_minutes": 5,
            },
            {
                "name": "Extended family (grandparents, aunts, uncles)",
                "description": "Nigerian family is big — learn who everyone is",
                "duration_minutes": 6,
            },
            {
                "name": "Cousins & distant relatives",
                "description": "The many layers of Nigerian extended family",
                "duration_minutes": 5,
            },
            {
                "name": "Titles of respect for elders",
                "description": "How to address older relatives with the right words",
                "duration_minutes": 6,
            },
            {
                "name": "Describing your family",
                "description": "Talk about family size, ages and where people live",
                "duration_minutes": 5,
            },
            {
                "name": "Talking about your family",
                "description": "Tell someone about your family in full sentences",
                "duration_minutes": 6,
            },
            {
                "name": "In-laws & marriage family",
                "description": "The vocabulary for a spouse's family — very commonly needed",
                "duration_minutes": 6,
            },
            {
                "name": "Neighbours & community",
                "description": "Beyond blood — how Nigerians talk about their community",
                "duration_minutes": 5,
            },
            {
                "name": "Terms of endearment & closeness",
                "description": "Affectionate words used with loved ones and friends",
                "duration_minutes": 5,
            },
        ],
    },

    "body": {
        "title": "The Human Body",
        "emoji": "🫱",
        "description": "Name body parts and talk about health and how you feel physically",
        "duration_minutes": 55,
        "level": "intermediate",
        "subtopics": [
            {
                "name": "The head & face",
                "description": "Eyes, ears, nose, mouth and everything on the head",
                "duration_minutes": 5,
            },
            {
                "name": "Upper body (chest, back, shoulders)",
                "description": "Torso and upper body vocabulary",
                "duration_minutes": 5,
            },
            {
                "name": "Arms & hands",
                "description": "Shoulders to fingertips — including hand gestures in culture",
                "duration_minutes": 5,
            },
            {
                "name": "Lower body & feet",
                "description": "Hips, legs, knees and feet",
                "duration_minutes": 5,
            },
            {
                "name": "Internal organs (basic vocabulary)",
                "description": "Heart, stomach, lungs — words you hear in health talks",
                "duration_minutes": 6,
            },
            {
                "name": "Describing pain or discomfort",
                "description": "'My head hurts', 'My stomach is aching' — vital phrases",
                "duration_minutes": 6,
            },
            {
                "name": "Visiting the clinic or doctor",
                "description": "A full mini-conversation at a health appointment",
                "duration_minutes": 7,
            },
            {
                "name": "Health & wellness vocabulary",
                "description": "Sickness, recovery, medicine and wellbeing words",
                "duration_minutes": 6,
            },
            {
                "name": "Body idioms & expressions",
                "description": "Colorful phrases involving body parts — very Nigerian",
                "duration_minutes": 6,
            },
        ],
    },

    "food": {
        "title": "Food & Eating",
        "emoji": "🍲",
        "description": "Talk about Nigerian food, cooking and sharing a meal",
        "duration_minutes": 60,
        "level": "beginner",
        "subtopics": [
            {
                "name": "Nigerian staple foods",
                "description": "Yam, garri, rice, fufu — the foundations of the diet",
                "duration_minutes": 5,
            },
            {
                "name": "Soups & stews",
                "description": "Egusi, ogbono, jollof — Nigerian soup culture is deep",
                "duration_minutes": 6,
            },
            {
                "name": "Fruits & vegetables",
                "description": "Common produce at the market and in the home",
                "duration_minutes": 5,
            },
            {
                "name": "Drinks & beverages",
                "description": "Water, palm wine, zobo, kunu and more",
                "duration_minutes": 5,
            },
            {
                "name": "Cooking verbs & methods",
                "description": "Fry, boil, pound, grind — how food is prepared",
                "duration_minutes": 5,
            },
            {
                "name": "Meal times & hunger phrases",
                "description": "Breakfast, lunch and dinner — plus 'I am hungry'",
                "duration_minutes": 5,
            },
            {
                "name": "Eating together & table culture",
                "description": "Sharing food communally — the customs and vocabulary",
                "duration_minutes": 6,
            },
            {
                "name": "Ordering food at a restaurant",
                "description": "A full mini-conversation at a restaurant or buka",
                "duration_minutes": 7,
            },
            {
                "name": "Food market vocabulary",
                "description": "Buy ingredients, ask for quantity and negotiate",
                "duration_minutes": 6,
            },
            {
                "name": "Food in culture & celebration",
                "description": "Festive foods and what they mean at occasions",
                "duration_minutes": 6,
            },
        ],
    },

    "home": {
        "title": "Home & Daily Life",
        "emoji": "🏠",
        "description": "Navigate home life, chores and the neighborhood",
        "duration_minutes": 55,
        "level": "beginner",
        "subtopics": [
            {
                "name": "Rooms in the house",
                "description": "Kitchen, bedroom, bathroom, parlour and the compound",
                "duration_minutes": 5,
            },
            {
                "name": "Furniture & household items",
                "description": "What is in each room — from the bed to the cooking pot",
                "duration_minutes": 5,
            },
            {
                "name": "Morning, afternoon & night routine",
                "description": "Describe a typical day from waking up to sleeping",
                "duration_minutes": 6,
            },
            {
                "name": "Household chores",
                "description": "Sweep, wash, cook, fetch water — daily duties",
                "duration_minutes": 5,
            },
            {
                "name": "Describing where things are",
                "description": "On the table, beside the door, behind the house",
                "duration_minutes": 6,
            },
            {
                "name": "Asking for things at home",
                "description": "'Please pass me…', 'Where is the…?' — daily requests",
                "duration_minutes": 5,
            },
            {
                "name": "The neighbourhood & surroundings",
                "description": "Road, market, school, church, mosque — what is nearby",
                "duration_minutes": 5,
            },
            {
                "name": "Common home activities",
                "description": "Watching TV, visiting relatives, resting — leisure at home",
                "duration_minutes": 5,
            },
            {
                "name": "Hosting guests (very Nigerian!)",
                "description": "Welcome someone in, offer food, say a proper goodbye",
                "duration_minutes": 7,
            },
        ],
    },

    "days_time": {
        "title": "Days, Time & Dates",
        "emoji": "📅",
        "description": "Talk about when things happen — days, times and seasons",
        "duration_minutes": 55,
        "level": "intermediate",
        "subtopics": [
            {
                "name": "Days of the week",
                "description": "Monday through Sunday — and how they are used culturally",
                "duration_minutes": 5,
            },
            {
                "name": "Months of the year",
                "description": "All twelve months and how dates are spoken",
                "duration_minutes": 5,
            },
            {
                "name": "Telling the time (hours)",
                "description": "One o'clock, two o'clock — exact hour expressions",
                "duration_minutes": 5,
            },
            {
                "name": "Telling the time (minutes & half)",
                "description": "Half past, quarter to — more precise time language",
                "duration_minutes": 6,
            },
            {
                "name": "Daily time markers (morning, noon, night)",
                "description": "Words for different parts of the day in conversation",
                "duration_minutes": 5,
            },
            {
                "name": "Past, present & future expressions",
                "description": "Yesterday, today, tomorrow, next week, last year",
                "duration_minutes": 6,
            },
            {
                "name": "Making plans & appointments",
                "description": "'Let us meet on Friday at 3 pm' — practical scheduling",
                "duration_minutes": 7,
            },
            {
                "name": "Seasons & weather",
                "description": "Dry season, rainy season and how weather is discussed",
                "duration_minutes": 6,
            },
            {
                "name": "Nigerian festivals & cultural calendar",
                "description": "New Yam, Sallah, Christmas — dates that matter culturally",
                "duration_minutes": 7,
            },
        ],
    },

    "animals_nature": {
        "title": "Animals & Nature",
        "emoji": "🦁",
        "description": "Name animals, talk about nature and understand their role in culture",
        "duration_minutes": 55,
        "level": "intermediate",
        "subtopics": [
            {
                "name": "Farm animals",
                "description": "Goat, cow, chicken, pig — animals in the compound",
                "duration_minutes": 5,
            },
            {
                "name": "Wild animals",
                "description": "Lion, elephant, monkey — animals of the bush and forest",
                "duration_minutes": 5,
            },
            {
                "name": "Birds",
                "description": "Common birds including those with cultural significance",
                "duration_minutes": 5,
            },
            {
                "name": "Insects & small creatures",
                "description": "Mosquito, ant, snake, lizard — very present in daily life",
                "duration_minutes": 5,
            },
            {
                "name": "Fish & water animals",
                "description": "Fish, crab, periwinkle — important for food and trade",
                "duration_minutes": 5,
            },
            {
                "name": "Animals in proverbs & culture",
                "description": "Why the tortoise, eagle and python appear in stories",
                "duration_minutes": 7,
            },
            {
                "name": "Trees, rivers & the natural world",
                "description": "Iroko, palm tree, rivers — the landscape of Nigeria",
                "duration_minutes": 6,
            },
            {
                "name": "Pets & domestic animals",
                "description": "Dogs, cats, birds kept at home — and how they are viewed",
                "duration_minutes": 5,
            },
            {
                "name": "Animal sounds & actions",
                "description": "How animals move and what sounds they make in the language",
                "duration_minutes": 5,
            },
        ],
    },

    "emotions": {
        "title": "Emotions & Personality",
        "emoji": "😊",
        "description": "Express how you feel and describe the people around you",
        "duration_minutes": 55,
        "level": "intermediate",
        "subtopics": [
            {
                "name": "Basic emotions (happy, sad, angry)",
                "description": "The core feelings every learner needs first",
                "duration_minutes": 5,
            },
            {
                "name": "Expressing how you feel",
                "description": "Full sentences: 'I am very happy', 'I am not feeling well'",
                "duration_minutes": 5,
            },
            {
                "name": "Asking 'how are you feeling?'",
                "description": "Show care and concern the way a Nigerian would",
                "duration_minutes": 5,
            },
            {
                "name": "Positive emotions & excitement",
                "description": "Joy, pride, excitement, gratitude — the good feelings",
                "duration_minutes": 5,
            },
            {
                "name": "Difficult emotions (grief, worry, fear)",
                "description": "Language for hard moments — culturally important",
                "duration_minutes": 6,
            },
            {
                "name": "Personality traits & character",
                "description": "Kind, stubborn, hardworking, funny — describing people",
                "duration_minutes": 6,
            },
            {
                "name": "Giving compliments",
                "description": "How to praise someone's looks, work or cooking",
                "duration_minutes": 6,
            },
            {
                "name": "Expressing comfort & support",
                "description": "What to say when someone is grieving or going through difficulty",
                "duration_minutes": 6,
            },
            {
                "name": "Emotional idioms & expressions",
                "description": "Rich, culturally-rooted phrases for strong feelings",
                "duration_minutes": 6,
            },
        ],
    },

    "market": {
        "title": "Market & Money",
        "emoji": "🛒",
        "description": "Buy, sell, bargain and handle money like a local",
        "duration_minutes": 60,
        "level": "intermediate",
        "subtopics": [
            {
                "name": "Greetings at the market",
                "description": "You always greet before you buy — learn the market opener",
                "duration_minutes": 5,
            },
            {
                "name": "Items for sale (food, clothing, goods)",
                "description": "Name what you want to buy across different stalls",
                "duration_minutes": 6,
            },
            {
                "name": "Asking for a price",
                "description": "'How much is this?' — the single most useful market phrase",
                "duration_minutes": 5,
            },
            {
                "name": "Bargaining & negotiating",
                "description": "Price is never final — learn to haggle with confidence",
                "duration_minutes": 7,
            },
            {
                "name": "Paying & giving change",
                "description": "Hand over money and understand what you get back",
                "duration_minutes": 5,
            },
            {
                "name": "Currency, notes & coins",
                "description": "Naira and kobo — how money is counted and spoken",
                "duration_minutes": 5,
            },
            {
                "name": "Complaints & problems with goods",
                "description": "'This is spoilt', 'This is not the right size' — assertive language",
                "duration_minutes": 6,
            },
            {
                "name": "Online & modern commerce vocabulary",
                "description": "Transfer, POS, delivery — how Nigerians shop today",
                "duration_minutes": 6,
            },
            {
                "name": "Traditional vs modern market culture",
                "description": "Understand what changes and what stays the same",
                "duration_minutes": 6,
            },
        ],
    },

    "travel": {
        "title": "Travel & Getting Around",
        "emoji": "✈️",
        "description": "Navigate cities, ask for directions and use transport confidently",
        "duration_minutes": 65,
        "level": "intermediate",
        "subtopics": [
            {
                "name": "Types of transportation",
                "description": "Danfo, okada, keke, BRT, tricycle — Nigeria's transport world",
                "duration_minutes": 6,
            },
            {
                "name": "Directions (left, right, straight, turn)",
                "description": "The core direction words you will use constantly",
                "duration_minutes": 5,
            },
            {
                "name": "Landmarks & asking for directions",
                "description": "Use shops, churches and bus stops to navigate",
                "duration_minutes": 6,
            },
            {
                "name": "At the motor park or bus station",
                "description": "Buy a ticket, find your bus, ask about departure",
                "duration_minutes": 6,
            },
            {
                "name": "At the airport",
                "description": "Check-in, customs, arrival — the airport in the language",
                "duration_minutes": 6,
            },
            {
                "name": "Places in a city or town",
                "description": "Hospital, school, market, church, mosque — key locations",
                "duration_minutes": 5,
            },
            {
                "name": "Distances & how far away",
                "description": "'Is it far?', 'It is just a short walk' — proximity language",
                "duration_minutes": 5,
            },
            {
                "name": "Arriving & departing phrases",
                "description": "What to say when you land, arrive or are leaving someone",
                "duration_minutes": 5,
            },
            {
                "name": "Emergency travel phrases",
                "description": "Lost, stolen, sick — phrases for when things go wrong",
                "duration_minutes": 7,
            },
            {
                "name": "Road culture in Nigeria",
                "description": "Traffic language, conductor calls and road-side phrases",
                "duration_minutes": 7,
            },
        ],
    },

    "verbs": {
        "title": "Verbs & Actions",
        "emoji": "🏃",
        "description": "Build fluency with the most important action words in the language",
        "duration_minutes": 65,
        "level": "advanced",
        "subtopics": [
            {
                "name": "Movement verbs (go, come, run, walk)",
                "description": "The verbs that describe getting from A to B",
                "duration_minutes": 5,
            },
            {
                "name": "Communication verbs (speak, say, ask, hear)",
                "description": "The verbs of talking, listening and understanding",
                "duration_minutes": 5,
            },
            {
                "name": "Thinking & feeling verbs",
                "description": "Know, think, want, love, hate, remember — inner life verbs",
                "duration_minutes": 5,
            },
            {
                "name": "Cooking & household verbs",
                "description": "Cook, clean, wash, pound, fetch — home action words",
                "duration_minutes": 5,
            },
            {
                "name": "Work & study verbs",
                "description": "Work, learn, read, write, teach, sell — productive action words",
                "duration_minutes": 5,
            },
            {
                "name": "Present tense — doing things now",
                "description": "How to say 'I am doing X right now' correctly",
                "duration_minutes": 7,
            },
            {
                "name": "Past tense — things that happened",
                "description": "How to say 'I did X yesterday' — past tense patterns",
                "duration_minutes": 7,
            },
            {
                "name": "Future tense — things to come",
                "description": "How to say 'I will do X' — expressing intentions and plans",
                "duration_minutes": 7,
            },
            {
                "name": "Negative sentences with verbs",
                "description": "How to say you are NOT doing something",
                "duration_minutes": 6,
            },
            {
                "name": "Questions using verbs",
                "description": "'Are you going?', 'Did she eat?' — turning verbs into questions",
                "duration_minutes": 6,
            },
        ],
    },

    "sentences": {
        "title": "Building Sentences",
        "emoji": "📝",
        "description": "Put all your vocabulary together into real, natural sentences",
        "duration_minutes": 70,
        "level": "advanced",
        "subtopics": [
            {
                "name": "Subject + verb (the basics)",
                "description": "'I eat', 'She goes', 'We see' — the simplest sentence form",
                "duration_minutes": 6,
            },
            {
                "name": "Adding an object",
                "description": "'I eat rice', 'She sees him' — completing the thought",
                "duration_minutes": 6,
            },
            {
                "name": "Describing with adjectives",
                "description": "'The big man eats' — placing adjectives in sentences",
                "duration_minutes": 6,
            },
            {
                "name": "Yes/no questions",
                "description": "How to form a question that needs a yes or no answer",
                "duration_minutes": 6,
            },
            {
                "name": "Question words (who, what, where, when, why, how)",
                "description": "The six question words — the most important grammar pattern",
                "duration_minutes": 7,
            },
            {
                "name": "Negative sentences",
                "description": "'I did not go', 'She does not want' — expressing negation",
                "duration_minutes": 6,
            },
            {
                "name": "Connecting ideas (and, but, because)",
                "description": "Link two thoughts together like a fluent speaker",
                "duration_minutes": 7,
            },
            {
                "name": "Sentence patterns for daily life",
                "description": "20 ready-to-use patterns for the most common situations",
                "duration_minutes": 7,
            },
            {
                "name": "Complex & compound sentences",
                "description": "Go beyond basic sentences to express nuanced ideas",
                "duration_minutes": 7,
            },
            {
                "name": "Telling a simple story",
                "description": "Use everything you know to narrate a short event",
                "duration_minutes": 8,
            },
        ],
    },

    "culture": {
        "title": "Culture, Proverbs & Identity",
        "emoji": "🌍",
        "description": "Connect with your heritage through language, wisdom and tradition",
        "duration_minutes": 75,
        "level": "advanced",
        "subtopics": [
            {
                "name": "Popular proverbs with meanings",
                "description": "The most famous proverbs and what they actually teach",
                "duration_minutes": 7,
            },
            {
                "name": "Using proverbs in conversation",
                "description": "When and how to drop a proverb naturally",
                "duration_minutes": 7,
            },
            {
                "name": "Festivals & cultural celebrations",
                "description": "New Yam, Ojude Oba, Durbar — events, their names and meaning",
                "duration_minutes": 7,
            },
            {
                "name": "Traditional music & dance vocabulary",
                "description": "Instruments, dances and songs — the language of celebration",
                "duration_minutes": 7,
            },
            {
                "name": "Religion & spiritual vocabulary",
                "description": "Christian, Muslim and traditional spiritual language",
                "duration_minutes": 7,
            },
            {
                "name": "Traditional titles & community roles",
                "description": "Obi, Oba, Emirs, Igwes — titles and what they mean",
                "duration_minutes": 7,
            },
            {
                "name": "The art of storytelling",
                "description": "How folktales begin, unfold and end in the language",
                "duration_minutes": 8,
            },
            {
                "name": "Food as cultural identity",
                "description": "What your people's food says about who you are",
                "duration_minutes": 6,
            },
            {
                "name": "Being Nigerian in the diaspora",
                "description": "Language for navigating dual identity and staying connected",
                "duration_minutes": 7,
            },
            {
                "name": "Pride vocabulary — talking your heritage",
                "description": "Words and phrases to speak about your culture with pride",
                "duration_minutes": 8,
            },
        ],
    },
}

VALID_LANGUAGES = ["Igbo", "Yoruba", "Hausa"]

# Total subtopics across all units — useful for progress calculation
TOTAL_SUBTOPICS = sum(len(u["subtopics"]) for u in TOPICS_METADATA.values())


def get_subtopic(unit_id: str, subtopic_index: int) -> dict | None:
    """
    Return a specific subtopic dict, or None if the unit or index is invalid.
    """
    unit = TOPICS_METADATA.get(unit_id)
    if not unit:
        return None
    subtopics = unit["subtopics"]
    if subtopic_index < 0 or subtopic_index >= len(subtopics):
        return None
    return subtopics[subtopic_index]


def get_next_subtopic(unit_id: str, subtopic_index: int) -> tuple[str, int] | tuple[None, None]:
    """
    Return (next_unit_id, next_subtopic_index) — either the next subtopic in
    the same unit, or the first subtopic of the next unit.
    Returns (None, None) when the learner has reached the very end.
    """
    unit = TOPICS_METADATA.get(unit_id)
    if not unit:
        return None, None

    next_index = subtopic_index + 1
    if next_index < len(unit["subtopics"]):
        return unit_id, next_index

    # Move to next unit
    unit_ids = list(TOPICS_METADATA.keys())
    current_pos = unit_ids.index(unit_id)
    if current_pos + 1 < len(unit_ids):
        return unit_ids[current_pos + 1], 0

    return None, None  # End of curriculum


class LessonsService:

    def get_lessons_list(
        self,
        language: str,
        level: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> LessonsListResponse:
        """Get a paginated list of available lesson units for a language."""

        if language not in VALID_LANGUAGES:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail=f"Invalid language. Must be one of: {', '.join(VALID_LANGUAGES)}"
            )

        all_units = []
        for unit_id, metadata in TOPICS_METADATA.items():
            if level and level.lower() != metadata["level"]:
                continue

            all_units.append(
                LessonTopicResponse(
                    id=unit_id,
                    title=metadata["title"],
                    emoji=metadata["emoji"],
                    description=metadata["description"],
                    duration_minutes=metadata["duration_minutes"],
                    level=metadata["level"],
                    subtopic_count=len(metadata["subtopics"]),
                    is_completed=False,
                )
            )

        total = len(all_units)
        paginated = all_units[offset : offset + limit]

        return LessonsListResponse(
            topics=paginated,
            total=total,
            language=language,
        )

    def get_lesson_detail(self, language: str, unit_id: str) -> LessonDetailResponse:
        """Get detailed content for a specific unit, including all subtopics."""

        if language not in VALID_LANGUAGES:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail=f"Invalid language. Must be one of: {', '.join(VALID_LANGUAGES)}"
            )

        if unit_id not in TOPICS_METADATA:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Unit not found")

        metadata = TOPICS_METADATA[unit_id]

        return LessonDetailResponse(
            id=unit_id,
            language=language,
            title=metadata["title"],
            emoji=metadata["emoji"],
            level=metadata["level"],
            subtopics=metadata["subtopics"],
            content={},   # Actual lesson content is AI-generated per subtopic at /lessons/
        )

    def get_subtopic_detail(
        self, language: str, unit_id: str, subtopic_index: int
    ) -> dict:
        """
        Return metadata for a single subtopic — used by the lesson and quiz
        routers before calling the AI so they know what to teach.
        """
        if language not in VALID_LANGUAGES:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail=f"Invalid language. Must be one of: {', '.join(VALID_LANGUAGES)}"
            )

        subtopic = get_subtopic(unit_id, subtopic_index)
        if subtopic is None:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"Subtopic index {subtopic_index} not found in unit '{unit_id}'"
            )

        unit = TOPICS_METADATA[unit_id]
        next_unit_id, next_index = get_next_subtopic(unit_id, subtopic_index)
        next_subtopic = get_subtopic(next_unit_id, next_index) if next_unit_id else None

        return {
            "unit_id": unit_id,
            "unit_title": unit["title"],
            "level": unit["level"],
            "subtopic_index": subtopic_index,
            "subtopic_name": subtopic["name"],
            "subtopic_description": subtopic["description"],
            "total_subtopics": len(unit["subtopics"]),
            "next_unit_id": next_unit_id,
            "next_subtopic_index": next_index,
            "next_subtopic_name": next_subtopic["name"] if next_subtopic else None,
        }


lessons_service = LessonsService()