import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")

# Load API key from Streamlit secrets
google_gemini_api_key = st.secrets["api_keys"]["google_gemini_api_key"]

# Configure Google Gemini API
genai.configure(api_key=google_gemini_api_key)

# Define functions
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("v=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([line["text"] for line in transcript_text])
        return transcript
    except Exception as e:
        st.error(f"Error extracting transcript for {youtube_video_url}: {e}")
        return None

def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

def combine_transcripts(transcript_list):
    combined_transcript = ""
    for url in transcript_list:
        extracted_transcript = extract_transcript_details(url)
        if extracted_transcript:
            combined_transcript += "\n\n" + extracted_transcript
    return combined_transcript

# UI Layout
st.title("YouTube Script Generator")
st.image("https://via.placeholder.com/800x200.png?text=YouTube+Script+Generator", use_column_width=True)
st.markdown(
    """
    Welcome to the YouTube Script Generator! This tool helps you generate cohesive scripts from multiple YouTube video transcripts.
    Simply enter the YouTube video links separated by commas, and let the app do the rest.
    """
)

user_input_links = st.text_input("Enter YouTube Video Links separated by commas:")
if user_input_links:
    st.subheader("Processing Videos")
    video_links = user_input_links.split(",")
    with st.spinner("Fetching transcripts..."):
        combined_transcript = combine_transcripts(video_links)

    if combined_transcript:
        prompt = """You are a YouTube Script Generator. You will be taking the transcript text
        and writing a cohesive script based on the following content: """
        with st.spinner("Generating script..."):
            summary = generate_gemini_content(combined_transcript, prompt)
        st.markdown("## Generated Script:")
        st.write(summary)
        st.download_button("Download Script", summary, file_name="script.txt")
    else:
        st.warning("No transcripts were found for the provided links.")
else:
    st.info("Please enter YouTube video links to generate a script.")
