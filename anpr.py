from skimage.measure import regionprops
from skimage.transform import resize
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from skimage import measure
from model import model
import numpy as np
import cv2

def licensePlateRecognition(plate_num_img):
    imgread = cv2.imread(plate_num_img)
    gray_img = cv2.cvtColor(imgread, cv2.COLOR_BGR2GRAY) 
    ret, thresh1 = cv2.threshold(gray_img, 120, 255, cv2.THRESH_BINARY)

    # The invert was done so as to convert the black pixel to white pixel and vice versa
    license_plate = np.invert(thresh1)

    labelled_plate = measure.label(license_plate)
    
    fig, ax1 = plt.subplots(1)
    plt.xticks([]), plt.yticks([])
    ax1.imshow(license_plate, cmap="gray")

    # Dimension of the plate number
    character_dimensions = (0.30*license_plate.shape[0], 0.60*license_plate.shape[0], 0.05*license_plate.shape[1], 0.15*license_plate.shape[1])
    min_height, max_height, min_width, max_width = character_dimensions

    characters = []
    counter=0
    column_list = []
    for regions in regionprops(labelled_plate):
        y0, x0, y1, x1 = regions.bbox
        region_height = y1 - y0
        region_width = x1 - x0

        if region_height > min_height and region_height < max_height and region_width > min_width and region_width < max_width:
            roi = license_plate[y0:y1, x0:x1]

            # draw a red bordered rectangle over the character.
            rect_border = patches.Rectangle((x0, y0), x1 - x0, y1 - y0, edgecolor="red", linewidth=2, fill=False)
            ax1.add_patch(rect_border)

            # resize the characters to 20X20 and then append each character into the characters list
            resized_char = resize(roi, (20, 20))
            characters.append(resized_char)

            # this is just to keep track of the arrangement of the characters
            column_list.append(x0)

    # ts = f"{datetime.timestamp(datetime.now())}".split(".")[0]
    threshPath = f'threshold/threshold.png'
    plt.savefig(threshPath)

    classification_result = []
    for each_character in characters:
        # converts it to a 1D array
        each_character = each_character.reshape(1, -1)
        get_model = model()
        result = get_model.predict(each_character)
        
        classification_result.append(result)

    plate_string = ''
    for eachPredict in classification_result:
        plate_string += eachPredict[0]

    column_list_copy = column_list[:]
    column_list.sort()
    plateNumStr = ''
    for each in column_list:
        plateNumStr += plate_string[column_list_copy.index(each)]

    return plateNumStr, threshPath