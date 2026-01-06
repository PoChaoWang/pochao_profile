## Introduction
This project uses a web crawler to collect overseas F1 news articles in English and stores them in Supabase's PostgreSQL. Then, it uses OpenRouter with Gemini 2.0 Flash for translation, and finally displays the content on the frontend page.

Originally, this project was created to help me quickly access overseas F1 news. Watching F1 races is my hobby, but I don't want to spend too much time searching for news or reading English articles. Therefore, I used Open Router's Gemini to translate overseas news and published the content on https://f1-news.netlify.app/.

# Backend
The `backend` directory contains the core logic for fetching, processing, translating, editing, and uploading F1 news articles. It integrates with multiple RSS feeds, processes the data, and stores the results in a Supabase database.

---

## Features
1. **Fetch News**: Retrieve F1 news articles from various RSS feeds.
2. **Clean and Merge**: Remove unnecessary HTML tags, clean content, and merge data from multiple sources.
3. **Translate**: Translate news articles into Traditional Chinese using the Gemini API.
4. **Edit Content**: Refine translated content to ensure clarity and conciseness.
5. **Upload to Database**: Store processed data in a Supabase database.
6. **Related News**: Generate related news recommendations based on content similarity.

---

## File Structure and Functionality

### 1. `fetch_news.py`
- **Purpose**: Fetch F1 news from RSS feeds and parse article content, images, and metadata.
- **Key Functions**:
  - `fetch_f1_news`: Fetch and parse RSS feed data.
  - `extract_image_url`: Extract image URLs from RSS entries.
  - `scrape_article_content`: Extract article content using BeautifulSoup.
  - `author`: Extract the author's name from the article.

---

### 2. `merge_and_clean.py`
- **Purpose**: Merge news data from multiple sources and clean unnecessary HTML tags and content.
- **Key Functions**:
  - `clean_data`: Clean HTML content and remove irrelevant tags.
  - `merge_and_clean_data`: Merge and clean data, removing duplicate entries.
  The cleaned data will be uploaded to Supabase without the title_zh and content_zh fields.

---

### 3. `translate_news.py`
- **Purpose**: Translate news titles and content into Traditional Chinese using the Gemini API.
- **Key Functions**:
  - `translate_text`: Translate text using the Gemini API.
  - `fetch_and_translate_column`: Translate titles and content, updating their translation status.
  Searches the Supabase database for entries with a 'pending' status, translates the title and content, and updates the title_zh and content_zh fields in the database.

---

### 4. `content_editor.py`
- **Purpose**: Edit translated content to ensure clarity, remove redundant sections, and retain meaningful information.
- **Key Functions**:
  - `edit_text`: Edit content using the Gemini API.
  - `content_edit`: Process and refine translated content.

---

### 5. `title_editor.py`
- **Purpose**: Edit translated titles to ensure they are concise and free of unnecessary HTML tags.
- **Key Functions**:
  - `edit_text`: Edit titles using the Gemini API.
  - `title_edit`: Process and refine translated titles.

---

### 6. `upload_to_supabase.py`
- **Purpose**: Upload processed data to the Supabase database.
- **Key Functions**:
  - `upload_to_supabase`: Insert or update data in the Supabase database using the `upsert` method.

---

### 7. `related_news.py`
- **Purpose**: Generate related news recommendations based on content similarity.
- **Key Functions**:
  - Use `SentenceTransformer` to calculate embeddings and cosine similarity.
  - Insert related news data into the Supabase database.
  It hasn't been integrated into the frontend yet.

---

### 8. `web.py`
- **Purpose**: Provide a FastAPI-based RESTful API for accessing news data.
- **Endpoints**:
  - `/index`: Paginated list of news articles.
  - `/news/{id}`: Retrieve a specific news article and its related articles.
  - `/search`: Search for news articles by keyword.
  - `/health`: Health check endpoint.

---

### 9. `main.py`
- **Purpose**: Orchestrate the entire workflow, including fetching, cleaning, translating, editing, and uploading news data.
- **Workflow**:
  1. Fetch news from multiple sources.
  2. Merge and clean the data.
  3. Translate titles and content.
  4. Edit translated content and titles.
  5. Upload processed data to Supabase.

---

## Environment Variables
The application uses environment variables for configuration. These should be stored in a `.env` file:
- `SUPABASE_URL`: Supabase project URL.
- `SUPABASE_KEY`: Supabase API key.
- `GEMINI_API_KEY`: API key for the Gemini translation service.

---

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt

-------------------------------------------------------------------------------------------------------------------------

# Frontend
The `frontend` directory contains the React-based user interface for the F1 News application. It provides a responsive and user-friendly platform for browsing, searching, and reading F1 news articles. The frontend communicates with the backend API to fetch and display news data.

---

## Features
1. **News Listing**: Display a paginated list of F1 news articles with titles, authors, publication dates, and summaries.
2. **Search Functionality**: Search for news articles by keywords.
3. **News Details**: View detailed content of individual news articles, including related news.
4. **Responsive Design**: Optimized for both desktop and mobile devices.
5. **SEO and Social Sharing**: Includes meta tags for better SEO and social media sharing.

---

## File Structure and Functionality

### 1. `src/`
- **Purpose**: Contains the main source code for the frontend application.
- **Key Files**:
  - `App.jsx`: The main component for displaying the news list.
  - `News.jsx`: Displays detailed content for a specific news article.
  - `Search.jsx`: Handles the search functionality and displays search results.
  - `About.jsx`: Provides information about the application.
  - `NotFound.jsx`: Displays a 404 page for invalid routes.
  - `api.js`: Contains functions for interacting with the backend API.
  - `useGtag.js`: Integrates Google Analytics for tracking user interactions.
  - `style.css`: Defines the global styles for the application.

---

### 2. `src/components/`
- **Purpose**: Contains reusable components for the application.
- **Key Components**:
  - `NavBar.jsx`: The navigation bar with links and a search form.
  - `Footer.jsx`: The footer section with copyright information.

---

### 3. `public/`
- **Purpose**: Contains static assets and configuration files.
- **Key Files**:
  - `_redirects`: Configures routing for deployment on platforms like Netlify.
  - `tyre.svg`, `f1404nb.png`: Static images used in the application.

---

### 4. `build/`
- **Purpose**: Contains the production build of the application, generated by Vite.

---

### 5. `vite.config.js`
- **Purpose**: Configuration file for Vite, specifying the build directory and plugins.

---

## Environment Variables
The application uses environment variables for configuration. These should be set in the deployment environment:
- `GA4_ID`: Google Analytics 4 tracking ID.

---

## How to Run
1. Install dependencies:
   ```bash
   npm install