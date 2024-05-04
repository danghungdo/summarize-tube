# summarize-tube

## Overview
Just summarizing the Youtube video, a Django based web application that provide summarization of Youtube videos, making it easier to grasp the main points without watching the whole video.
This project is for learning Django purpose and it takes advantages of these 2 platforms:
- AssemblyAI for generate the transcript of the video
- OpenAI for summarize the transcript
## Installation
1. Clone the repository:
```git clone git clone https://github.com/danghungdo/summarize-tube.git```

2. Install dependencies:
```pip install -r requirements.txt```

3. Create `.env` file in the root directory with the following contents:
```
# Postgresql
DB_NAME=your_postgresql_database_name
DB_USER=your_postgresql_database_user
DB_PASSWORD=your_postgresql_database_password
DB_HOST=your_postgresql_database_host
DB_PORT=your_postgresql_database_port

#Django secret key
SECRET_KEY=your_django_secret_key

# OPENAI
OPENAI_API_KEY=your_openai_api_key

# Assemblyai
AAI_API_KEY=your_assemblyai_api_key
```
4. Create a `media` folder in the root directory
5. Apply migrations:
```python manage.py migrate```
6. Run the development server:
```python manage.py runserver```

