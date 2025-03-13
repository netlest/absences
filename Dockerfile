FROM python:3.12-slim
RUN apt-get update && apt-get dist-upgrade -y
RUN apt-get install vim -y
RUN useradd absences
WORKDIR /home/absences
COPY app app
COPY *.py ./
COPY *.sh ./
COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn
RUN mkdir -p instance/logs
RUN mkdir -p instance/migrations
RUN chown -R absences:absences ./
RUN chmod 755 run_absences.sh
USER absences
EXPOSE 8000
ENTRYPOINT ["./run_absences.sh", "prod"]
