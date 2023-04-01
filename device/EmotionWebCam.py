from labplatform.core import DeviceSetting
from labplatform.core import Device
from fer import FER
import matplotlib.pyplot as plt
import numpy as np
from traits.api import Str, Bool, Int, Any, Tuple
import cv2 as cv

class EmotionWebCamSetting(DeviceSetting):
    device_name = Str("EmotionWebCam", group="status", dsec="Name of the camera")
    dtype = Any(np.uint8, group="status", dsec="Type of the data")
    type = Str("Image", group="status", dsec="Nature of the signal")
    shape = Tuple((480, 640, 4), group="status", dsec="Image shape")
    sampling_freq = Int(group="status", dsec="Sampling frequency of video")

class EmotionWebCam(Device):
    setting = EmotionWebCamSetting()
    emo_detector = FER(mtcnn=True)
    cap = Any()

    def _initialize(self):
        self.cap = cv.VideoCapture(0)

    def _configure(self):
        pass

    def _start(self):
        pass

    def _pause(self):
        pass

    def _stop(self):
        self.cap.release()

    def snapshot(self):
        frame = self.get_frame()
        # rgb = cv.cvtColor(frame, cv.COLOR_BGR2BGRA)
        plt.imshow(frame)
        plt.show()

    def get_frame(self):
        ret, frame = self.cap.read()
        return frame

    def show_video(self):
        if not self.cap.isOpened():
            print("Cannot open camera")
            exit()
        while True:
            # Capture frame-by-frame
            ret, frame = self.cap.read()
            # if frame is read correctly ret is True
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            # Our operations on the frame come here
            # gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            # Display the resulting frame
            cv.imshow('frame', frame)
            if cv.waitKey(1) == ord('q'):
                break
        # When everything done, release the capture
        cv.destroyAllWindows()

    def detect_emotions(self, show_image=True):
        img_array = self.get_frame()
        captured_emotions = self.emo_detector.detect_emotions(img_array)
        if show_image:
            plt.imshow(img_array)
            plt.show()
        return captured_emotions

    def get_top_emotion(self, show_image=True):
        img_array = self.get_frame()
        dominant_emotion, emotion_score = self.emo_detector.top_emotion(img_array)
        if show_image:
            plt.imshow(img_array)
            plt.show()
        return dominant_emotion, emotion_score

    def thread_func(self):
        if self.experiment:
            if self.experiment().trial_stop == True:
                self.experiment().process_event({'trial_stop': 0})



if __name__ == "__main__":
    cam = EmotionWebCam()
    cam.initialize()
    cam.detect_emotions()
    cam.get_top_emotion()
    cam.show_video()
    cam.stop()