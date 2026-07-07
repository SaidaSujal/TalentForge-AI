# Tech Stack
## Core
Backend: FastAPI  
Frontend: HTML, CSS, JavaScript, Jinja2 templates  
Database: PostgreSQL on Neon  
Vector DB: pgvector first, Qdrant optional later  
AI Provider: NVIDIA NIM  
LLM Framework: LangChain  
ML/Data: Pandas, NumPy, Scikit-learn  
File Parsing: PyPDF2, python-docx  
Charts: Chart.js or Plotly.js  
Deployment: Render/Railway for backend, Neon for DB
## Backend
Use FastAPI only. Do not use Flask or Streamlit.  
Use Pydantic v2 for request validation.  
Use SQLAlchemy 2.x for database access.  
Use Alembic for migrations.
## AI Models
Small tasks: `meta/llama-3.1-8b-instruct`  
Complex HR reasoning: `meta/llama-3.1-70b-instruct`  
Advanced admin reasoning: `nvidia/llama-3.3-nemotron-super-49b-v1.5`  
Embeddings: `nvidia/nv-embed-v1`
## RAG
Use NVIDIA embeddings to embed policy chunks.  
Store vectors in PostgreSQL pgvector.  
Retrieve top relevant chunks only.  
Never send full documents to LLM.
## Security Libraries
Use python-dotenv for environment variables.  
Use passlib/bcrypt for passwords.  
Use python-jose for JWT.  
Use slowapi or custom Redis rate limiter.
## Rules
No hardcoded secrets.  
No raw user input to LLM.  
Use Pandas before LLM.  
Cache all repeated AI outputs.  
Use small model by default, large model only when required.