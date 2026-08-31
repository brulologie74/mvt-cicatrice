import cv2
import numpy as np
from config import *

def apply_processing(
    image,
    luminosite,
    contraste,
    rotation
):
    img = image.copy()
    # luminosité / contraste
    img = cv2.convertScaleAbs( img, alpha=contraste,  beta=luminosite )
    # rotation
    h, w = img.shape[:2]
    center = (  w // 2,  h // 2 )
    matrix = cv2.getRotationMatrix2D( center, rotation, 1.0 )
    img = cv2.warpAffine( img, matrix, (w, h) )

    return img
    
def draw_virtual_markers(
    image,
    points,
    radius=20
):
    img = image.copy()
    for point in points:
        cv2.circle(  img, point, radius, (0,255,0), -1 )

    return img    