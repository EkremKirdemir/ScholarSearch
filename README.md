# Scholar Search Engine

Scholar Search Engine is a Django web application that interfaces with academic databases like SemanticScholar to search for academic papers based on user-provided keywords. The results are then displayed to the user, offering a clean and accessible interface for academic research.

## Features

- **Keyword Search**: Users can enter a search term to find relevant academic papers.
- **Result Filtering**: Results can be filtered by paper name, authors, abstract, and more.
- **Responsive Design**: A user-friendly interface that adapts to various screen sizes.
- **Pagination**: Search results are paginated for easier navigation.

## Local Setup

To get this project up and running on your local machine, follow these steps:

1. Clone the repository:
  - git clone https://github.com/yourusername/scholar-search-engine.git
  - cd scholar-search-engine
   
2.Set up a Python virtual environment and activate it:
- python -m venv venv
- source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3.Install the required dependencies:
- pip install -r requirements.txt

4.Run database migrations:
- python manage.py migrate

5.Start the development server:
- python manage.py runserver

6.Open your browser and navigate to http://127.0.0.1:8000/ to use the application.

## Technologies
- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** MongoDB
