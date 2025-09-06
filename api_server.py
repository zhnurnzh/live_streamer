from fastapi import FastAPI
import subprocess

app = FastAPI()

process = None

@app.post("/start")
def start_stream():
    global process
    if process:
        return {"message": "Stream is already running."}

    try:
       
        pipeline = (
            "gst-launch-1.0 dshowvideosrc ! "
            "videoconvert ! tee name=t ! queue ! autovideosink "
            "t. ! queue ! x264enc tune=zerolatency ! rtph264pay config-interval=1 pt=96 ! "
            "udpsink host=127.0.0.1 port=5000"
        )
        subprocess.check_call("gst-inspect-1.0 x264enc", shell=True)
    except subprocess.CalledProcessError:
        
        print("x264enc not available. Using vp8enc instead.")
        pipeline = (
            "gst-launch-1.0 dshowvideosrc ! "
            "videoconvert ! tee name=t ! queue ! autovideosink "
            "t. ! queue ! vp8enc deadline=1 ! rtpvp8pay pt=96 ! "
            "udpsink host=127.0.0.1 port=5000"
        )

    process = subprocess.Popen(pipeline, shell=True)
    return {"message": "Streaming started."}

@app.post("/stop")
def stop_stream():
    global process
    if process:
        process.terminate()
        process = None
        return {"message": "Streaming stopped."}
    return {"message": "No stream is currently running."}

@app.get("/status")
def get_status():
    return {"status": "streaming" if process else "not streaming"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
#controls the stream