# Documentation and setup of the model was taken from here!
# https://ai.google.dev/edge/mediapipe/solutions/customization/gesture_recognizer

from google.colab import files
import os
import tensorflow as tf
assert tf.__version__.startswith('2')

from mediapipe_model_maker import gesture_recognizer

import matplotlib.pyplot as plt