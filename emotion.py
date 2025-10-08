import streamlit as st
from datetime import datetime
from textblob import TextBlob
import requests

# Configuration
OLLAMA_BASE_URL = "http://localhost:11434"


def check_ollama():
    """Check if Ollama is running"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def chat_with_llama(message):
    """Simple chat with Llama3"""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": "james",
                "prompt": message,
                "stream": False
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get('response', 'No response received')
        return "Error: Unable to get response"
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"


def analyze_text(text):
    """Advanced sentiment + emotion analysis using LLaMA"""
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        prompt = f"""
        You are an empathetic AI mental health assistant. 
        Analyze the user's emotional tone and psychological state based on the following input.

        ---
        🧠 User Input:
        "{text}"
        ---
        📊 Sentiment Polarity (from TextBlob): {polarity}

        Please:
        1. Interpret the sentiment polarity (from -1 = very negative to +1 = very positive).
        2. Identify emotional categories (e.g., stress, anxiety, sadness, calmness, happiness, hopefulness, anger).
        3. Explain the likely mental state of the user.
        4. Provide 1–2 short, compassionate suggestions or coping strategies (e.g., mindfulness, journaling, taking a break, talking to someone).
        5. Keep your response concise and human-like.
        """

        response = chat_with_llama(prompt)
        return polarity, response  # Return both polarity (number) and AI analysis (text)

    except Exception as e:
        return 0.0, f"Error analyzing text: {str(e)}"


def calculate_score(responses):
    """Calculate simple score"""
    return sum(responses.values())


def get_basic_recommendations(score):
    """Generate basic recommendations"""
    if score <= 15:
        level = "Minimal to Mild"
        advice = "Continue with healthy habits. Practice self-care regularly."
    elif score <= 30:
        level = "Moderate"
        advice = "Consider speaking with a mental health professional. Practice stress management techniques."
    else:
        level = "Significant"
        advice = "Strongly recommend consulting a mental health professional soon."

    return f"""**Assessment Level: {level}** (Score: {score}/45)

**Recommendations:**
{advice}

**Self-Care Tips:**
• Sleep 7-9 hours nightly
• Exercise 30 minutes daily
• Practice deep breathing
• Connect with supportive people
• Keep a mood journal

**Crisis Resources:**
• 988 - Suicide Prevention Lifeline
• 741741 - Crisis Text Line (text HOME)
• 1-800-662-4357 - SAMHSA Helpline

*This is not a medical diagnosis. Consult a qualified professional.*"""


def main():
    st.set_page_config(page_title="Mental Health Tool", page_icon="🧠", layout="wide")

    st.title("🧠 Mental Health Support Tool")

    # Sidebar
    st.sidebar.title("Navigation")

    ollama_connected = check_ollama()
    if ollama_connected:
        st.sidebar.success("✅ Ollama Connected")
    else:
        st.sidebar.warning("⚠️ Ollama Offline")

    page = st.sidebar.radio("Select Page", ["Assessment", "Results", "Chat", "Resources"])

    # ===== ASSESSMENT PAGE =====
    if page == "Assessment":
        st.header("Mental Health Assessment")
        st.write("Rate how you've felt over the past 2 weeks:")

        questions = {
            'q1': 'Little interest in activities',
            'q2': 'Feeling down or hopeless',
            'q3': 'Sleep problems',
            'q4': 'Low energy',
            'q5': 'Appetite changes',
            'q6': 'Feeling bad about yourself',
            'q7': 'Trouble concentrating',
            'q8': 'Moving slowly or restless',
            'q9': 'Thoughts of self-harm',
            'q10': 'Feeling nervous',
            'q11': 'Unable to stop worrying',
            'q12': 'Feeling afraid',
            'q13': 'Feeling overwhelmed',
            'q14': 'Feeling stressed',
            'q15': 'Unable to relax'
        }

        options = ["Not at all", "Several days", "More than half", "Nearly every day"]
        responses = {}

        for qid, question in questions.items():
            responses[qid] = st.radio(question, options, key=qid, horizontal=True)

        st.subheader("How are you feeling?")
        text_input = st.text_area("Describe your feelings:", height=100)

        if st.button("Analyze", type="primary"):
            if text_input.strip():
                with st.spinner("Analyzing your responses..."):
                    numeric = {k: options.index(v) for k, v in responses.items()}
                    score = calculate_score(numeric)

                    # Get both polarity (number) and AI analysis (text)
                    polarity, ai_analysis = analyze_text(text_input)

                    recommendations = get_basic_recommendations(score)

                    st.session_state.results = {
                        'score': score,
                        'sentiment_score': polarity,  # Store number for comparison
                        'ai_analysis': ai_analysis,  # Store AI text separately
                        'recommendations': recommendations,
                        'timestamp': datetime.now()
                    }
                st.success("✅ Analysis complete! Check Results page.")
            else:
                st.warning("Please enter some text about your feelings.")

    # ===== RESULTS PAGE =====
    elif page == "Results":
        st.header("Your Results")

        if 'results' not in st.session_state:
            st.info("Complete the assessment first.")
        else:
            res = st.session_state.results
            st.write(f"**Completed:** {res['timestamp'].strftime('%Y-%m-%d %H:%M')}")
            st.write(f"**Total Score:** {res['score']}/45")

            st.write("---")

            # Display sentiment score with color
            sentiment = res['sentiment_score']
            sentiment_color = "green" if sentiment > 0 else "red" if sentiment < -0.1 else "orange"
            st.markdown(
                f"**Sentiment Score:** <span style='color:{sentiment_color}'>{sentiment:.2f}</span> (Range: -1 to +1)",
                unsafe_allow_html=True)

            # Display AI emotional analysis
            st.subheader("🤖 AI Emotional Analysis")
            st.write(res['ai_analysis'])

            st.write("---")

            # Display recommendations
            st.subheader("📋 Recommendations")
            st.write(res['recommendations'])

            if res['score'] > 30:
                st.error("⚠️ Significant symptoms detected. Please consult a professional.")

    # ===== CHAT PAGE =====
    elif page == "Chat":
        st.header("💬 Chat with AI Assistant")

        if not ollama_connected:
            st.error("Ollama is not running. Start it with: `ollama serve`")
            st.info("Then run: `ollama pull james` (or your model name)")
            st.stop()

        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []

        # Display chat history
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Chat input
        if user_input := st.chat_input("Type your message..."):
            # Add user message
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    ai_response = chat_with_llama(user_input)
                    st.write(ai_response)
                    st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})

        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.chat_messages = []
            st.rerun()

    # ===== RESOURCES PAGE =====
    else:
        st.header("Resources")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🆘 Crisis Support")
            st.write("**Emergency:** 911")
            st.write("**Suicide Prevention:** 988")
            st.write("**Crisis Text:** HOME to 741741")
            st.write("**SAMHSA:** 1-800-662-4357")

            st.subheader("🧘 Self-Care")
            st.write("• Deep breathing")
            st.write("• Regular exercise")
            st.write("• Adequate sleep")
            st.write("• Social connections")
            st.write("• Journaling")

        with col2:
            st.subheader("👨‍⚕️ When to Seek Help")
            st.write("• Symptoms persist 2+ weeks")
            st.write("• Daily functioning impaired")
            st.write("• Thoughts of self-harm")
            st.write("• Substance use concerns")

            st.subheader("📚 Resources")
            st.write("• NIMH.nih.gov")
            st.write("• MentalHealthAmerica.org")
            st.write("• ADAA.org")
            st.write("• PsychologyToday.com")

    # Footer
    st.markdown("---")
    st.caption("⚠️ Educational tool only. Not medical advice. Consult professionals.")


if __name__ == "__main__":
    main()


