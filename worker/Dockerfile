# prebuilt dmucs image
FROM xserrat/facebook-demucs:latest

# run this command
RUN python3 -m pip install --no-cache-dir minio redis requests

# put worker code in /srv
WORKDIR /srv
COPY worker-server.py /srv/

# start with running the worker, instead of the default
ENTRYPOINT ["python3", "-u", "/srv/worker-server.py"]