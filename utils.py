import os
import base64
import time
import json
import requests
import re
import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
from retry import retry
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# Load environment variables (for local development)
load_dotenv()

# Get OpenAI API key from Streamlit secrets or environment variable
def get_openai_api_key():
    # Try to get from Streamlit secrets first
    if 'api_keys' in st.secrets and 'openai' in st.secrets['api_keys']:
        api_key = st.secrets['api_keys']['openai']
        if api_key != "YOUR_OPENAI_API_KEY":
            return api_key
    
    # Fall back to environment variable
    return os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=get_openai_api_key())

class APIError(Exception):
    """Custom exception for API errors"""
    pass

def process_internal_links(content: str) -> str:
    """
    Process internal links in the content to remove the 'INTERNAL_LINK:' prefix
    
    Args:
        content: Blog content with internal links in format [INTERNAL_LINK: topic]
        
    Returns:
        str: Content with cleaned internal links in format [topic]
    """
    # Regular expression to find [INTERNAL_LINK: topic] and replace with [topic]
    return re.sub(r'\[INTERNAL_LINK:\s*(.*?)\]', r'[\1]', content)

@retry(APIError, tries=3, delay=2, backoff=2)
def generate_blog_content(
    title: str,
    keywords: List[str],
    tone: str,
    length: str,
    target_word_count: int
) -> str:
    """
    Generate blog content using GPT-4
    
    Args:
        title: Blog post title
        keywords: SEO keywords to target
        tone: Tone of the blog (professional, casual, etc.)
        length: Short, medium, or long
        target_word_count: Approximate word count to aim for
        
    Returns:
        str: Markdown formatted blog content
    """
    try:
        prompt = f"""Write a comprehensive, engaging, and well-structured blog post titled "{title}".

The blog post should:
- Be written in a {tone} tone
- Target these SEO keywords: {', '.join(keywords)}
- Include appropriate H2 and H3 headers
- Use bullet points and numbered lists where appropriate
- Include placeholders for internal links [INTERNAL_LINK: related topic]
- Be approximately {target_word_count} words ({length} length)
- Include an introduction and conclusion

Format the output as Markdown.
"""

        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": "You are an expert blog writer skilled in SEO and creating engaging, well-structured content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        # Get generated content and process internal links
        content = response.choices[0].message.content
        processed_content = process_internal_links(content)
        
        return processed_content
    except Exception as e:
        raise APIError(f"Error generating blog content: {str(e)}")

@retry(APIError, tries=3, delay=2, backoff=2)
def generate_image(prompt: str) -> Optional[Image.Image]:
    """
    Generate image using DALL-E
    
    Args:
        prompt: Image description
        
    Returns:
        PIL.Image: Generated image
    """
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        
        if image_response.status_code == 200:
            return Image.open(BytesIO(image_response.content))
        else:
            raise APIError(f"Failed to download image: {image_response.status_code}")
    except Exception as e:
        raise APIError(f"Error generating image: {str(e)}")

def count_words(text: str) -> int:
    """Count the number of words in a text"""
    return len(text.split())

def markdown_to_html(markdown_text: str) -> str:
    """Convert markdown to HTML"""
    try:
        import markdown
        return markdown.markdown(markdown_text)
    except Exception as e:
        raise APIError(f"Error converting markdown to HTML: {str(e)}")

def get_notion_credentials():
    """Get Notion credentials from secrets or environment variables"""
    api_key = None
    database_id = None
    
    # Try Streamlit secrets first
    if 'notion' in st.secrets:
        api_key = st.secrets['notion'].get('api_key')
        database_id = st.secrets['notion'].get('database_id')
        
        # Don't use placeholder values
        if api_key == "YOUR_NOTION_API_KEY":
            api_key = None
        if database_id == "YOUR_NOTION_DATABASE_ID":
            database_id = None
    
    # Fall back to environment variables
    if not api_key:
        api_key = os.getenv("NOTION_API_KEY")
    if not database_id:
        database_id = os.getenv("NOTION_DATABASE_ID")
        
    return api_key, database_id

def get_wordpress_credentials():
    """Get WordPress credentials from secrets or environment variables"""
    wp_url = None
    wp_username = None
    wp_password = None
    
    # Try Streamlit secrets first
    if 'wordpress' in st.secrets:
        wp_url = st.secrets['wordpress'].get('url')
        wp_username = st.secrets['wordpress'].get('username')
        wp_password = st.secrets['wordpress'].get('password')
        
        # Don't use placeholder values
        if wp_url == "YOUR_WORDPRESS_URL":
            wp_url = None
        if wp_username == "YOUR_WORDPRESS_USERNAME":
            wp_username = None
        if wp_password == "YOUR_WORDPRESS_APPLICATION_PASSWORD":
            wp_password = None
    
    # Fall back to environment variables
    if not wp_url:
        wp_url = os.getenv("WORDPRESS_URL")
    if not wp_username:
        wp_username = os.getenv("WORDPRESS_USERNAME")
    if not wp_password:
        wp_password = os.getenv("WORDPRESS_PASSWORD")
        
    return wp_url, wp_username, wp_password

def save_to_notion(title: str, content: str, image=None) -> Optional[str]:
    """
    Save blog post to Notion
    
    Args:
        title: Blog post title
        content: Blog post content
        image: Featured image (PIL.Image)
        
    Returns:
        str: URL of the created page or None if failed
    """
    from notion_client import Client
    
    try:
        notion_api_key, notion_database_id = get_notion_credentials()
        
        if not notion_api_key or not notion_database_id:
            raise APIError("Notion API key or database ID not found in Streamlit secrets or environment variables")
        
        notion = Client(auth=notion_api_key)
        
        properties = {
            "title": {"title": [{"text": {"content": title}}]},
            "Status": {"select": {"name": "Draft"}}
        }
        
        children = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            }
        ]
        
        if image:
            # Save image to temp file
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Upload to Notion
            # This is a simplified version - Notion API might require more complex handling
            children.insert(0, {
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": "https://via.placeholder.com/1024x1024"  # Placeholder - actual upload would need different approach
                    }
                }
            })
        
        response = notion.pages.create(
            parent={"database_id": notion_database_id},
            properties=properties,
            children=children
        )
        
        return response["url"]
    except Exception as e:
        raise APIError(f"Error saving to Notion: {str(e)}")

def save_to_wordpress(title: str, content: str, image=None) -> Optional[str]:
    """
    Save blog post to WordPress
    
    Args:
        title: Blog post title
        content: Blog post content (HTML format)
        image: Featured image (PIL.Image)
        
    Returns:
        str: URL of the created post or None if failed
    """
    from wordpress_xmlrpc import Client, WordPressPost
    from wordpress_xmlrpc.methods.posts import NewPost
    from wordpress_xmlrpc.methods import media
    from wordpress_xmlrpc.compat import xmlrpc_client
    from wordpress_xmlrpc.transport import RequestsTransport

    try:
        wp_url, wp_username, wp_password = get_wordpress_credentials()
        
        if not wp_url or not wp_username or not wp_password:
            raise APIError("WordPress credentials not found in Streamlit secrets or environment variables")
        
        # Set a custom timeout for the transport layer
        transport = RequestsTransport(timeout=180)  # Increase timeout to 60 seconds
        wp = Client(f'{wp_url}/xmlrpc.php', wp_username, wp_password, transport=transport)
        
        post = WordPressPost()
        post.title = title
        post.content = content
        post.post_status = 'draft'
        
        # Handle featured image if provided
        if image:
            # Optimize image size before uploading
            img_byte_arr = BytesIO()
            optimized_image = image.copy()
            optimized_image.thumbnail((1024, 1024))  # Resize to a maximum of 1024x1024
            optimized_image.save(img_byte_arr, format='PNG', optimize=True)
            img_byte_arr = img_byte_arr.getvalue()
            
            # Upload to WordPress
            data = {
                'name': f'{title}_featured_image.png',
                'type': 'image/png',
                'bits': xmlrpc_client.Binary(img_byte_arr),
            }
            
            # Retry upload in case of intermittent failures
            for attempt in range(3):  # Retry up to 3 times
                try:
                    response = wp.call(media.UploadFile(data))
                    attachment_id = response['id']
                    post.thumbnail = attachment_id  # Set as featured image
                    break
                except Exception as upload_error:
                    if attempt == 2:  # If the last attempt fails, raise the error
                        raise APIError(f"Error uploading image to WordPress: {str(upload_error)}")
        
        # Publish the post
        post_id = wp.call(NewPost(post))
        
        return f"{wp_url}/?p={post_id}"
    except Exception as e:
        raise APIError(f"Error saving to WordPress: {str(e)}")
