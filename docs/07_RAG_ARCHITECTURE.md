# RAG Architecture
## Purpose
RAG is used for the HR Policy Chatbot.  
The LLM must answer from company documents, not from memory.
## Documents
Supported files: PDF and DOCX.  
Examples: leave policy, code of conduct, payroll rules, onboarding guide, benefits policy.
## Ingestion Flow
Upload file → validate file → extract text → clean text → split into chunks → create embeddings → store in pgvector
## Chunking
Chunk size: 500–800 characters.  
Overlap: 80–120 characters.  
Store metadata with every chunk: document name, page number, category, chunk id.
## Embeddings
Use NVIDIA `nvidia/nv-embed-v1`.  
Embed documents only when uploaded or updated.  
Do not re-embed unchanged documents.
## Retrieval Flow
User question → validate question → embed question → similarity search → get top chunks → build prompt → call LLM → return answer with sources
## Retrieval Rules
Retrieve top 3–5 chunks only.  
Never send full policy documents to LLM.  
Reject answers when context is weak.  
Show source document and page number.
## Prompt Rules
Wrap user question in delimiters.  
Wrap retrieved context in delimiters.  
Tell LLM to answer only from context.  
If answer is not in context, say HR should be contacted.
## Security
Scan questions for prompt injection.  
Never allow uploaded policy text to override system instructions.  
Do not expose internal file paths or vector IDs.
## Output
Answer, confidence level, source citations, and HR review flag.