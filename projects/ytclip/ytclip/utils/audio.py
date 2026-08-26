import parselmouth
from IPython.display import Audio

def display_audio(snd: parselmouth.Sound):
    return Audio(snd.values.T.flatten(), rate=snd.sampling_frequency, normalize=False)