FROM python:3.11.6

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
