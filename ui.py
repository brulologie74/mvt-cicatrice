import streamlit as st
import cv2
from analyse import (
    sort_points,
    compute_dimensions
)
def manual_correction(points, prefix):
    if len(points) == 4:
        hg, hd, bg, bd = sort_points(points)
    else:
        hg = (0, 0)
        hd = (0, 0)
        bg = (0, 0)
        bd = (0, 0)

    st.subheader("Correction fine (±10 px)")
    corrections = {}

    for name in ["HG", "HD", "BG", "BD"]:
        st.markdown(f"**{name}**")
        col1, col2 = st.columns(2)
        with col1:
            corrections[f"{name}_dx"] = st.slider(
                f"{name} ΔX",
                min_value=-10,
                max_value=10,
                value=0,
                key=f"{prefix}_{name}_dx"
            )
        with col2:
            corrections[f"{name}_dy"] = st.slider(
                f"{name} ΔY",
                min_value=-10,
                max_value=10,
                value=0,
                key=f"{prefix}_{name}_dy"
            )
    corrected_points = [
        (
            hg[0] + corrections["HG_dx"],
            hg[1] + corrections["HG_dy"]
        ),
        (
            hd[0] + corrections["HD_dx"],
            hd[1] + corrections["HD_dy"]
        ),
        (
            bg[0] + corrections["BG_dx"],
            bg[1] + corrections["BG_dy"]
        ),
        (
            bd[0] + corrections["BD_dx"],
            bd[1] + corrections["BD_dy"]
        )
    ]

    return corrected_points

def manual_correction_old(points, prefix):

    if len(points) == 4:
        hg, hd, bg, bd = sort_points(points)
    else:
        hg = (0, 0)
        hd = (0, 0)
        bg = (0, 0)
        bd = (0, 0)

    st.subheader( f"Correction manuelle {prefix}")

    hg_x = st.number_input( f"{prefix}_HG_ECC", value=int(hg[0]) )
    hg_y = st.number_input( f"{prefix}_HG_EML", value=int(hg[1]) )
    hd_x = st.number_input( f"{prefix}_HD_ECC", value=int(hd[0]) )
    hd_y = st.number_input( f"{prefix}_HD_EML", value=int(hd[1]) )
    bg_x = st.number_input( f"{prefix}_BG_ECC", value=int(bg[0]) )
    bg_y = st.number_input( f"{prefix}_BG_EML", value=int(bg[1]) )
    bd_x = st.number_input( f"{prefix}_BD_ECC", value=int(bd[0]) )
    bd_y = st.number_input( f"{prefix}_BD_Y",   value=int(bd[1]) )

    return [
        (hg_x, hg_y),
        (hd_x, hd_y),
        (bg_x, bg_y),
        (bd_x, bd_y)
    ]

def draw_points( image, points ):
    output = image.copy()
    for p in points:
        cv2.circle( output, (int(p[0]), int(p[1])), 12, (0, 255, 0), -1 )
    return output

def draw_validated_shape(image, points):
    img = image.copy()
    labels = ["HG", "HD","BG","BD" ]
    for i, p in enumerate(points):
        x = int(p[0])
        y = int(p[1])
        cv2.circle (  img,  (x, y),  12,  (0, 255, 0),  -1 )
        cv2.putText(  img,  labels[i],  (x + 15, y),  cv2.FONT_HERSHEY_SIMPLEX,  0.7,  (255, 0, 0),  2  )
    # Quadrilatère
    cv2.line( img, points[0], points[1], (255, 0, 0), 2 )
    cv2.line( img, points[1], points[3], (255, 0, 0), 2 )
    cv2.line( img, points[3], points[2], (255, 0, 0), 2 )
    cv2.line( img, points[2], points[0], (255, 0, 0), 2 )
    return img        
    