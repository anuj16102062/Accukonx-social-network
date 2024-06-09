# Accukonx-social-network

This is a Django-based social network API with user authentication and friend management functionalities.

## Features
- User login/signup
- Search users by email or name
- Send/accept/reject friend requests
- List friends and pending friend requests
- List unconnected frineds

## Installation

### Prerequisites
- Python 3.8+
- Docker (for containerization)

### Steps

1. Clone the repository
    ```sh
    git clone <repository-url>
    cd accukonx_social_network
    ```

2. Create and activate a virtual environment
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages
    ```sh
    pip install -r requirements.txt
    ```

4. Apply database migrations
    ```sh
    python manage.py migrate
    ```

5. Create a superuser
    ```sh
    python manage.py createsuperuser
    ```

6. Run the development server
    ```sh
    python manage.py runserver
    ```

## Docker

### Build and Run with Docker

1. Build the Docker image
    ```sh
    docker-compose build
    ```

2. Run the Docker container
    ```sh
    docker-compose up
    ```

3. The application will be available at `http://127.0.0.1:8000/`

## API Documentation
API documentation is available via postman collections


