'''
    a testing case, operation on the FooDevice
    Copied from Chao Huang, https://github.com/sandriver03
'''

from labplatform.core.ExperimentLogic import ExperimentLogic
from labplatform.core.Setting import ExperimentSetting
from labplatform.core.Data import ExperimentData
from labplatform.core import Subject
from labplatform.config import get_config

from device.FooDevice import FooDevice

from traits.api import List, Float, Property, Int
import random
import time
import os
import slab

import logging

log = logging.getLogger(__name__)


class FooExperimentSetting(ExperimentSetting):
    experiment_name = 'FooExp'
    mu_sequence = List([1, 1], group='primary', context=False, dsec='different means of the Gaussian to run')
    trial_duration = 5
    trial_number = 5

    total_trial = Property(Int(), group='status', depends_on=['trial_number', 'mu_sequence'],
                           dsec='Total number of trials')

    def _get_total_trial(self):
        return self.trial_number * len(self.mu_sequence)


class FooExperiment(ExperimentLogic):
    setting = FooExperimentSetting()
    data = ExperimentData()
    results = slab.ResultsFile(folder=get_config("DATA_ROOT"))
    time_0 = Float()

    def _devices_default(self):
        fd = FooDevice()
        fd.setting.device_ID = 0
        return {'FooDevice': fd}

    def _initialize(self, **kwargs):
        pass

    # internal temporal parameter
    mu_list = List()

    def setup_experiment(self, info=None):
        self.mu_list = []
        for k in self.setting.mu_sequence:
            self.mu_list.extend([k]*self.setting.trial_number)
        # randomize the sequence
        random.shuffle(self.mu_list)
        # save the sequence
        self.results.write(self.setting.trial_number, 'trial_number')

        # setup correct data_length in FooDevice
        data_length = self.devices['FooDevice'].setting.sampling_freq * self.setting.trial_duration
        self.results.write(data_length, "data_length")
        self.devices['FooDevice'].configure(data_length=data_length)
        self.time_0 = time.time()

    def _start_trial(self):
        self.devices['FooDevice'].configure(mu=self.mu_list[self.setting.current_trial])
        self.devices['FooDevice'].start()
        log.info('trial {} start: {}'.format(self.setting.current_trial, time.time() - self.time_0))
        self.time_0 = time.time()

    def _stop_trial(self):
        self.results.write(self.setting.current_trial, "trial")
        self.results.write(time.time() - self.time_0, "trial_duration")
        self.results.write(self.devices["FooDevice"]._output_specs["response"], "FooDevice_response")
        log.info('trial {} end: {}'.format(self.setting.current_trial, time.time() - self.time_0))
        self.time_0 = time.time()

    def _stop(self):
        pass

    def _pause(self):
        pass


if __name__ == '__main__':
    import logging

    log = logging.getLogger()
    log.setLevel(logging.INFO)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    log.addHandler(ch)

    # cohort = load_cohort('example')
    try:
        subject = Subject(name="Foo", group="Pilot", species="Human", cohort="Pilot", sex="M")
        subject.add_subject_to_h5file(file=os.path.join(get_config("SUBJECT_ROOT"), "Foo_Test.h5"))
    except ValueError:
        # read the subject information
        subject = Subject(name="Foo", group="Pilot", species="Human", cohort="Pilot", sex="M")
        subject.read_info_from_h5file(file=os.path.join(get_config("SUBJECT_ROOT"), "Foo_Test.h5"))

    fe = FooExperiment(subject=subject)
    fd = fe.devices['FooDevice']

    # current parameters can be viewed
    fe.setting.get_parameter_value()
    # parameters can be changed
    # parameter change should only be done through the .configure method
    # fe.configure(mu_sequence=[0, 0.1])
    # start the experiment
    fe.start()

