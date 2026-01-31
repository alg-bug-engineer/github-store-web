# Introduction

This project is a web application designed to store and display GitHub repository information. It allows users to browse, search, and view details about trending and recommended software projects.

## Architecture Overview

The system is designed with a clear separation of concerns, consisting of two main components:

1.  **Data Service (Asynchronous Celery Worker)**
2.  **Backend Service (FastAPI Web Server)**

This decoupled architecture ensures that the user-facing API is fast and resilient, as it does not depend on live calls to the external GitHub API.

### Data Service

The Data Service is a background process powered by Celery. Its sole responsibility is to handle all interactions with the GitHub API and keep the local database up-to-date.

-   **Trigger**: A Celery Beat scheduler triggers the main data synchronization task (`sync_all_github_data`) to run periodically (every 5 minutes).
-   **Data Fetching**: The task uses a dedicated `GitHub Client` to fetch repository metadata and release information from the GitHub API.
-   **Data Storage**: The fetched data is processed, deduplicated, and stored in a PostgreSQL database using a CRUD (Create, Read, Update, Delete) abstraction layer.

This service acts as an independent data ingestion pipeline, ensuring the application's database contains fresh and relevant data without impacting the performance of the main application.

### Backend Service

The Backend Service is a FastAPI application that serves the REST API used by the frontend.

-   **API Endpoints**: It exposes various endpoints for searching, retrieving, and interacting with repository data (e.g., listing trending projects, getting repository details).
-   **Database Interaction**: All API endpoints interact exclusively with the PostgreSQL database. They **do not** make any direct calls to the GitHub API. This ensures low latency and high availability for all user requests.
-   **Frontend Support**: The service provides all the necessary data for the frontend application to render its views and components.

This separation ensures a scalable and maintainable system where the data-intensive background processing is isolated from the real-time request/response cycle of the web application.