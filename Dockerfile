FROM python:3.12.3-bullseye
	
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential
RUN pip install --upgrade pip
ADD requirements.txt /app/
RUN pip install -r requirements.txt

COPY ./ /app/

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["python", "-m", "streamlit", "run", "website/websitename.py", "--server.enableCORS=false","--server.enableXsrfProtection=false","--server.enableWebsocketCompression=true"]
