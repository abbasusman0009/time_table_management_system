# Northeastern University Timetable Management System (TTMS)

A production-ready Django application for automated, conflict-free university scheduling.

## Features
- **Automated Scheduling**: Greedy constraint-based engine.
- **Conflict Resolution**: Manual overrides and reports.
- **Role-Based Access**: Specialized portals for Admin, Lecturers, and Students.
- **Branded UI**: Modern interface with NEU Gombe styling.
- **PDF Export**: Downloadable schedules for all roles.

## Prerequisites
- **Python**: 3.11+
- **MySQL**: 8.0+
- **Virtualenv** (Recommended)

## Local Setup

1. **Clone the repository** (or copy the files into your workspace).
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment**:
   - Copy `.env.example` to `.env`.
   - Update `DB_PASSWORD` and other credentials for your local MySQL instance.
5. **Prepare the Database**:
   - Create the MySQL database: `CREATE DATABASE ttms_db;`.
6. **Apply Migrations**:
   ```bash
   python manage.py makemigrations accounts academics venues scheduling timetable
   python manage.py migrate
   ```
7. **Seed Data**:
   ```bash
   python manage.py seed_data
   ```
8. **Run the Server**:
   ```bash
   python manage.py runserver
   ```

## Default Credentials
- **Admin**: `admin` / `admin123`
- **Lecturer**: `dr.bello` / `lecturer123`
- **Student**: Register via the signup page.

## Project Structure
- **/apps**: Domain-specific logic (Academics, Venues, Scheduling).
- **/templates**: Responsive Bootstrap 5 templates.
- **/static**: Custom CSS and assets.

---
Built for Northeastern University, Gombe State.
