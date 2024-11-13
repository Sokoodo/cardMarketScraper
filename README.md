1. Clone the Repository

2. Set Up Python Environment
  python -m venv .venv
  .venv\Scripts\activate

3. Install Dependencies
   pip install -r requirements.txt

4. Configure Environment Variables
  DATABASE_URL=postgresql://user:password@localhost:5432/your_database
  SECRET_KEY=your_secret_key

5. Set Up and Configure the Database
  ex. CREATE DATABASE your_database;

6. Apply Database Migrations with Alembic
  alembic upgrade head

7. Run the Application
  uvicorn main:app --reload
