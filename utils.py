from glob import glob
import os

def removeFiles(filepath: str, thresholdpath: str) -> bool:
    status = False
    try:
        files = glob(f"{filepath}/*")
        for file in files:
            os.remove(file)

        thresholds = glob(f"{thresholdpath}/*")
        for thres in thresholds:
            os.remove(thres)
        status = True
    except Exception as e:
        status = False
        print("ERROR == ", e)
        
    return status
    