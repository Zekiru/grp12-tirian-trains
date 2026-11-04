# CSCI41-Grp12 Tirian Trains

# Setup Guide

## Prerequisites

- **Python**
- **pip**
- **Git**

## Setup Instructions
1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

2. Create and Activate a Virtual Environment

Windows
```bash
python -m venv venv
venv\Scripts\activate
```

macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```

4. Generate the Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

5. Create the .env file within the project folder
```bash
# insert inside .env file
SECRET_KEY='your_generated_secret_key_here'
DEBUG=True
```

6. Run the Development Server
```bash
python manage.py runserver
```
