FROM python:3.10-slim
ENV DOWNLOAD_URL="https://download.acestream.media/linux/acestream_3.2.3_ubuntu_22.04_x86_64_py3.10.tar.gz"
WORKDIR /opt/acestream
RUN apt update ; apt install -yq wget && wget -qO- $DOWNLOAD_URL | tar xz ; \
    pip install -q --no-cache-dir -U -r requirements.txt ; 
EXPOSE 6878
ENTRYPOINT [ "/opt/acestream/start-engine" ]
CMD [ "--client-console","--bind-all" ]
HEALTHCHECK CMD wget -q -t1 -O- 'http://127.0.0.1:6878/webui/api/service?method=get_version' | grep '"error": null'