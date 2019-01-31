import re
import subprocess

def convert_to_seconds(time_in_words):
    secs = 0

    def to_secs(s):
        mat = re.match(r"((?P<hours>\d+)\s?hour)?\s?((?P<minutes>\d+)\s?min)?\s?((?P<seconds>\d+)\s?sec)?", s)
        secs = 0
        secs += int(mat.group("hours")) * 3600 if mat.group("hours") else 0
        secs += int(mat.group("minutes")) * 60 if mat.group("minutes") else 0
        secs += int(mat.group("seconds")) if mat.group("seconds") else 0
        return secs

    for s in time_in_words.split(','):
        secs = secs + to_secs(s)
    return secs


def convert_bandwidth(bandwidth):
    download, upload = 0.0, 0.0

    def to_bytes(num, type):
        try:
            if 'KiB' in type:
                return num * 1024.0
            elif 'MiB' in type:
                return num * 1024.0 * 1024
            elif 'GiB' in type:
                return num * 1024.0 * 1024 * 1024
            else:
                return num
        except TypeError as e:
            print("The following exception has occured : {}".format(e))
            return None

    for s in bandwidth.split(','):
        if 'received' in s:
            a = s.replace('received', '').strip().split(' ')
            upload = to_bytes(float(a[0]), str(a[1]))
            if not upload:
                return None,"Exception raised"
        elif 'sent' in s:
            a = s.replace('sent', '').strip().split(' ')
            download = to_bytes(float(a[0]), str(a[1]))
            if not download:
                return None,"Exception raised"
    return {
        'download': download,
        'upload': upload
    },None

