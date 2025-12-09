# Database Usage Guide

This guide explains how to use the SQLite database created according to the ERD.

## 📋 Database Structure

The database consists of the following tables:

- **users** - User information
- **tips** - Agriculture tips
- **news_categories** - News categories
- **news** - News articles
- **search_history** - Search history
- **chat_log** - Chat logs
- **favorite_news** - Favorite news

## 🚀 Initializing the Database

The database has already been created. If you want to create it from scratch:

```bash
python backend/init_db.py
```

This script:
- Creates all tables
- Sets up relationships (foreign keys)
- Creates indexes
- Adds sample categories and tips

## 📝 Manual Data Entry

### Method 1: Interactive Script (Recommended)

The easiest method is to use the interactive script:

```bash
python backend/add_data.py
```

This script offers you the following options:
1. **Add News** - You can add new news articles
2. **Add Tip** - You can add new agriculture tips
3. **Add Category** - You can add new news categories
4. **List All Data** - You can view existing data

### Method 2: Using Python Code

You can use the `database` module directly in Python code:

```python
from backend import database

# Add category
category_id = database.add_category(
    name="Agriculture News",
    description="General agriculture news"
)

# Add news
news_id = database.add_news(
    title="New Agriculture Technologies",
    summary="New technologies in the agriculture sector",
    content="Detailed news content goes here...",
    category_id=category_id,
    image_url="https://example.com/image.jpg"  # Optional
)

# Add tip
tip_id = database.add_tip(
    title="Tomato Growing",
    content="Regular watering is important for tomato plants.",
    difficulty="Easy"  # Optional: Easy, Medium, Hard
)
```

### Method 3: Using API Endpoints

You can use API endpoints when the backend is running:

```bash
# Add category
curl -X POST "http://localhost:8000/api/categories" \
  -H "Content-Type: application/json" \
  -d '{"name": "Agriculture News", "description": "General agriculture news"}'

# Add news
curl -X POST "http://localhost:8000/api/news" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Agriculture Technologies",
    "summary": "New technologies in the agriculture sector",
    "content": "Detailed news content...",
    "category_id": 1,
    "image_url": "https://example.com/image.jpg"
  }'

# Add tip
curl -X POST "http://localhost:8000/api/tips" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tomato Growing",
    "content": "Regular watering is important for tomato plants.",
    "difficulty": "Easy"
  }'
```

## 📊 Querying Data

### Using Python

```python
from backend import database

# Get all news
news = database.get_all_news(limit=10)

# Get news by category
news = database.get_all_news(category_id=1)

# Get all tips
tips = database.get_all_tips(difficulty="Easy")

# Get categories
categories = database.get_all_categories()
```

### Using API

```bash
# All news
curl "http://localhost:8000/api/news"

# News in a specific category
curl "http://localhost:8000/api/news?category_id=1"

# All tips
curl "http://localhost:8000/api/tips"

# Easy tips
curl "http://localhost:8000/api/tips?difficulty=Easy"

# Categories
curl "http://localhost:8000/api/categories"
```

## 🔧 Updating and Deleting Data

### Using Python

```python
# Update news
database.update_news(
    news_id=1,
    title="Updated Title",
    summary="Updated summary"
)

# Delete news
database.delete_news(news_id=1)

# Update tip
database.update_tip(
    tip_id=1,
    title="Updated Tip Title"
)

# Delete tip
database.delete_tip(tip_id=1)
```

### Using API

```bash
# Update news
curl -X PUT "http://localhost:8000/api/news/1" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'

# Delete news
curl -X DELETE "http://localhost:8000/api/news/1"
```

## 📍 Database File

The database file is stored as `database.db` in the project root directory.

## 🔍 Examining the Database

To examine the SQLite database directly:

```bash
# Using SQLite CLI
sqlite3 database.db

# SQLite commands
.tables          # List all tables
.schema news     # Show news table structure
SELECT * FROM news;  # Show all news
SELECT * FROM tips;  # Show all tips
```

## 📚 API Documentation

When the backend is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ⚠️ Notes

1. **Foreign Key Relationships**: When adding news, you must use an existing `category_id`
2. **Unique Constraints**: In the `favorite_news` table, a user cannot favorite the same news article more than once
3. **Timestamps**: `created_at` fields are automatically added
4. **Data Backup**: Regularly backup the `database.db` file

## 🎯 Example Usage Scenario

1. **Create Category**:
   ```python
   cat_id = database.add_category("Technology", "Agriculture technologies")
   ```

2. **Add News**:
   ```python
   news_id = database.add_news(
       title="AI in Agriculture",
       summary="AI technology is revolutionizing agriculture",
       content="Detailed content...",
       category_id=cat_id
   )
   ```

3. **Add Tip**:
   ```python
   tip_id = database.add_tip(
       title="Smart Irrigation",
       content="Set up an automatic irrigation system with sensors",
       difficulty="Medium"
   )
   ```

4. **View Data**:
   ```python
   news = database.get_all_news()
   tips = database.get_all_tips()
   ```
