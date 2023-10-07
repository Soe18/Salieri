import curses
import simpleaudio as audio
from salieri import AudioPlayer, audio_manager, sig_manager
from sheets import papers
from multiprocessing import Process, Queue
from time import sleep

# Will enable messaging
queue = Queue()

key_for_start = (ord('s'), ord('S'))
key_for_pause = (ord('p'), ord('P'))
key_for_force_stop = (ord('f'), ord('F'))
key_for_end = (ord('e'), ord('E'))
key_for_quit = (ord('q'), ord('Q'))
key_up = curses.KEY_UP
key_down = curses.KEY_DOWN

# max y = curses.LINES
# max x = curses.COLS

MARGIN_TOP = 6
MARGIN_BOTTOM = 5
MARGIN_LEFT = 3
MARGIN_RIGHT = 3

def main(konsole):
    # Curses setup
    curses.curs_set(0)
    if curses.has_colors():
        curses.use_default_colors()

    # Run
    run = True
    key = -1
    stop_audio = False
    start_audio = 0
    loop_audio = 0
    music_pointer = 0
    music_pointer_fallback = -1

    # Establishing connection with salieri
    p_salieri = Process(target=audio_manager, args=(queue,))
    p_salieri.start()

    # megu_death = AudioPlayer(audio.WaveObject.from_wave_file(path_to_ost+'start.wav'), audio.WaveObject.from_wave_file(path_to_ost+'loop.wav'), audio.WaveObject.from_wave_file(path_to_ost+'end.wav'))

    # Get max rows and cols
    MAX_DIM = konsole.getmaxyx()
    music_list = curses.newpad(len(papers.operas),MAX_DIM[1])

    looped_song = None
    while run:
        konsole = curses.initscr()
        #curses.cbreak()

        MAX_DIM = konsole.getmaxyx()

        # Printing default UI
        keybinds_guideline = 'Keybinds: '
        for inst_key in ('Start','Pause','End','Force Stop','Quit'):
            keybinds_guideline += ' '+inst_key[0]+' - '+inst_key+'; '

        keybinds_x_spacing = 0
        if MAX_DIM[1] > len(keybinds_guideline):
            keybinds_x_spacing = (MAX_DIM[1]-len(keybinds_guideline))//2
        konsole.addstr(1,keybinds_x_spacing,keybinds_guideline)

        # Now playing
        curr_string = 'Now playing: '
        if music_pointer_fallback == -1:
            curr_string += 'None'
        else:
            curr_string = format_curr_string(curr_string + papers.operas[music_pointer_fallback].get('default_name'), MAX_DIM[1], MARGIN_LEFT + MARGIN_RIGHT)
        konsole.addstr(MAX_DIM[0]-3,0,curr_string)

        # Status
        konsole.addstr(MAX_DIM[0]-2,0,'Status: '+sig_manager.get_status())

        # Print main screen
        for index in range(len(papers.operas)):
            if index == music_pointer:
                arg = curses.A_STANDOUT
            else:
                arg = 0
            curr_string = format_curr_string(str(index)+" - "+papers.operas[index].get('default_name'), MAX_DIM[1], MARGIN_LEFT + MARGIN_RIGHT)
            music_list.addstr(index, 0, curr_string, arg)

#MAX_DIM[1]-MARGIN_RIGHT
        music_list.refresh(music_pointer,0,MARGIN_TOP,MARGIN_LEFT,MAX_DIM[0]-MARGIN_BOTTOM,MAX_DIM[1]-MARGIN_RIGHT)
        # Obtain input
        key = konsole.getch()

        if key in key_for_quit:
            run = False
            konsole.clear()
            konsole.addstr(0,0,'Made by Fabiano Da Pozzo')


        # My code here:

        if key in key_for_start:
            queue.put(['1', music_pointer])
            music_pointer_fallback = music_pointer
        
        if key in key_for_end:
            queue.put('2')
        
        if key in key_for_force_stop:
            queue.put('3')
            music_pointer_fallback = -1
        
        if key in key_for_pause:
            queue.put('5')

        if key == key_down:
            if music_pointer < len(papers.operas)-1:
                music_pointer += 1
        if key == key_up:
            if music_pointer != 0:
                music_pointer -= 1

        konsole.refresh()
        konsole.clear()
    p_salieri.terminate()
    sleep(1)
    p_salieri.kill()
    exit(0)

def format_curr_string(curr_string, MAX_X, bb):
    if len(curr_string) > (MAX_X - bb):
        curr_string = curr_string[:MAX_X-bb-3] + '...'
    return curr_string


if __name__ == '__main__':
    print("Executed as main")
    curses.wrapper(main)
    exit(0)
