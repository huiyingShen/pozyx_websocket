from pysinewave import SineWave
import simpleaudio as sa
from time import time,sleep
import threading

class AudioPlayer:
    def __init__(self):
        self.sineWave = SineWave(pitch = 12, pitch_per_second = 100)
        self.wave_obj = sa.WaveObject.from_wave_file("Knocking-on-door.wav")
        self.cases = "beep","knock","silent"
        self.freq = 500
        self.case = "silent"

    def knock(self,n=1):
        for _ in range(n):
            self.wave_obj.play().wait_done()

    def beep(self,freq,t=0.01):
        self.sineWave.set_frequency(freq)
        self.sineWave.play()
        sleep(t)

    def loop(self):
        while True:
            if not (self.case in self.cases): break
            if self.case == self.cases[0]: 
                self.beep(self.freq,0.01)
            elif self.case == self.cases[1]: 
                self.sineWave.stop()
                self.knock(1)
            else: 
                self.sineWave.stop()
                sleep(0.01)
                
    def go(self):
        threading.Thread(target=self.loop).start()

    def test1(self):
        self.case = self.cases[0]
        threading.Thread(target=self.loop).start()
        sleep(1)
        self.freq *= 0.8
        sleep(1)
        self.case = self.cases[1]
        sleep(3)
        self.case = self.cases[2]
        sleep(5)
        self.case = self.cases[0]
        sleep(1)
        self.case = 'q'

    def test0(self):
        self.knock(2)
        f = 500
        for _ in range(10):
            f *= 0.8
            self.beep(f,0.1)

def test1():
    # Create a sine wave, with a starting pitch of 12, and a pitch change speed of 10/second.
    sinewave = SineWave(pitch = 12, pitch_per_second = 10)

    # Turn the sine wave on.
    sinewave.play()

    # Sleep for 2 seconds, as the sinewave keeps playing.
    sleep(2)

    # Set the goal pitch to -5.
    sinewave.set_pitch(-5)

    # Sleep for 3 seconds, as the sinewave smoothly slides its pitch down from 12 to -5, and stays there.
    sleep(3)

def test2():
    wave_obj = sa.WaveObject.from_wave_file("Knocking-on-door.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()

if __name__ == "__main__":
    # test1()
    # test2()
    AudioPlayer().test1()