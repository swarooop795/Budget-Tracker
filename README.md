Budget Tracker
A personal finance web application built with Flask that helps users record income and expenses, review transaction history, manage account settings, and export financial statements. It also includes a separate admin area for user management and visitor statistics.
Project status: Core application features are implemented. Automated tests are included in tests/test_app.py; run them locally before relying on the results or submitting the project.

Table of Contents
- Features
- Technology Stack
- Project Structure
- Requirements
- Setup and Run Locally
- Environment Configuration
- Data Model
- Design Decisions
- Automated Tests
- What Is Finished
- Limitations and Future Improvements
- AI Tools Used
Features
User features
- User registration and login.
- Password hashing using Werkzeug security utilities.
- Add income and expense statements.
- View recorded financial statements and account totals.
- Manage account settings.
Admin features
- Separate admin login.
- Admin dashboard with user, statement, and visitor statistics.
- Charts summarizing visitor browsers, operating systems, and visits over time.
- User-management pages.
Application features
- Flask application factory and blueprints to organize routes.
- SQLAlchemy models for database access.
- WTForms-based form handling and validation.
- SQLite database by default.
- Flask-Migrate/Alembic database migrations.
Technology Stack
Area	Technology
Backend	Python, Flask
Database access	Flask-SQLAlchemy, SQLAlchemy
Default database	SQLite
Migrations	Flask-Migrate, Alembic
Forms	Flask-WTF, WTForms
Authentication utilities	Werkzeug security and Flask sessions
Charts	Matplotlib
Frontend	HTML, CSS, JavaScript, Jinja templates
Testing	pytest
Development server	Flask CLI


Project Structure
budget_tracker/
├── app/
│   ├── static/                  # CSS, fonts, and other static assets
│   ├── templates/               # Jinja HTML templates
│   ├── views/
│   │   ├── auth.py              # Registration, login, and logout
│   │   ├── home.py              # Home page and statement operations
│   │   ├── settings.py          # Account settings
│   │   └── admin.py             # Admin login, dashboard, and user management
│   ├── __init__.py              # Flask application factory and request hooks
│   ├── app_functions.py         # Authentication helpers and access decorators
│   ├── commands.py              # CLI command to create an admin account
│   ├── db.py                    # SQLAlchemy database models
│   ├── forms.py                 # Form definitions and validation
│   └── functions.py             # Shared helpers and chart functions
├── instance/                    # Local instance data, depending on configuration
├── migrations/                  # Alembic migration files, if initialized
├── tests/
│   └── test_app.py              # Automated backend tests
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
└── README.md
Some generated folders, such as migrations/, may not exist until database migrations are initialized.
Requirements
- Python installed and available from PowerShell as py or python.
- pip.
- Git, if you plan to push the project to GitHub.
- A web browser.
The project has been set up to work with Python 3.14 in the current development environment. If any dependency does not yet provide a compatible build for your specific Python installation, use a supported Python version for that dependency or update the dependency version as needed.
Setup and Run Locally
The following instructions use Windows PowerShell.
1. Open the project directory
cd "C:\path\to\budget_tracker"
Replace the path with the folder where you extracted the project.
2. Create and activate a virtual environment
py -m venv env
.\env\Scripts\Activate.ps1
If PowerShell blocks activation in the current terminal, run this for the current process only and try again:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\env\Scripts\Activate.ps1
3. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
Install pytest if it is not already listed in the requirements:
pip install pytest
4. Initialize the database
If the project does not already have a migrations/ directory, initialize migrations once:
flask --app main db init
Create and apply the initial migration:
flask --app main db migrate -m "Create initial database tables"
flask --app main db upgrade
If the project already has migration files, do not run db init again. Apply the existing migrations with:
flask --app main db upgrade
5. Create an administrator
flask --app main createadminuser
Follow the prompts for an admin username, email address, and password. Use a password of at least eight characters. Keep these credentials private.
6. Start the application
flask --app main run
Open the app in your browser:
- Application: http://127.0.0.1:5000/
- User authentication: http://127.0.0.1:5000/auth/
- Admin login: http://127.0.0.1:5000/admin/login
- Admin dashboard: http://127.0.0.1:5000/admin/
Stop the local development server with Ctrl+C in the terminal.
Environment Configuration
The app reads the following environment variables:
Variable	Purpose	Default
SECRET_KEY	Flask session signing key	A development fallback in the source code
DB_URI	SQLAlchemy database connection URI	sqlite:///master.sqlite3


For local PowerShell development, set a secret key for the current terminal session:
$env:SECRET_KEY = "replace-with-a-long-random-secret"
The database URI can also be overridden, for example:
$env:DB_URI = "sqlite:///master.sqlite3"
Do not use a public or predictable secret key in production. Configure environment variables through your hosting provider and never commit real secrets, passwords, or production database credentials to GitHub.
Data Model
The application uses SQLAlchemy models defined in app/db.py.
User
Stores the regular user's account information:
- id: primary key.
- name: user's display name.
- email: unique email address.
- password: password hash, not the plain-text password.
- session_id: identifier used by the application's session/authentication logic.
- Relationship to the user's statements.
Statements
Stores a user's financial transactions:
- id: primary key.
- description: transaction description.
- amount: transaction amount.
- operation_time: date/time associated with the transaction.
- statement_id: unique statement identifier.
- user_id: foreign key connecting the statement to its owner.
Amount convention: income is represented as a positive amount and expenses as a negative amount. This makes net totals straightforward to calculate by summing transaction amounts.
Admin
Stores administrator account information:
- id: primary key.
- username: administrator's name.
- email: unique email address.
- password: password hash.
- session_id: unique identifier used for the admin session.
Admin authentication is separate from regular user authentication.
VisitorStats
Stores visitor/request statistics used by the admin dashboard:
- id: primary key.
- browser: detected browser family.
- device: detected device information.
- operating_system: detected operating system.
- is_bot: whether the user agent is classified as a bot.
- date: timestamp associated with the visit/request.
Visitor data is used to build aggregate statistics and charts. Consider privacy, retention, and consent requirements before deploying visitor tracking publicly.
Design Decisions
1. Application factory: create_app() configures the Flask application and extensions in one place.
2. Blueprints: authentication, home/transactions, settings, and admin routes are separated into different modules to keep route code organized.
3. SQLAlchemy models: database entities and relationships are represented through models instead of scattering raw SQL across route handlers.
4. Password hashing: passwords are hashed with Werkzeug security functions before storage and checked using check_password_hash.
5. Positive/negative transaction values: income is positive and expense is negative, simplifying net balance calculations.
6. SQLite by default: SQLite keeps local setup simple. DB_URI allows the database connection to be configured for another SQLAlchemy-supported database.
7. Database migrations: Flask-Migrate/Alembic tracks schema changes.
8. Isolated tests: tests configure a separate in-memory SQLite database so test records do not need to be written to the developer's normal database.
Automated Tests
Automated tests are in tests/test_app.py. The included test cases cover:
1. Unauthenticated access to the home page redirects to login.
2. Registration creates a user record and stores a password hash.
3. A valid login redirects to the home page.
4. An invalid password does not authenticate the user.
5. An income statement is saved with a positive amount.
6. An expense statement is saved with a negative amount.
7. CSV export contains a saved statement.
8. The admin dashboard requires an admin session.
9. An admin can log in and access the dashboard.
Run the tests
From the project root, with the virtual environment activated:
pytest -v
To run only this test file:
pytest -v tests/test_app.py
Review the output and resolve any failures before submitting. Test behavior can depend on the current route definitions, form fields, and decorators, so the test suite must be run against the final code rather than assuming all tests pass.
What Is Finished
The following features are present in the project structure and application code:
- User registration and login.
- Password hashing and session-based authentication.
- Income and expense statement handling.
- Financial statement history and totals.
- Account settings pages.
- CSV export for statements.
- Admin login and dashboard.
- User-management routes.
- Visitor statistics and dashboard charts.
- SQLAlchemy data models and migration support.
- Initial automated backend test cases and project documentation.
Limitations and Future Improvements
With more time, I would:
- Expand test coverage for transaction editing/deletion, invalid input, account settings, and admin user-management operations.
- Validate transaction amounts and dates more thoroughly, including negative or malformed user input.
- Use Python's csv module for robust CSV escaping of commas, quotation marks, and newlines.
- Review visitor tracking so only appropriate requests are recorded, with clear retention and privacy controls.
- Improve handling of empty data sets in dashboard charts and statistics.
- Add pagination for large transaction and user lists.
- Strengthen production configuration, including secret management, secure cookies, logging, and error monitoring.
- Add CI to run tests automatically on each push or pull request.
- Add deployment instructions specific to the selected hosting provider.
- Review all password update paths to ensure they use supported Werkzeug hashing methods.
AI Tools Used
ChatGPT was used to:
- Help organize the README and document the project structure.
- Suggest backend test cases for authentication, transaction handling, and admin access.
- Explain Flask, SQLAlchemy, and testing concepts.
- Help troubleshoot application errors during development.
AI-generated suggestions should be reviewed and tested. I am responsible for understanding the application's code and being able to explain the data model, route behavior, design decisions, and each automated test.
