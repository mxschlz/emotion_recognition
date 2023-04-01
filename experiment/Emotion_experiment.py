from device.EmotionWebCam import EmotionWebCam
from labplatform.core import ExperimentSetting
from labplatform.core import ExperimentLogic
from labplatform.core import ExperimentData
from labplatform.core import load_cohort
import slab
import random
from experiment import config as cfg
from traits.api import Bool, Int, List, Str, Any


class EmotionDetectionExperimentSetting(ExperimentSetting):
    experiment_name = Str("EmotionDetection")
    emotions = List(["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"])
    conditions = Int(cfg.conditions)
    trial_number = Int(cfg.n_reps)
    total_trial = trial_number
    show_image = Bool(False)


class EmotionDetectionExperiment(ExperimentLogic):
    setting = EmotionDetectionExperimentSetting()
    data = ExperimentData()
    sequence = slab.Trialsequence(conditions=setting.conditions, n_reps=setting.trial_number)
    trial_success = slab.Sound.tone()
    emotion_to_detect = Any()
    trial_stop = Bool(False)
    results = slab.ResultsFile()

    def _devices_default(self):
        return {"cam": EmotionWebCam()}

    def _initialize(self):
        pass

    def setup_experiment(self, info=None):
        pass

    def prepare_trial(self):
        self.trial_stop = False
        self.sequence.__next__()
        self.emotion_to_detect = random.choices(self.setting.emotions)
        self.results.write(self.emotion_to_detect, "emotion_to_detect")

    def start_trial(self):
        self.devices["cam"].start()
        print(f"Please express following emotion: {self.emotion_to_detect[0]}")
        while True:
            dominant_emotion, emotion_score = self.devices["cam"].get_top_emotion(show_image=self.setting.show_image)
            if dominant_emotion == self.emotion_to_detect[0]:
                print(f"Emotion expression successful! Emotion score: {emotion_score}")
                self.results.write(emotion_score, "emotion_score")
                self.trial_success.play()
                self.trial_stop = True
                break
            else:
                print("Desired emotion not expressed, please try changing your expression.", end="\r", flush=True)

    def stop_trial(self):
        self.devices["cam"].pause()

    def _start(self):
        pass

    def _pause(self):
        pass

    def _stop(self):
        print("Experiment done!")


if __name__ == "__main__":
    cohort = load_cohort("example")
    subject = cohort.subjects[0]
    exp = EmotionDetectionExperiment(subject=subject)
    exp.configure(show_image=True)
    # exp.start()

