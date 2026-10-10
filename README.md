# AI Website Generator

An AI-powered web application that generates ready-to-run website projects based on user-provided website requirements and reference URLs. The goal is to simplify website development by automatically creating essential frontend pages, backend APIs, database integration, and test files.

## 🚀 Project Overview

The AI Website Generator allows users to describe the type of website they want to build, such as an e-commerce website, personal portfolio, educational platform, restaurant website, or admin dashboard.

Based on the submitted requirements, the application generates a structured project containing the website interface, backend functionality, database setup, automated tests, and documentation.

## ✨ Features

- **Requirement-Based Generation:** Generate website projects from natural-language descriptions.
- **Reference Website Analysis:** Analyze reference URLs to extract information such as page titles and headings.
- **Multiple Website Categories:** Support for business websites, portfolios, e-commerce layouts, educational websites, restaurants, and dashboards.
- **Responsive User Interface:** Generate layouts designed for desktop and mobile screens.
- **Backend API Development:** Use FastAPI to provide backend endpoints.
- **Database Integration:** Use SQLite to store contact form submissions.
- **Automated Testing:** Include tests to verify essential application functionality.
- **Project Structure Generation:** Create source files, templates, dependencies, and README documentation.
- **Local Execution:** Generate projects that can be installed and run locally.

## 🛠️ Technologies Used

- Python
- FastAPI
- HTML5
- CSS3
- JavaScript
- SQLite
- Jinja2
- Requests
- Beautiful Soup
- Pytest
- Uvicorn

## 🏗️ System Architecture

1. **User Input:** The user provides a reference URL and website requirements.
2. **Reference Analysis:** The application extracts basic information from the reference website.
3. **Requirement Processing:** The generator identifies the intended website category and required sections.
4. **Project Generation:** The application creates frontend templates, backend APIs, database code, and test files.
5. **Database Integration:** SQLite stores supported form submissions.
6. **Testing:** Automated tests check essential functionality.
7. **Local Deployment:** The generated website can be started on localhost.

## 📂 Project Structure

```text
AI-Website-Generator/
├── generator/
│   ├── main.py
│   └── website_generator.py
├── generated_projects/
│   └── generated_website/
│       ├── main.py
│       ├── templates/
│       │   └── index.html
│       ├── tests/
│       │   └── test_app.py
│       ├── requirements.txt
│       ├── README.md
│       └── project.json
├── tests/
├── requirements.txt
└── README.md
```

*Note: The generated project names and exact folder structure may vary depending on your implementation.*

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.12 or a compatible Python version
- pip
- Git
- Visual Studio Code (recommended)

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd AI-Website-Generator
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bat
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the application

```bash
python -m uvicorn generator.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Open the application

- Application: http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs

Keep the terminal running while using the application.

## 🌐 Running a Generated Website

Navigate to the generated project directory:

```bash
cd generated_projects/YOUR_GENERATED_PROJECT
```

Install its dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the generated website:

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8001 in your browser.

Replace `YOUR_GENERATED_PROJECT` with the actual generated folder name.

## 🧪 Running Tests

Run the generator's tests from the main project directory:

```bash
python -m pytest -v
```

To run tests for an individual generated project, navigate to that project's directory and run:

```bash
python -m pytest -v
```

## 🎯 Use Cases

- Rapid prototyping of websites
- Generating portfolio and business website templates
- Creating educational and restaurant website layouts
- Producing starter projects for web development
- Learning backend API development and database integration
- Reducing repetitive website setup work




