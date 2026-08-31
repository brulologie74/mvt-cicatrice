import cv2
import numpy as np
from config import *


def detect_markers(image_rgb):

    hsv = cv2.cvtColor(
        image_rgb,
        cv2.COLOR_RGB2HSV
    )

    # Vert cible HSV
    target_h = 60
    target_s = 255
    target_v = 255

    h_margin = 9
    s_margin = 13
    v_margin = 13

    lower = np.array([
        max(0, target_h - h_margin),
        max(0, target_s - s_margin),
        max(0, target_v - v_margin)
    ])

    upper = np.array([
        min(179, target_h + h_margin),
        min(255, target_s + s_margin),
        min(255, target_v + v_margin)
    ])

    mask = cv2.inRange(
        hsv,
        lower,
        upper
    )

    kernel = np.ones((5, 5), np.uint8)

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    candidates = []

    for contour in contours:

        area = cv2.contourArea(contour)

        if area < 30:
            continue

        perimeter = cv2.arcLength(
            contour,
            True
        )

        if perimeter == 0:
            continue

        circularity = (
            4 * np.pi * area
        ) / (perimeter * perimeter)

        if circularity < 0.60:
            continue

        M = cv2.moments(contour)

        if M["m00"] == 0:
            continue

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        candidates.append(
            (cx, cy, area)
        )

    candidates.sort(
        key=lambda x: x[2],
        reverse=True
    )

    candidates = candidates[:4]

    points = [
        (c[0], c[1])
        for c in candidates
    ]

    return points, mask