import streamlit as st
import re
import string

"""
TruthPulse Prototype Application

This Streamlit app demonstrates a proof‑of‑concept for TruthPulse, an
AI‑powered tool designed to help users navigate today’s information
landscape.  The prototype supports four core features:

  1. Real‑time fact‑checking: rates the credibility of user‑submitted
     statements and provides brief explanations with citations to
     authoritative sources.
  2. Bias and sentiment analysis: identifies emotionally charged
     language in the statement, reports overall sentiment, and
     generates a neutral rewrite.
  3. Economic clarity: explains common economic terms and concepts in
     plain language when they appear in the input.
  4. Mental health support: detects anxiety‑related keywords and
     supplies a short, supportive message that includes a simple
     breathing exercise.

Although the app does not perform live web searches, it draws upon
up‑to‑date facts gathered from recent official publications and
research.  Citations are provided in the explanation section to
encourage transparency and enable further reading.  The user interface
is intentionally minimalist to keep the focus on the results.
"""

# Predefined fact patterns and corresponding responses.  Each entry
# contains a list of keywords to match, a credibility rating, a
# concise explanation, and a list of citation strings.  The
# citations refer to sources embedded in the assistant's final
# explanation and will be displayed alongside the explanation.
FACT_PATTERNS = [
    {
        "keywords": [
            "recession", "economy is in recession", "jobs vanishing",
            "jobs are vanishing", "vanishing jobs"
        ],
        "credibility": "Moderately credible",
        "explanation": (
            "Recent economic data show a slowdown in certain industries, but the \n"
            "United States is not officially in a recession. The unemployment \n"
            "rate was 4.1% in June 2025—within the 4.0–4.2% range seen since May 2024—\n"
            "suggesting that the labour market remains broadly stable【241353771908563†L143-L149】. \n"
            "Economists typically define a recession as two consecutive quarters of \n"
            "declining GDP or, more formally, a significant decline in economic \n"
            "activity across the economy lasting more than a few months【779321479305291†L245-L267】. \n"
            "So while some sectors are cutting jobs, most analysts do not yet \n"
            "characterise the current environment as a recession."
        ),
        "sources": [
            "U.S. Bureau of Labor Statistics: unemployment rate data【241353771908563†L143-L149】",
            "International Monetary Fund: definition of recession【779321479305291†L245-L267】"
        ],
    },
    {
        "keywords": [
            "vaccines cause autism", "vaccine causes autism", "vaccines and autism",
            "vaccine linked to autism"
        ],
        "credibility": "False",
        "explanation": (
            "Multiple large studies have found no association between vaccines and \n"
            "autism.  A small 1998 study that suggested a link between the MMR \n"
            "vaccine and autism was later retracted, and the lead author's \n"
            "conclusions were widely discredited. Subsequent research has shown \n"
            "no causal relationship【910319921190478†L98-L107】.  Claims that vaccines \n"
            "cause autism are therefore unsupported by evidence."
        ),
        "sources": [
            "Johns Hopkins Bloomberg School of Public Health: evidence on vaccines and autism【910319921190478†L98-L107】"
        ],
    },
    {
        "keywords": [
            "climate change is natural", "climate change is not caused by humans",
            "climate change hoax", "global warming is natural"
        ],
        "credibility": "False",
        "explanation": (
            "Scientists agree that the recent warming trend cannot be explained \n"
            "by natural factors alone. Human activities—primarily the burning of \n"
            "fossil fuels—have released large amounts of greenhouse gases into \n"
            "the atmosphere, causing the climate to warm. The U.S. EPA notes that \n"
            "the long‑term warming trend observed since the Industrial Revolution \n"
            "is extremely likely (>95%) to be due to human activities【43950627913764†L80-L114】.\n"
        ),
        "sources": [
            "U.S. Environmental Protection Agency: causes of climate change【43950627913764†L80-L114】"
        ],
    },
]

# Emotional words that may indicate bias or sensationalism.  For each
# key, provide a neutral alternative.  This list is not exhaustive but
# covers common charged terms found in political or economic rhetoric.
EMOTIONAL_WORDS = {
    "vanishing": "declining",
    "vanish": "decline",
    "vanishing jobs": "job reductions",
    "plummeting": "decreasing",
    "plunge": "drop",
    "soaring": "increasing",
    "skyrocketing": "rising",
    "exploding": "rising",
    "crisis": "challenge",
    "disaster": "difficult situation",
    "booming": "growing",
    "catastrophic": "severe",
    "collapse": "sharp decline",
    "miracle": "unexpected increase",
}

# Simple lexicons for sentiment detection.  Positive and negative
# keywords are used to compute a rudimentary sentiment score.
POSITIVE_WORDS = {
    "growth", "increase", "increasing", "stable", "improve", "improvement", "progress",
    "low", "benefit", "opportunity", "strength"
}
NEGATIVE_WORDS = {
    "vanish", "vanishing", "loss", "losses", "decline", "declining", "fall", "drop",
    "high", "collapse", "recession", "crisis", "anxiety", "stress", "fear", "panic",
    "decrease", "decreasing"
}

# Economic terms and their plain‑language explanations.  Each term is
# matched using a simple substring search (case‑insensitive).  The
# definitions are kept concise and cite authoritative sources.
ECONOMIC_TERMS = {
    "recession": (
        "A recession refers to a significant decline in economic activity \n"
        "spread across the economy and lasting more than a few months. Many \n"
        "commentators use a practical rule of thumb of two consecutive \n"
        "quarters of negative GDP growth, but formal definitions consider \n"
        "broader indicators such as employment, income and industrial \n"
        "production【779321479305291†L245-L267】."
    ),
    "inflation": (
        "Inflation is the rate of increase in prices over time. It measures \n"
        "how much more expensive a basket of goods and services has become, \n"
        "often expressed on an annual basis【675228743970689†L230-L240】.  Central banks aim \n"
        "for low and stable inflation to encourage economic growth while \n"
        "protecting purchasing power【675228743970689†L320-L328】."
    ),
    "gdp": (
        "Gross domestic product (GDP) is the monetary value of all final \n"
        "goods and services produced within a country in a given period. \n"
        "Changes in GDP, reported quarterly and annually, are a key gauge \n"
        "of economic growth【227927830193326†L67-L78】."
    ),
    "unemployment": (
        "The unemployment rate measures the number of people without a job \n"
        "who are actively seeking work as a share of the labour force (the \n"
        "employed plus the unemployed)【393517848734167†L680-L739】.  A low unemployment \n"
        "rate signals a strong labour market, while a high rate suggests \n"
        "slack."
    ),
}

# Keywords associated with anxiety or stress.  If any of these words
# appear in the user input, the mental health support agent will
# respond.
ANXIETY_KEYWORDS = {
    "anxious", "anxiety", "worried", "worry", "panic", "afraid", "scared",
    "stress", "stressed", "nervous", "overwhelmed"
}

def fact_check(text: str):
    """Return a credibility rating, explanation, and sources for a given text.

    The function scans the input for known patterns.  If a pattern
    matches, it returns the associated response; otherwise it reports
    that it cannot provide an automated fact check.
    """
    lowered = text.lower()
    for pattern in FACT_PATTERNS:
        for keyword in pattern["keywords"]:
            if keyword in lowered:
                return pattern["credibility"], pattern["explanation"], pattern["sources"]
    # Default response when no pattern matches.
    default_explanation = (
        "Unable to determine credibility automatically. The statement may \n"
        "contain nuanced or ambiguous claims that require context‑specific \n"
        "research. Please consult multiple trusted sources for verification."
    )
    return "Not enough information", default_explanation, []


def analyze_bias_and_sentiment(text: str):
    """Identify emotionally charged words, compute sentiment, and rewrite neutrally."""
    # Tokenise text by splitting on whitespace and stripping punctuation.
    tokens = []
    for raw_token in text.split():
        # Remove punctuation from beginning/end of the word
        token = raw_token.strip(string.punctuation).lower()
        if token:
            tokens.append(token)

    # Collect emotional words found in the input
    found_bias = [word for word in tokens if word in EMOTIONAL_WORDS]

    # Create neutral rewrite by replacing emotional words with their neutral counterparts
    rewrite_tokens = []
    for raw_token in text.split():
        # Separate punctuation from word to preserve original structure
        stripped = raw_token.strip(string.punctuation)
        lower_stripped = stripped.lower()
        replacement = EMOTIONAL_WORDS.get(lower_stripped)
        if replacement:
            # Preserve original capitalization
            if stripped.istitle():
                replacement = replacement.capitalize()
            # Append punctuation that trailed the original token
            prefix = raw_token[: raw_token.find(stripped)]
            suffix = raw_token[raw_token.find(stripped) + len(stripped) :]
            rewrite_tokens.append(f"{prefix}{replacement}{suffix}")
        else:
            rewrite_tokens.append(raw_token)

    neutral_rewrite = " ".join(rewrite_tokens)

    # Compute a simple sentiment score: positive words increment, negative words decrement
    sentiment_score = 0
    for token in tokens:
        if token in POSITIVE_WORDS:
            sentiment_score += 1
        elif token in NEGATIVE_WORDS:
            sentiment_score -= 1
    if sentiment_score > 0:
        sentiment = "Positive"
    elif sentiment_score < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return found_bias, sentiment, neutral_rewrite


def economic_clarity(text: str):
    """Return explanations of economic terms found in the text."""
    lowered = text.lower()
    explanations = []
    for term, definition in ECONOMIC_TERMS.items():
        if term in lowered:
            explanations.append(f"**{term.capitalize()}**: {definition}")
    return explanations


def mental_health_support(text: str):
    """Detect anxiety‑related keywords and return a supportive message."""
    lowered = text.lower()
    if any(keyword in lowered for keyword in ANXIETY_KEYWORDS):
        support_message = (
            "It’s natural to feel anxious when reading alarming headlines. \n"
            "Try a simple box‑breathing exercise to ground yourself: sit or \n"
            "stand comfortably and breathe in slowly while counting to four, \n"
            "hold your breath for four seconds, exhale for four seconds, and \n"
            "wait for another four seconds before breathing in again【167705470332884†L162-L170】. \n"
            "Repeat this cycle a few times. If persistent worry interferes with \n"
            "daily life, consider reaching out to a mental health professional or \n"
            "trusted friend for support."
        )
        return support_message
    return None


def main():
    st.set_page_config(page_title="TruthPulse Prototype", layout="centered")
    st.title("TruthPulse Prototype")
    st.write(
        "Enter a news headline, social media post, or economic statement below. "
        "TruthPulse will evaluate its credibility, highlight biased language, "
        "clarify economic terms, and offer supportive advice if anxiety is "
        "detected."
    )

    user_input = st.text_area("Your input", height=150)
    if st.button("Analyze"):
        if not user_input.strip():
            st.warning("Please enter some text to analyze.")
        else:
            # Fact checking
            credibility, explanation, sources = fact_check(user_input)
            st.subheader("Fact‑Check Result")
            st.write(f"**Credibility:** {credibility}")
            st.write(explanation)
            if sources:
                st.write("**Sources:**")
                for src in sources:
                    st.write(f"- {src}")

            # Bias and sentiment
            st.subheader("Bias Detection & Neutral Rewrite")
            bias_words, sentiment, rewrite = analyze_bias_and_sentiment(user_input)
            if bias_words:
                st.write(
                    f"The statement uses emotionally charged language: {', '.join(bias_words)}."
                )
            else:
                st.write("No obvious emotionally charged language detected.")
            st.write(f"**Overall Sentiment:** {sentiment}")
            st.write(f"**Neutral Rewrite:** {rewrite}")

            # Economic clarity
            st.subheader("Economic Clarity Explanation")
            econ_explanations = economic_clarity(user_input)
            if econ_explanations:
                for exp in econ_explanations:
                    st.write(exp)
            else:
                st.write("No specific economic terms detected.")

            # Mental health support
            support = mental_health_support(user_input)
            st.subheader("Mental Health Support")
            if support:
                st.write(support)
            else:
                st.write("No mental health concerns detected in your input.")


if __name__ == "__main__":
    main()