# Python 3.12.3 on Debian Bullseye available on 26 Sep 2025
FROM python:3.12.3-bullseye@sha256:9b7b707f0d9faab8544b815c9b4b5f73cab5a33753cf2ea99110fe4ab30e1d9c
	
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential
RUN pip install --upgrade pip
ADD web_application/requirements.txt /app/
RUN pip install --timeout=6000 -r requirements.txt

COPY ./web_application /app/

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["python", "-m", "streamlit", "run", "website/fluhunter_web.py", "--server.enableCORS=false","--server.enableXsrfProtection=false","--server.enableWebsocketCompression=true"]
