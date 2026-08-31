import math
import cv2
import numpy as np
from config import *

def distance(p1, p2):
    return math.sqrt( (p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 )

def sort_points(points):
    points = sorted(
        points,
        key=lambda p: p[1]
    )
    top = sorted(
        points[:2],
        key=lambda p: p[0]
    )
    bottom = sorted(
        points[2:],
        key=lambda p: p[0]
    )
    hg = top[0]
    hd = top[1]
    bg = bottom[0]
    bd = bottom[1]
    return hg, hd, bg, bd

def compute_dimensions(points):
    hg, hd, bg, bd = points
    largeur = ( distance(hg, hd) + distance(bg, bd) ) / 2
    hauteur = ( distance(hg, bg) + distance(hd, bd) ) / 2
    return largeur, hauteur

def compute_variation( repos_value, tension_value):
    if repos_value == 0 : 
        return 0
    return abs(((tension_value - repos_value) / repos_value ) * 100)

def extract_roi_color(image, points):
    """
    Calcule la couleur moyenne RGB
    dans le quadrilatère défini
    par les 4 pastilles.
    """

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    x_min = int(min(xs))
    x_max = int(max(xs))

    y_min = int(min(ys))
    y_max = int(max(ys))

    roi = image[ y_min:y_max, x_min:x_max]

    if roi.size == 0:
        return 0, 0, 0
    r = round( roi[:, :, 0].mean(), 1)
    g = round( roi[:, :, 1].mean(), 1)
    b = round( roi[:, :, 2].mean(), 1)

    return r, g, b  

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os


def save_mean_color_image( patient_id, jour, photo_repos, r, g, b):
    """
    Génère une image représentant
    la couleur moyenne calculée.
    """

    width = 256
    height = 256

    color = ( int(r), int(g), int(b) )
    img = Image.new(  "RGB", (width, height), color )
    draw = ImageDraw.Draw(img)

    text = ( f"RGB: [{int(r)} {int(g)} {int(b)}]"  )
    draw.text((10, 10), text, fill=(255, 255, 255) )

    # nom photo sans extension

    photo_name = os.path.splitext( os.path.basename(photo_repos))[0]
    directory = os.path.join( "data", patient_id, jour )
    os.makedirs( directory, exist_ok=True )
    output_file = os.path.join(
        directory,
        f"{photo_name}_couleur_moyenne.jpg"
    )
    img.save(output_file)

    return output_file    
    
def rgb_percentages(r, g, b):
    total = r + g + b

    if total == 0:
        return 0, 0, 0
    r_pct = round((r / total) * 100, 2 )
    g_pct = round((g / total) * 100, 2 )
    b_pct = round((b / total) * 100, 2 )
 
    return r_pct, g_pct, b_pct    


