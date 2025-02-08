FROM python:latest
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 7000
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
