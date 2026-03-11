import pandas as pd

MODES = ('5K ONLY',
         '5K RUBY',
         '5K STANDARD',
         '7K STANDARD',
         '10K MANIAC',
         '14K MANIAC',
         '5K COURSE',
         '7K COURSE',
         '10K COURSE',
         '14K COURSE',
         'CATCH',
         'TURNTABLE')

DIFFICULTIES = ('NM MIX',
                'HD MIX',
                'SHD MIX',
                'EX MIX')

SCORE_VALUE_NAMES = ('total_notes',
                     'KOOL',
                     'COOL',
                     'GOOD',
                     'MISS',
                     'FAIL',
                     'rate',
                     'max_combo',
                     'score')

SCORE_VALUE_NAMES_CATCH = ('total_notes',
                           'CATCH',
                           'MISS',
                           'rate',
                           'max_combo',
                           'score')

SONGS = pd.read_csv('data/songs.csv')['title'].to_list()

SKULLS = (('Ctrl + Alt + Del', 'EX MIX', '5K STANDARD'),
          ('Moving On', 'SHD MIX', '7K STANDARD'),
          ('To My Love', 'SHD MIX', '7K STANDARD'),
          ('G.O.A', 'EX MIX', '14K MANIAC'),
          ('Revelation', 'EX MIX', '14K MANIAC'))