# 1️⃣ Use official Python image (with 3.10 and slimmed-down OS)
FROM python:3.10-slim

# 2️⃣ Set the working directory inside the container to /app
WORKDIR /app

# 3️⃣ Copy your current project files into /app inside the container
COPY . .

# 4️⃣ Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Install uvicorn (not always needed but safer for FastAPI)
RUN pip install uvicorn

# 6️⃣ Final command: start FastAPI backend AND Streamlit frontend together
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run chatbot_ui.py --server.port 8501 --server.enableCORS false"]
