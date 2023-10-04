import curses
import simpleaudio as audio
from salieri import AudioPlayer, audio_manager
from sheets import papers
from multiprocessing import Process, Queue
from time import sleep

# Will enable messaging
queue = Queue()

key_for_start = ord('s')
key_for_pause = ord('p')
key_for_force_stop = ord('f')
key_for_end = ord('e')
key_for_quit = ord('q')
key_up = curses.KEY_UP
key_down = curses.KEY_DOWN

# max y = curses.LINES
# max x = curses.COLS

def main(konsole):
    # Run
    run = True
    key = -1
    stop_audio = False
    start_audio = 0
    loop_audio = 0
    music_pointer = 0

    # Establishing connection with salieri
    p_salieri = Process(target=audio_manager, args=(queue,))
    p_salieri.start()

    # megu_death = AudioPlayer(audio.WaveObject.from_wave_file(path_to_ost+'start.wav'), audio.WaveObject.from_wave_file(path_to_ost+'loop.wav'), audio.WaveObject.from_wave_file(path_to_ost+'end.wav'))

    looped_song = None
    while run:
        konsole = curses.initscr()
        konsole.clear()
        #curses.cbreak()

        # Print to screen
        konsole.addstr(papers.operas[music_pointer].get('default_name')+str(music_pointer))

        # Obtain input
        key = konsole.getch()

        if key == key_for_quit:
            run = False


        # My code here:

        if key == key_for_start:
            queue.put(['1', music_pointer])
        
        if key == key_for_end:
            queue.put('2')
        
        if key == key_for_force_stop:
            queue.put('3')
        
        if key == key_for_pause:
            queue.put('5')

        if key == key_up:
            if music_pointer < len(papers.operas)-1:
                music_pointer += 1
        if key == key_down:
            if music_pointer != 0:
                music_pointer -= 1

        konsole.refresh()
    p_salieri.terminate()
    sleep(1)
    p_salieri.kill()
    exit(0)


if __name__ == '__main__':
    print("Executed as main")
    curses.wrapper(main)
    exit(0)
