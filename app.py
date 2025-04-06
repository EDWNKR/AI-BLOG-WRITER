import os
import streamlit as st
import time
from typing import List, Optional
from io import BytesIO
from PIL import Image

from utils import (
    generate_blog_content,
    generate_image,
    count_words,
    markdown_to_html,
    save_to_notion,
    save_to_wordpress,
    APIError
)

# Page config
st.set_page_config(
    page_title="AI Blog Writer",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        max-width: 1600px;
        margin: 0 auto;
    }
    .output-container {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 20px;
        background-color: #f9f9f9;
    }
    .success-message {
        color: green;
        font-weight: bold;
    }
    .error-message {
        color: red;
        font-weight: bold;
    }
    .stButton button {
        font-size: 18px;
        padding: 10px 15px;
    }
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-size: 110%;
    }
    .stHeader h1 {
        font-size: 40px;
    }
    .stSubheader h2 {
        font-size: 30px;
    }
    
    /* HTML Preview Styles */
    .html-preview {
        background-color: white;
        padding: 20px;
        border-radius: 5px;
        border: 1px solid #eee;
        color: #333;
        font-family: Arial, sans-serif;
    }
    .html-preview h1, .html-preview h2, .html-preview h3 {
        color: #2c3e50;
    }
    .html-preview p {
        line-height: 1.6;
    }
    .html-preview ul, .html-preview ol {
        margin-left: 20px;
    }
    .html-preview a {
        color: #3498db;
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("✍️ AI Blog Writer")
st.markdown("Generate SEO-optimized blog posts with AI. Create beautiful, structured content with images in seconds.")

# Function to validate OpenAI API key
def validate_openai_key() -> bool:
    # Try to get API key from Streamlit secrets first
    if 'api_keys' in st.secrets and 'openai' in st.secrets['api_keys']:
        api_key = st.secrets['api_keys']['openai']
        return api_key != "YOUR_OPENAI_API_KEY" and api_key.startswith("sk-")
    
    # Fall back to environment variable (for local development)
    api_key = os.getenv("OPENAI_API_KEY")
    return api_key is not None and api_key.startswith("sk-")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # Check if API key is set
    if not validate_openai_key():
        st.error("⚠️ OpenAI API key not found. Please add it to your Streamlit secrets or .env file.")
    
    # Blog post settings
    st.subheader("Blog Settings")
    title = st.text_input("Blog Title", placeholder="Enter a compelling title")
    
    # Keyword input
    keywords_input = st.text_area("SEO Keywords (one per line)", 
                                 placeholder="Enter keywords to target\nOne per line")
    
    # Process keywords
    keywords = []
    if keywords_input:
        keywords = [k.strip() for k in keywords_input.split("\n") if k.strip()]
    
    # Content settings
    st.subheader("Content Settings")
    tone_options = ["Professional", "Casual", "Humorous", "Educational", "Conversational"]
    tone = st.selectbox("Tone", tone_options)
    
    length_options = ["Short (500 words)", "Medium (1000 words)", "Long (1500+ words)"]
    length = st.selectbox("Length", length_options)
    
    # Map length options to approximate word counts
    length_to_words = {
        "Short (500 words)": 500,
        "Medium (1000 words)": 1000,
        "Long (1500+ words)": 1500
    }
    target_word_count = length_to_words[length]
    
    # Featured image
    st.subheader("Featured Image")
    generate_featured_image = st.checkbox("Generate featured image with DALL-E", value=True)
    custom_image_prompt = st.text_area(
        "Custom image prompt (optional)",
        placeholder="Leave empty to generate automatically based on title and keywords"
    )
    
    # Output format
    st.subheader("Output Format")
    output_format = st.radio("Format", ["Markdown", "HTML"])
    
    # Export options
    st.subheader("Export Options")
    export_options = st.multiselect(
        "Export to",
        ["Download", "Notion", "WordPress"]
    )

# Main content area
col1, col2 = st.columns([2, 3])

with col1:
    st.header("Generate Blog")
    
    if st.button("🚀 Generate Blog Post", use_container_width=True, disabled=not validate_openai_key()):
        if not title:
            st.error("Please enter a blog title")
        elif not keywords:
            st.error("Please enter at least one keyword")
        else:
            try:
                with st.spinner("Generating blog content..."):
                    # Generate the blog content
                    blog_content = generate_blog_content(
                        title=title,
                        keywords=keywords,
                        tone=tone.lower(),
                        length=length.split(" ")[0].lower(),
                        target_word_count=target_word_count
                    )
                    
                    # Count words
                    word_count = count_words(blog_content)
                    
                    # Store in session state
                    st.session_state.blog_content = blog_content
                    st.session_state.word_count = word_count
                    st.session_state.featured_image = None
                    
                    # Generate featured image if requested
                    if generate_featured_image:
                        with st.spinner("Generating featured image..."):
                            image_prompt = custom_image_prompt if custom_image_prompt else f"Create a professional featured image for a blog post titled '{title}' about {', '.join(keywords[:3])}"
                            
                            try:
                                image = generate_image(image_prompt)
                                if image:
                                    st.session_state.featured_image = image
                            except APIError as e:
                                st.error(f"Error generating image: {str(e)}")
                    
                    # Convert to HTML if needed
                    if output_format == "HTML":
                        html_content = markdown_to_html(blog_content)
                        # Wrap in div with class for styling
                        styled_html = f'<div class="html-preview">{html_content}</div>'
                        st.session_state.html_content = styled_html
                    
                    # Success message
                    st.success(f"Blog post generated successfully! ({word_count} words)")
                
            except APIError as e:
                st.error(f"Error: {str(e)}")
                
    # Display export options
    if 'blog_content' in st.session_state:
        st.subheader("Export Blog")
        
        # Download option
        if "Download" in export_options:
            if output_format == "Markdown":
                download_content = st.session_state.blog_content
                download_filename = f"{title.replace(' ', '_')}.md"
            else:
                # Strip the wrapper div for download
                raw_html = st.session_state.html_content.replace('<div class="html-preview">', '').replace('</div>', '')
                download_content = raw_html
                download_filename = f"{title.replace(' ', '_')}.html"
            
            st.download_button(
                label="📥 Download as File",
                data=download_content,
                file_name=download_filename,
                mime="text/plain",
                use_container_width=True
            )
        
        # Notion export
        if "Notion" in export_options:
            if st.button("📓 Save to Notion", use_container_width=True):
                try:
                    with st.spinner("Saving to Notion..."):
                        content = st.session_state.blog_content
                        image = st.session_state.featured_image if 'featured_image' in st.session_state else None
                        
                        url = save_to_notion(title, content, image)
                        if url:
                            st.success(f"Saved to Notion successfully!")
                            st.markdown(f"[View in Notion]({url})")
                except APIError as e:
                    st.error(f"Error saving to Notion: {str(e)}")
        
        # WordPress export
        if "WordPress" in export_options:
            if st.button("🌐 Save to WordPress", use_container_width=True):
                try:
                    with st.spinner("Saving to WordPress..."):
                        if output_format == "HTML":
                            # Strip the wrapper div for WordPress
                            raw_html = st.session_state.html_content.replace('<div class="html-preview">', '').replace('</div>', '')
                            content = raw_html
                        else:
                            content = markdown_to_html(st.session_state.blog_content)
                        
                        image = st.session_state.featured_image if 'featured_image' in st.session_state else None
                        
                        url = save_to_wordpress(title, content, image)
                        if url:
                            st.success(f"Saved to WordPress as draft!")
                            st.markdown(f"[View draft post]({url})")
                except APIError as e:
                    st.error(f"Error saving to WordPress: {str(e)}")

with col2:
    st.header("Preview")
    
    # Display content if available
    if 'blog_content' in st.session_state:
        # Word count indicator
        word_count = st.session_state.word_count
        st.markdown(f"**Word count:** {word_count}")
        
        # Featured image if available
        if 'featured_image' in st.session_state and st.session_state.featured_image:
            st.image(st.session_state.featured_image, caption="Featured Image", use_container_width=True)
        
        # Content display
        st.subheader("Content Preview")
        if output_format == "Markdown":
            st.markdown(st.session_state.blog_content)
        else:
            st.components.v1.html(st.session_state.html_content, height=800, scrolling=True)
    else:
        st.info("Generated content will appear here. Fill in the details and click 'Generate Blog Post' to get started.")

# Footer
st.markdown("---")
st.markdown("AI Blog Writer © 2023 | Powered by OpenAI GPT-4 and DALL-E") 