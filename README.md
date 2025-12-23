# Microbiome Taxonomy Browser

A web-based application for managing and searching microbiome sample data using multiple search algorithms.

## Features

- User authentication and authorization
- Sample management (create, view, delete)
- Multiple search strategies:
  - Exact Match
  - Approximate Match
  - Hierarchical Match
  - Abundance Filter

## Technology Used

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Database**: SQLite with SQLAlchemy ORM
- **Design Pattern**: Strategy Pattern

## Prerequisites

- Python 3.7+
- pip

## Installation

1. Clone the repository:
```bash
git clone https://github.com/igor-heslenji270/DEDIS-Project.git
cd DEDIS-Project
```

2. Create and activate virtual environment:

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install fastapi uvicorn streamlit sqlalchemy pydantic
```

## Running the Application

The application requires two terminals running simultaneously:

**Terminal 1 - Start the Backend API:**
```bash
uvicorn app.api:app --reload
```

The API will be available at `http://127.0.0.1:8000`
- API Documentation: `http://127.0.0.1:8000/docs`

**Terminal 2 - Start the Frontend:**
```bash
streamlit run app/main.py
```

The application will open in your browser at `http://localhost:8501`

## Usage

1. **Register**: Create a new account with username and password
2. **Login**: Authenticate with your credentials
3. **Add Samples**: Navigate to "Add Sample" tab and input microbiome data
4. **View Samples**: See all your samples in "My Samples" tab
5. **Search**: Use "Search" tab to find samples with different strategies


## API Endpoints

- `POST /users/` - Register new user
- `POST /login` - Authenticate user
- `POST /samples/` - Create sample
- `GET /samples/user/{user_id}` - Get user's samples
- `DELETE /samples/{sample_id}` - Delete sample
- `GET /search/exact` - Exact match search
- `GET /search/approximate` - Approximate match search
- `GET /search/hierarchical` - Hierarchical search
- `GET /search/abundance` - Abundance filter search

## Security

- Passwords are hashed using SHA-256 with unique salts
- Users can only access and modify their own samples
- Session-based authentication in Streamlit


## Author

Igor Heslenji, 89252108

## Acknowledgments

- FastAPI framework by Sebastián Ramírez
- Streamlit for rapid prototyping
- SQLAlchemy for ORM capabilities