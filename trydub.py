from pydub import AudioSegment
import simpleaudio
from threading import Thread
from time import sleep
import signal

class spawn_thread(Thread):
    def __init__(self, name, path_to_ost):
        Thread.__init__(self)
        self.name = name
        self.path_to_ost = path_to_ost
        self.running = False
        self.time_elapsed = 0
        self.forced_interrupt = False
        ''' TIME_CHECK defines how frequently it will control
        if the audio track has ended.
        The lower the value, the more precise it will cut the audio,
        but it will also be more CPU intensive. Use wisely or do not change. '''
        self.TIME_CHECK = 0.01

    def run(self):
        self.running = True
        self.play_audio()

        # self test
        is_playing = False
        while True:
            self.time_elapsed += (self.TIME_CHECK*1000)
            sleep(self.TIME_CHECK)
            is_playing = self.ost.is_playing()
            if not is_playing:
                self.play_audio()
            if self.forced_interrupt:
                print("INTERRUPT!")
                self.ost.stop()
                self.ost = AudioSegment.from_wav(self.path_to_ost)
                print(len(self.ost), self.time_elapsed)
                tts = len(self.ost)-self.time_elapsed+10 # Time To Skip
                temp_track = self.ost[-tts:] # <== DA SISTEMARE TIMING
                temp_track = temp_track[:1000]
                temp_track = temp_track.fade_out(1000)
                self.ost = simpleaudio.play_buffer(temp_track.raw_data,
                                            num_channels=temp_track.channels,
                                            bytes_per_sample=temp_track.sample_width,
                                            sample_rate=temp_track.frame_rate)
                self.ost.wait_done()
                self.running = False
                break
                
    def play_audio(self):
        self.time_elapsed = 0
        self.ost = AudioSegment.from_wav(self.path_to_ost)
        self.ost = simpleaudio.play_buffer(self.ost.raw_data,
                                            num_channels=self.ost.channels,
                                            bytes_per_sample=self.ost.sample_width,
                                            sample_rate=self.ost.frame_rate)

    def kill_with_fade_out(self, signum, frame):
        print(" - Killing...")
        self.forced_interrupt = True
    
#print("hi")

a = spawn_thread("hi", "soundtracks/death/start.wav")
a.start()
signal.signal(signal.SIGTSTP, a.kill_with_fade_out)

while 1:
    sleep(3)