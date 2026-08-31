import streamlit as st
import cv2
import numpy as np
from PIL import Image
import math

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="MVP Cicatrices",
    layout="wide"
)

st.title("🩹 MVP Cicatrices")
st.info(
    "Outil d'aide à la mesure de déformation à partir de 4 pastilles."
)

# ==================================================
# OUTILS
# ==================================================

def distance(p1, p2):
    return math.sqrt(
        (p2[0] - p1[0]) ** 2 +
        (p2[1] - p1[1]) ** 2
    )
def detect_markers(image_rgb):

    hsv = cv2.cvtColor(
        image_rgb,
        cv2.COLOR_RGB2HSV
    )

    # ----------------------------
    # Vert cible
    # ----------------------------

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

    kernel = np.ones((5,5), np.uint8)

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

        # éliminer les parasites
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

        # conserver les formes rondes
        if circularity < 0.60:
            continue

        M = cv2.moments(contour)

        if M["m00"] == 0:
            continue

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        candidates.append(
            (
                cx,
                cy,
                area
            )
        )

    # garder les 4 plus grosses pastilles

    candidates = sorted(
        candidates,
        key=lambda x: x[2],
        reverse=True
    )

    candidates = candidates[:4]

    centers = [
        (c[0], c[1])
        for c in candidates
    ]

    return centers, mask

def detect_markers_old(image_rgb):

    hsv = cv2.cvtColor(
        image_rgb,
        cv2.COLOR_RGB2HSV
    )

    saturation = hsv[:, :, 1]

    _, mask = cv2.threshold(
        saturation,
        60,
        255,
        cv2.THRESH_BINARY
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

    points = []

    for contour in contours:

        area = cv2.contourArea(contour)

        if area < 50:
            continue

        M = cv2.moments(contour)

        if M["m00"] == 0:
            continue

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        points.append((cx, cy))

    return points, mask


def sort_points(points):

    if len(points) != 4:
        return None

    points = sorted(points, key=lambda p: p[1])

    top = sorted(points[:2], key=lambda p: p[0])
    bottom = sorted(points[2:], key=lambda p: p[0])

    hg = top[0]
    hd = top[1]

    bg = bottom[0]
    bd = bottom[1]

    return hg, hd, bg, bd


def draw_detected_points(img, points):

    output = img.copy()

    for p in points:

        cv2.circle(
            output,
            p,
            12,
            (0, 255, 0),
            -1
        )

    return output


def manual_correction(points, prefix):

    if len(points) == 4:

        hg, hd, bg, bd = sort_points(points)

    else:

        hg = (0, 0)
        hd = (0, 0)
        bg = (0, 0)
        bd = (0, 0)

    st.subheader("Correction manuelle")

    c1, c2 = st.columns(2)

    with c1:

        hg_x = st.number_input(
            "HG X",
            value=int(hg[0]),
            key=f"{prefix}_hg_x"
        )

        hg_y = st.number_input(
            "HG Y",
            value=int(hg[1]),
            key=f"{prefix}_hg_y"
        )

        bg_x = st.number_input(
            "BG X",
            value=int(bg[0]),
            key=f"{prefix}_bg_x"
        )

        bg_y = st.number_input(
            "BG Y",
            value=int(bg[1]),
            key=f"{prefix}_bg_y"
        )

    with c2:

        hd_x = st.number_input(
            "HD X",
            value=int(hd[0]),
            key=f"{prefix}_hd_x"
        )

        hd_y = st.number_input(
            "HD Y",
            value=int(hd[1]),
            key=f"{prefix}_hd_y"
        )

        bd_x = st.number_input(
            "BD X",
            value=int(bd[0]),
            key=f"{prefix}_bd_x"
        )

        bd_y = st.number_input(
            "BD Y",
            value=int(bd[1]),
            key=f"{prefix}_bd_y"
        )

    return [
        (hg_x, hg_y),
        (hd_x, hd_y),
        (bg_x, bg_y),
        (bd_x, bd_y)
    ]


def draw_validated_shape(img, points):

    output = img.copy()

    labels = [
        "HG",
        "HD",
        "BG",
        "BD"
    ]

    for i, p in enumerate(points):

        x = int(p[0])
        y = int(p[1])

        cv2.circle(
            output,
            (x, y),
            12,
            (255, 0, 0),
            -1
        )

        cv2.putText(
            output,
            labels[i],
            (x + 15, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 0),
            2
        )

    cv2.line(
        output,
        points[0],
        points[1],
        (0, 255, 0),
        2
    )

    cv2.line(
        output,
        points[1],
        points[3],
        (0, 255, 0),
        2
    )

    cv2.line(
        output,
        points[3],
        points[2],
        (0, 255, 0),
        2
    )

    cv2.line(
        output,
        points[2],
        points[0],
        (0, 255, 0),
        2
    )

    return output


def compute_dimensions(points):

    hg, hd, bg, bd = points

    largeur = distance(
        hg,
        hd
    )

    hauteur = distance(
        hg,
        bg
    )

    return largeur, hauteur


def analyze_photo(image_file, prefix):

    image = Image.open(
        image_file
    ).convert("RGB")

    img_np = np.array(image)

    points, mask = detect_markers(
        img_np
    )

    st.subheader(prefix)

    st.image(
        draw_detected_points(
            img_np,
            points
        ),
        caption=f"{len(points)} pastilles détectées"
    )

    corrected_points = manual_correction(
        points,
        prefix
    )

    preview = draw_validated_shape(
        img_np,
        corrected_points
    )

    st.image(
        preview,
        caption="Points validés"
    )

    width, height = compute_dimensions(
        corrected_points
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            f"Largeur {prefix}",
            f"{width:.1f}px"
        )

    with col2:
        st.metric(
            f"Hauteur {prefix}",
            f"{height:.1f}px"
        )

    return width, height

# ==================================================
# CHARGEMENT DES IMAGES
# ==================================================
st.header("📷 Acquisition")

repos_file = st.file_uploader(
    "Photo Repos",
    type=["jpg","jpeg","png"],
    key="repos"
)

tension_x_file = st.file_uploader(
    "Photo Tension ECC",
    type=["jpg","jpeg","png"],
    key="tension_x"
)

tension_y_file = st.file_uploader(
    "Photo Tension EML",
    type=["jpg","jpeg","png"],
    key="tension_y"
)

repos_width = None
repos_height = None

tension_width = None
tension_height = None

repos_width = None
repos_height = None

tx_width = None
tx_height = None

ty_width = None
ty_height = None

# -------------------------
# REPOS
# -------------------------

if repos_file:

    st.header("Repos")

    repos_width, repos_height = analyze_photo(
        repos_file,
        "Repos"
    )

# -------------------------
# TENSION ECC
# -------------------------

if tension_x_file:

    st.header("Tension ECC")

    tx_width, tx_height = analyze_photo(
        tension_x_file,
        "Tension ECC"
    )

# -------------------------
# TENSION EML
# -------------------------

if tension_y_file:

    st.header("Tension EML")

    ty_width, ty_height = analyze_photo(
        tension_y_file,
        "Tension EML"
    )
# ==================================================
# RESULTATS
# ==================================================

if (
    repos_width is not None
    and tension_width is not None
):

    width_var = (
        (tension_width - repos_width)
        / repos_width
    ) * 100

    height_var = (
        (tension_height - repos_height)
        / repos_height
    ) * 100

    st.header("📊 Résultats")

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Variation largeur",
            f"{width_var:.1f}%"
        )

    with c2:

        st.metric(
            "Variation hauteur",
            f"{height_var:.1f}%"
        )

else:

    st.info(
        "Importer les deux images pour calculer les déformations."
    )
    
    
 if (
    repos_width is not None
    and tx_width is not None
):

    st.header("📊 Déformation Tension X")

    width_var_x = (
        (tx_width - repos_width)
        / repos_width
    ) * 100

    height_var_x = (
        (tx_height - repos_height)
        / repos_height
    ) * 100

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Variation largeur X",
            f"{width_var_x:.1f}%"
        )

    with c2:
        st.metric(
            "Variation hauteur X",
            f"{height_var_x:.1f}%"
        )

# ----------------------------------

if (
    repos_width is not None
    and ty_width is not None
):

    st.header("📊 Déformation Tension Y")

    width_var_y = (
        (ty_width - repos_width)
        / repos_width
    ) * 100

    height_var_y = (
        (ty_height - repos_height)
        / repos_height
    ) * 100

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Variation largeur Y",
            f"{width_var_y:.1f}%"
        )

    with c2:
        st.metric(
            "Variation hauteur Y",
            f"{height_var_y:.1f}%"
        )   