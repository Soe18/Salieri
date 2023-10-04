from pydub import AudioSegment
import simpleaudio
from threading import Thread
from time import sleep
import signal
from multiprocessing import Process, Queue
from sheets import papers

''' Code messages:
1 ==> Start
2 ==> End loop
3 ==> Fast finish
4 ==> Hard finish
5 ==> Pause

'''

FOR_PAUSE = 0
FOR_END = 1

class AudioPlayer(Thread):
    global FOR_PAUSE
    global FOR_END
    def __init__(self, opera):
        Thread.__init__(self)
        if opera != None:
            self.opera = opera
            if self.opera.get('has_start'):
                self.running = 'intro'
                self.path_to_ost = 'soundtracks/'+self.opera.get('dir')+'/start.wav'
            else:
                self.running = 'loop'
                self.path_to_ost = 'soundtracks/'+self.opera.get('dir')+'/loop.wav'
            self.time_elapsed = 0
            self.forced_interrupt = False
            ''' TIME_CHECK defines how frequently it will control
            if the audio track has ended.
            The lower the value, the more precise it will cut the audio,
            but it will also be more CPU intensive. Use wisely or do not change. '''
            self.TIME_CHECK = 0.01
            self.status_fallback = ['intro','no_end']

    def run(self):
        self.play_audio()

        # self test
        is_playing = False
        while True:
            if self.running == 'pause':
                self.ost.stop()
                while self.running == 'pause':
                    sleep(0.25)
                self.play_audio(tts=self.time_elapsed)
            self.time_elapsed += (self.TIME_CHECK*1000)
            sleep(self.TIME_CHECK)
            is_playing = self.ost.is_playing()
            if not is_playing:
                if self.running == 'intro':
                    self.time_elapsed = 0
                    self.running = 'loop'
                    self.path_to_ost = 'soundtracks/'+self.opera.get('dir')+'/loop.wav'
                elif self.running == 'approach_to_end' and self.opera.get(has_end):
                    self.running = 'end'
                    self.path_to_ost = 'soundtracks/'+self.opera.get('dir')+'/end.wav'
                elif self.running == 'end':
                    exit(0)
                self.play_audio()
            if self.forced_interrupt:
                # print('Interrupt')
                self.ost.stop()
                self.play_audio(tts=self.time_elapsed, fade_out='kill')
                self.ost.wait_done()
                self.running = 'interrupted'
                exit(0)
    
    ''' tts ==> time to skip, will skip the time spent
        fade_out ==> if set, determines a fade out:
                        'kill' ==> kills with the fade
                        anything except False wont kill with fade '''
    def play_audio(self, tts=False, fade_out=False):
        self.ost = AudioSegment.from_wav(self.path_to_ost)
        if tts:
            self.ost = self.ost[tts:]
        if fade_out:
            if fade_out == 'kill':
                self.ost = self.ost[:1000]
            self.ost = self.ost.fade_out(1000)
        if not tts and fade_out:
            self.time_elapsed = 0
        self.ost = simpleaudio.play_buffer(self.ost.raw_data,
                                            num_channels=self.ost.channels,
                                            bytes_per_sample=self.ost.sample_width,
                                            sample_rate=self.ost.frame_rate)

    def kill_with_fade_out(self):
        self.forced_interrupt = True
    
    # I hate this func, better reorganize it, isn't it?
    def stop(self):
        if self.running == 'pause':
            if self.status_fallback != 'approach_to_end':
                self.status_fallback[FOR_PAUSE] = 'approach_to_end'
                self.status_fallback[FOR_END] = self.status_fallback[FOR_PAUSE]
            else:
                self.status_fallback[FOR_PAUSE] = self.status_fallback[FOR_END]
                self.status_fallback[FOR_END] = 'no_end'
        elif self.running != 'intro' or self.status_fallback != 'intro':
            if self.running != 'approach_to_end':
                self.running = 'approach_to_end'
                self.status_fallback[FOR_END] = self.running
            else:
                self.running = self.status_fallback[FOR_END]
                self.status_fallback[FOR_END] = 'no_end'
        

    def pause(self):
        if self.running != 'pause':
            self.status_fallback[FOR_PAUSE] = self.running
            self.running = 'pause'
        else:
            self.running = self.status_fallback[FOR_PAUSE]

#print("hi")

#a = AudioPlayer("hi", "soundtracks/death/start.wav")
#a.start()
#signal.signal(signal.SIGTSTP, a.kill_with_fade_out)

def audio_manager(queue):
    sig_manager = Signal_Manager()
    signal.signal(signal.SIGTERM, sig_manager.recall)
    sound_to_play = None
    while True:
        message = queue.get()
        sleep(0.05)
        if message[0] == '1' and (not sound_to_play):
            sound_to_play = AudioPlayer(papers.operas[message[1]])
            sig_manager.update(sound_to_play)
            sound_to_play.start()
        elif message == '2':
            if sound_to_play:
                sound_to_play.stop()
                sound_to_play = None
        elif message == '3':
            if sound_to_play:
                sound_to_play.kill_with_fade_out()
                sound_to_play = None
        elif message == '5':
            if sound_to_play:
                sound_to_play.pause()

class Signal_Manager():
    def __init__(self):
        self.current_obj_playing = None
    
    def update(self, obj_music):
        self.current_obj_playing = obj_music
    
    def recall(self, signum, frame):
        self.current_obj_playing.kill_with_fade_out()