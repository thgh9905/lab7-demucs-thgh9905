import os
import io
import sys
import json
import redis
import platform
import base64
import hashlib
from minio import Minio

from flask import Flask, jsonify, request

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = int(os.getenv("REDIS_PORT") or 6379)

minioHost = os.getenv("MINIO_HOST") or "localhost:9000" #minio address
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
client = Minio(minioHost, secure=False, access_key=minioUser, secret_key=minioPasswd)

for bucket in ["queue", "output"]:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

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

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "<h1>Music Separation Server</h1><p>Use a valid endpoint</p>" # send back an HTML page


@app.route("/apiv1/queue", methods=["GET"], strict_slashes=False)
def queue():
    list_entries = redisClient.lrange("toWorker", 0, -1) #read every entry in the toWorker list from start (0) to end (-1)
    hashes = []
    for entry in list_entries: # go through each job
        job = json.loads(entry) #convert the jobs from json to dictionaries
        hashes.append(job["hash"]) #put the song's hash into the song hashes list
    log_debug(f"Queue has {len(hashes)} entries")
    return jsonify({"queue": hashes}) # reply

@app.route("/apiv1/separate", methods=["POST"], strict_slashes=False)
def separate():
    request_json = request.get_json(silent = True)
    if not request_json or "mp3" not in request_json: # Look for requests that aren't a json or doesn't have an "mp3" field
        log_info()
        return jsonify({"error": "Request must be JSON with a base64 'mp3' field"})
    decoded_mp3_bytes = base64.b64decode(request_json["mp3"])
    mp3_song_hash = hashlib.sha224(decoded_mp3_bytes).hexidigest()
    client.put_object("queue", f"{mp3_song_hash}.mp3", io.BytesIO(decoded_mp3_bytes), length=len(decoded_mp3_bytes), content_type="audio/mpeg")
    log_debug()
    job = {"hash": mp3_song_hash, "model": request_json.get("model"), "callback": request_json.get("callback")}
    redisClient.lpush("toWorker", json.dumps(job))
    log_info()
    return jsonify({"hash": mp3_song_hash, "reason": "Song enqueued for separation"})

if __name__ == "__main__": 
    log_info(f"Starting REST server. Redis is at {redisHost}:{redisPort}")
    app.run(host="0.0.0.0", port=5000, debug=True) 
    

        