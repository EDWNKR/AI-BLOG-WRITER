# AI Blog Writer

An AI-powered tool that generates structured, SEO-optimized blog posts using OpenAI's GPT-4 API.

## Features

- Generate complete blog posts with proper structure (headers, bullet points, etc.)
- SEO optimization with keyword targeting
- Generate featured images using DALL-E
- Adjust tone, length, and style
- Export to Markdown or HTML
- Integration with Notion and WordPress

## The Importance of SEO Optimization

Search Engine Optimization (SEO) is critical for increasing your website's visibility and attracting more visitors. Here's why SEO matters:

### Traffic Growth
- **Organic Discovery**: 53% of website traffic comes from organic search
- **Targeted Visibility**: Appear in front of users actively searching for your content
- **Cost-Effective**: Unlike paid advertising, organic traffic continues without ongoing costs

### Business Impact
- **Higher Conversion Rates**: SEO-driven visitors convert at higher rates than outbound leads
- **Credibility Building**: Higher rankings signal trustworthiness to potential visitors
- **Competitive Advantage**: Outranking competitors directly impacts market share

### Long-Term Value
- **Compounding Returns**: Well-optimized content continues to drive traffic for years
- **Measurable Results**: Track performance with analytics to refine your strategy
- **Adapting to Algorithms**: Staying current with SEO practices ensures continued visibility

This AI Blog Writer tool helps implement SEO best practices by automatically:
- Incorporating targeted keywords throughout your content
- Creating properly structured content with appropriate heading hierarchy
- Generating engaging, high-quality content that keeps readers on your page longer

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your API keys:
   ```
   cp .env.example .env
   ```
4. Edit the `.env` file with your API keys

## Usage

Start the Streamlit app:
```
streamlit run app.py
```

## Detailed Usage Example

Here's a step-by-step example of how to use the AI Blog Writer:

### 1. Configure Blog Settings

In the sidebar, enter your blog details:

- **Blog Title**: "10 Essential SEO Strategies for Small Business Websites in 2023"
- **SEO Keywords** (enter one per line):
  ```
  small business SEO
  website optimization
  local SEO
  content marketing
  SEO strategies
  Google ranking
  keyword research
  mobile optimization
  page speed
  business growth
  ```

### 2. Content Settings

Choose the style and length of your blog:

- **Tone**: Professional
- **Length**: Medium (1000 words)

### 3. Featured Image

- **Generate featured image with DALL-E**: Checked
- **Custom image prompt** (optional): "A small business owner optimizing their website for search engines, with visual elements representing SEO concepts like rankings, keywords, and search results"

### 4. Output and Export Options

- **Output Format**: Choose Markdown or HTML
- **Export Options**: Select Download, Notion, or WordPress

### 5. Generate Content

Click the "🚀 Generate Blog Post" button and wait for your content to be created. The app will:

1. Generate the blog content with proper structure
2. Create a featured image if requested
3. Display the content in the preview area
4. Show word count statistics

### 6. Export Your Content

After generation, you can:
- Download the content as a file
- Save it directly to Notion (if configured)
- Publish it as a draft to WordPress (if configured)

## Example Output

The generated blog post will include:

- A compelling title and introduction
- Properly formatted H2 and H3 headers
- Bullet points and numbered lists where appropriate
- Internal link placeholders in the format [related topic]
- SEO-optimized content targeting your keywords
- A professional conclusion

## Requirements

- Python 3.8+
- OpenAI API key
- Notion API key (optional)
- WordPress credentials (optional) 