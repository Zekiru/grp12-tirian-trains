# CSCI41-Grp12 Tirian Trains

A multi-app Django web application for managing trains, maintenance logs, route networks (`S-Series` circular loop and `A-Series` inter-town network), trip schedules, and customer ticket itineraries.

## Project Structure

```text
grp12-tirian-trains/
├── apps/
│   ├── trains/             # Trains, maintenance crew, and maintenance logs
│   ├── route_schedules/    # Stations, S-Series circular loop, A-Series links, and TripSchedules
│   └── tickets/            # Customers, Tickets, and ordered multi-leg TicketItineraries
├── rebuilding/             # Modular DB cleanup, migration regeneration, and .env superuser setup
├── seeding/                # Idempotent, dependency-ordered database seeding & constraint checks
├── rebuild_db.py           # One-command full DB reset, migrate, seed, and superuser pipeline
├── seed.py                 # Standalone database seeding & verification entry point
├── manage.py
└── .env                    # Local environment variables & superuser credentials (git-ignored)
```

---

## Setup Guide

### Prerequisites

- **Python** (3.11+)
- **pip**
- **Git**

### Setup Instructions

1. **Clone the Repository**
```bash
git clone <repository-url>
cd <repository-folder>
```

2. **Create and Activate a Virtual Environment**

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

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Generate the Secret Key**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

5. **Create the `.env` file within the project folder**
Include your Django settings along with the default admin credentials used by `rebuild_db.py`:
```env
SECRET_KEY='your_generated_secret_key_here'
DEBUG=True

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=your_admin_password
```

6. **Initialize the Database, Seed Data, and Create Superuser**
```bash
python rebuild_db.py
```

7. **Run the Development Server**
```bash
python manage.py runserver
```

---

## Development Workflows & Features

### Full Database Rebuild (`rebuild_db.py`)
Because generated migration files (`**/migrations/*.py` except `__init__.py`) and `db.sqlite3` are git-ignored during active schema iteration, use `rebuild_db.py` to spin up or reset your local environment in a single step:

```bash
python rebuild_db.py
```

This runs the complete 5-step pipeline:
1. Deletes any existing `db.sqlite3` database file.
2. Removes old system-generated migration files across `apps/*`.
3. Runs `makemigrations` and `migrate` across `trains`, `route_schedules`, and `tickets`.
4. Executes `seed.main()` to populate initial train, route, schedule, and ticketing records.
5. Creates a Django superuser automatically from your `.env` credentials.

### Standalone Seeding (`seed.py`)
You can also run the seeding pipeline independently without wiping migrations or your superuser account:

```bash
# Idempotent seed (safe to re-run without duplicating records)
python seed.py

# Clear existing seeded records in dependency order before re-seeding
python seed.py --reset
```

### Automated Domain Signals (`signals.py`)
Each domain app isolates reactive database logic inside a dedicated `signals.py` module registered in `apps.py`:
- **`apps.route_schedules`:**
  - Automatically creates or removes `ASeries` records when a station is assigned to or removed from the `A-Series` route, and cleans up `SSeries` records when removed from `S-Series`.
  - Automatically syncs or deletes reverse `ASeriesLink` edges when `bidirectional=True` is toggled.
- **`apps.tickets`:**
  - Automatically recalculates and updates `Ticket.total_cost` whenever `TicketItinerary` legs are added, updated, or removed.
