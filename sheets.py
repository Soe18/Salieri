import os, glob

class Papers():
    def __init__(self):
        # Read files
        os.chdir('soundtracks/')
        dirs = glob.glob('*' + os.path.sep)

        self.operas = []

        for dir in dirs:
            name_dir = dir[:-1]
            opera = {
                'default_name':name_dir,
                'dir':name_dir,
                'has_start':False,
                'has_end':False,
            }
            os.chdir(dir)
            read = glob.glob('*')
            if 'loop.wav' in read:    
                if 'start.wav' in read:
                    opera['has_start'] = True
                if 'end.wav' in read:
                    opera['has_end'] = True
                self.operas.append(opera)
            os.chdir('..')
        os.chdir('..')

papers = Papers()
