import os
import io
import sys
import json
import redis
import platform
import base64
import hashlib
import shutil
import subprocess
import requests
from minio import Minio

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = int(os.getenv("REDIS_PORT") or 6379)

minioHost = os.getenv("MINIO_HOST") or "localhost:9000" #minio address
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
client = Minio(minioHost, secure=False, access_key=minioUser, secret_key=minioPasswd)


infoKey = "{}.rest.info".format(platform.node())
debugKey = "{}.rest.debug".format(platform.node())
def log_debug(message, key=debugKey):
    print("DEBUG:", message, file=sys.stdout)
    redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
    redisClient.lpush('logging', f"{debugKey}:{message}")

def log_info(message, key=infoKey):
    print("INFO:", message, file=sys.stdout)
    redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
    redisClient.lpush('logging', f"{infoKey}:{message}")


def process(job): # pass in a dict
    mp3_song_hash = job["hash"]
    requested_model = job.get("model") or "htdemucs"

    if requested_model not in {"htdemucs", "htdemucs_ft", "hdemucs_mmi", "mdx", "mdx_extra", "mdx_q", "mdx_extra_q"}: # if an unknown model is passed, change it to default
        requested_model = "htdemucs"

    input_path = os.path.join("/tmp", f"{mp3_song_hash}.mp3")
    client.fget_object("queue", f"{mp3_song_hash}.mp3", input_path)
    log_debug(f"Downloaded {mp3_song_hash}.mp3")

    command = ["python3", "-m", "demucs.separate", "-n", requested_model, "--mp3", "--out", "/tmp/output", input_path]
    result = subprocess.run(command) # run the command

    



if __name__ == "__main__": 
