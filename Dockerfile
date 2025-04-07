FROM python:3.13-slim
RUN mkdir "/app"
WORKDIR "/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt update
RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
EXPOSE 8000
CMD ["bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]


