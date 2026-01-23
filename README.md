# MY JOURNAL APP API

Welcome the "My Journal App" API and database! 
This is an API that allows users to make an account, and make journal entries that are only visible to those users by using JSON Web Token

## Set up

1. Fork and clone the Repository

2. Install dependencies

    A. Navigate to the folder after cloning the repository and enter the command `pipenv install` to install the dependencies for the backend API.

    B. Enter the command `npm install --prefix client-with-jwt` to install the dependencies for the frontend.

    C. Enter `pipenv shell` to start the vitual environment.
3. Create the database

    A. Navigate to the `server` folder

    B. Run `flask db init` to initialize database migration and create the folders for migration data

    C. Enter `flask db migrate -m "initial migration"` for first migration

    D. Then, enter `flask db upgrade head` to form the database

    E. Finally, enter `python seed.py` to run the Seed file and fill your database with random data

### Run the API

1. Enter `cd server` to navigate to the server.

2. Enter `python app.py` to start the API locally.

3. In another terminal, navigate to the root folder of the app and enter `npm start --prefix client-with-jwt` to start the React frontend, which should automatically load into a browswer.


#### API Endpoints

1. POST Login (`/login`) - Allows login with username with password

2. POST Signup (`/signup`) - Allows user to create a new username and password

3. GET Me (`/me`) - Checks for token, then retrieves current user

4. GET and POST JournalEntryIndex (`/journal_entries`) - Displays journal entries attributed to current user, and allows user to create new entries with a title, date, and content.

5. PATCH and DELETE JournalEntryDetail (`/journal_entries/<int:journal_entry_id>`) - allows current user to edit journal entries, and/or delete journal entries.

