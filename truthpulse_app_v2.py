
import streamlit as st

# New content for the updated TruthPulse app
FACT_PATTERNS = [
    {
        "keywords": ["recession", "job losses"],
        "credibility": "Moderately credible",
        "explanation": "The U.S. economy has shown some slowing, especially in tech and manufacturing. However, unemployment remains historically low (4.1% in June 2025).",
        "sources": ["https://www.bls.gov", "https://www.factcheck.org"]
    },
    {
        "keywords": ["nuclear submarines", "Trump", "Russia"],
        "credibility": "Unclear",
        "explanation": "This is a complex geopolitical action. The credibility depends on whether this was confirmed by reliable news agencies or official statements.",
        "sources": ["https://www.reuters.com", "https://www.nytimes.com", "https://factcheck.org"]
    }
]

EMOTIONAL_WORDS = ["terrifying", "disaster", "vanishing", "catastrophic", "crisis", "provocative", "escalation", "unprecedented", "alarming", "escalate"]
MENTAL_HEALTH_KEYWORDS = ["anxious", "worried", "scared", "depressed", "hopeless", "nervous", "overwhelmed", "nuclear war", "military strike", "invasion", "crisis", "retaliation"]

ECONOMIC_TERMS = {
    "GDP": "Gross Domestic Product, the total market value of goods and services produced in a country.",
    "inflation": "The rate at which prices for goods and services rise, decreasing purchasing power.",
    "unemployment": "The percentage of the labor force that is jobless and actively seeking employment.",
    "recession": "A significant decline in economic activity lasting more than a few months, typically defined by two consecutive quarters of GDP decline.",
    "military spending": "Money that a government allocates to defense and armed forces, often included in national budgets.",
    "defense budget": "A financial plan outlining government expenditure on national defense and military operations."
}

# Minimal app code structure
st.title("TruthPulse")
st.write("Paste a news headline or statement below to analyze it:")

user_input = st.text_area("Input your text here:")

if user_input:
    # Fact-check
    credibility = "Not enough information"
    explanation = ""
    sources = []
    for pattern in FACT_PATTERNS:
        if all(kw.lower() in user_input.lower() for kw in pattern["keywords"]):
            credibility = pattern["credibility"]
            explanation = pattern["explanation"]
            sources = pattern["sources"]
            break

    st.subheader("Fact‑Check Result")
    st.markdown(f"**Credibility:** {credibility}")
    if explanation:
        st.markdown(f"**Explanation:** {explanation}")
        st.markdown("**Sources:**")
        for src in sources:
            st.markdown(f"- [{src}]({src})")
    else:
        st.markdown("Unable to determine credibility automatically. Please consult multiple trusted sources.")

    # Bias Detection
    bias_words_found = [word for word in EMOTIONAL_WORDS if word.lower() in user_input.lower()]
    sentiment = "Neutral" if not bias_words_found else "Emotionally Charged"
    st.subheader("Bias Detection & Neutral Rewrite")
    st.markdown(f"**Overall Sentiment:** {sentiment}")
    st.markdown(f"**Bias Words Found:** {', '.join(bias_words_found) if bias_words_found else 'None'}")
    st.markdown(f"**Neutral Rewrite:** {user_input}")

    # Economic Clarity
    st.subheader("Economic Clarity Explanation")
    found_terms = [term for term in ECONOMIC_TERMS if term.lower() in user_input.lower()]
    if found_terms:
        for term in found_terms:
            st.markdown(f"- **{term.title()}:** {ECONOMIC_TERMS[term]}")
    else:
        st.markdown("No specific economic terms detected.")

    # Mental Health Support
    st.subheader("Mental Health Support")
    if any(keyword in user_input.lower() for keyword in MENTAL_HEALTH_KEYWORDS):
        st.markdown("You may be experiencing anxiety or concern related to this topic. Here's a grounding tip:")
        st.markdown("> Try box breathing: Inhale for 4 seconds, hold for 4, exhale for 4, hold for 4 — and repeat.")
    else:
        st.markdown("No mental health concerns detected in your input.")
