
# Django Authentication Project

## Overview

This Django project implements basic user authentication functionalities, including a landing page, sign-up, login, and logout mechanisms. It's designed to demonstrate how to work with Django's authentication system, including user registration and session management.

## Getting Started

Follow these instructions to get the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.8+
- Django (Refer to `requirements.txt` for the exact version)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   
   ```shell
   git clone https://example.com/your-repository.git
   ```
   
2. **Set up a virtual environment**

   Navigate to the project directory and create a virtual environment:
   
   ```shell
   python -m venv venv
   ```
   
   Activate the virtual environment:
   
   - On Windows: cmd: `venv\Scripts\activate.bat` or PowerShell: `venv\Scripts\Activate.ps1`
   - On Unix or MacOS: `source venv/bin/activate`

deactivate to exit

3. **Install dependencies**

   ```shell
   pip install -r requirements.txt
   ```
note for saving you can use: pip freeze > requirements.txt

4. **Run migrations**

   ```shell
   python manage.py migrate
   ```

5. **Start the development server**

   ```shell
   python manage.py runserver
   ```
   
   Visit `http://127.0.0.1:8000/` in your web browser.

6. **Using Django's Admin Site**
creating superuser:
   ```shell
   python manage.py createsuperuser
   ```
user: admin
password: howgoodismycv

### Project Structure

```
/project_root
    /config
        settings.py
        urls.py
    /myapp
        /migrations
        /templates
            /myapp
                login.html
                signup.html
                base.html
                home.html
        models.py
        views.py
        urls.py
        forms.py
    /venv
    manage.py
```

## Features

- Landing page as the initial view with options to sign in or sign up.
- User authentication system including sign-up, login, and logout functionalities.
- Home page accessible only to authenticated users.
- Session management ensuring users are automatically logged out upon closing the browser.

## Contributing

If you're interested in contributing to this project, please fork the repository and submit a pull request.

## Acknowledgments

- Django documentation for providing comprehensive guides and tutorials.

