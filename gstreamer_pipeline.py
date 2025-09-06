
import subprocess

process = None

def start_gstreamer():
    global process
   
    try:
        pipeline = (
            "gst-launch-1.0 dshowvideosrc ! "
            "videoconvert ! tee name=t ! queue ! autovideosink "
            "t. ! queue ! x264enc tune=zerolatency ! rtph264pay config-interval=1 pt=96 ! "
            "udpsink host=127.0.0.1 port=5000"
        )
       
        subprocess.check_call("gst-inspect-1.0 x264enc", shell=True)
    except subprocess.CalledProcessError:
        print("x264enc not available. Falling back to vp8enc.")
        pipeline = (
            "gst-launch-1.0 dshowvideosrc ! "
            "videoconvert ! tee name=t ! queue ! autovideosink "
            "t. ! queue ! vp8enc deadline=1 ! rtpvp8pay pt=96 ! "
            "udpsink host=127.0.0.1 port=5000"
        )

    process = subprocess.Popen(pipeline, shell=True)
    print("GStreamer started. Video is displayed locally and streaming to UDP.")

def stop_gstreamer():
    global process
    if process:
        process.terminate()
        process = None
        print("GStreamer stopped.")

if __name__ == "__main__":
    start_gstreamer()
    input("Press Enter to stop the GStreamer pipeline...")
    stop_gstreamer()
# proper video stream capture 