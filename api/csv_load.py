import csv
from .models import Content

with open('content.csv') as csvfile:
    print('csv opening?')
    '''
    reader = csv.DictReader(csvfile)
    for row in reader:
        # The header row values become your keys
        suite_name = row['SuiteName']
        test_case = row['Test Case']
        # etc....

        new_revo = Revo(SuiteName=suite_name, TestCase=test_case,...)
        new_revo.save()
    '''
