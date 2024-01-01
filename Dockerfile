FROM python:latest
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app", "--workers", "2"]
