from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

# Camera setup
picamera = Picamera2()

video_config = picamera.create_video_configuration()
image_config = picamera.create_still_configuration()

# Video to file
def start_video(filepath):
    picamera.configure(video_config)
    picamera.set_controls({"ExposureValue": 0, "FrameRate": 18, "AwbEnable": False})

    encoder = H264Encoder(10000000)
    output = FfmpegOutput(filepath)

    picamera.start_recording(encoder, output)

def stop_video():
    picamera.stop_recording()

# Image as array
def get_image_2_array():
    picamera.configure(image_config)
    picamera.start(show_preview=False)

    image =  picamera.capture_array("main")

    picamera.stop()

    return image

# Image as file
def get_image_2_file(filepath):
    picamera.configure(image_config)
    picamera.start(show_preview=False)

    picamera.capture_file(filepath)

    picamera.stop()