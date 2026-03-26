# Expense Tracker Flask

A comprehensive financial management application built with Flask, allowing users to track income, expenses, and export reports.

## Project Structure

- `app.py`: Main Flask application entry point.
- `models.py`: Database models (SQLAlchemy) for users and transactions.
- `config.py`: Application configurations and database secrets.
- `export_pdf.py`: Utility for generating PDF financial reports.
- `templates/`: Jinja2 templates for the user interface.
- `migrations/`: Database migration history.

## Development Iterations
The repository includes several versions (`app2.py`, `app3_works.py`, etc.) demonstrating the incremental addition of features like constraints and export utilities.

## Getting Started

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Environment Setup**: Update `config.py` with your database URI.
3.  **Run Application**:
    ```bash
    python app.py
    ```

## Key Features
- **PDF Export**: Generate professional financial snapshots.
- **SQLAlchemy ORM**: Clean data management and persistence.
- **User Authentication**: Secure multi-user expense tracking.