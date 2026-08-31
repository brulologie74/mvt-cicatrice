import streamlit as st
import numpy as np
import pandas as pd
import os
from PIL import Image

from detection import detect_markers
from storage import save_measurements

from analyse import (
    sort_points,
    compute_dimensions,
    compute_variation
)

from ui import (
    draw_validated_shape
)

# ======================================================
# CONFIG
# ======================================================

st.set_page_config(
    page_title="MVP Cicatrices",
    layout="wide"
)

st.title("🩹 MVP Cicatrices")

st.info(
    "Mesure de déformation de la peau à partir de 4 pastilles "
    "(outil d'aide à la mesure, sans diagnostic médical)."
)

st.header("Patient")
patient_id = st.text_input( "Identifiant Patient", value="")
jour = st.selectbox( "Jour",["J0","J9","J18"])

# ======================================================
# TRAITEMENT D'UNE PHOTO
# ======================================================

def process_image(uploaded_file, prefix):

    image = Image.open(uploaded_file).convert("RGB")

    img_np = np.array(image)

    detected_points, mask = detect_markers(
        img_np
    )

    if len(detected_points) == 4:

        hg, hd, bg, bd = sort_points(
            detected_points
        )

    else:

        st.error(
            f"{prefix} : {len(detected_points)} "
            f"pastille(s) détectée(s)."
        )

        hg = (0, 0)
        hd = (0, 0)
        bg = (0, 0)
        bd = (0, 0)

    # ------------------------------------
    # COLONNES
    # ------------------------------------

    photo_col, control_col = st.columns(
        [3, 1]
    )

    # ------------------------------------
    # CORRECTIONS
    # ------------------------------------

    with control_col:

        st.markdown(
            "### Correction ±10 px"
        )

        st.markdown("#### HG")

        hg_dx = st.slider(
            "HG ΔX",
            -10,
            10,
            0,
            key=f"{prefix}_hg_dx"
        )

        hg_dy = st.slider(
            "HG ΔY",
            -10,
            10,
            0,
            key=f"{prefix}_hg_dy"
        )

        st.markdown("#### HD")

        hd_dx = st.slider(
            "HD ΔX",
            -10,
            10,
            0,
            key=f"{prefix}_hd_dx"
        )

        hd_dy = st.slider(
            "HD ΔY",
            -10,
            10,
            0,
            key=f"{prefix}_hd_dy"
        )

        st.markdown("#### BG")

        bg_dx = st.slider(
            "BG ΔX",
            -10,
            10,
            0,
            key=f"{prefix}_bg_dx"
        )

        bg_dy = st.slider(
            "BG ΔY",
            -10,
            10,
            0,
            key=f"{prefix}_bg_dy"
        )

        st.markdown("#### BD")

        bd_dx = st.slider(
            "BD ΔX",
            -10,
            10,
            0,
            key=f"{prefix}_bd_dx"
        )

        bd_dy = st.slider(
            "BD ΔY",
            -10,
            10,
            0,
            key=f"{prefix}_bd_dy"
        )

    # ------------------------------------
    # APPLICATION DES CORRECTIONS
    # ------------------------------------

    corrected_points = [

        (
            hg[0] + hg_dx,
            hg[1] + hg_dy
        ),

        (
            hd[0] + hd_dx,
            hd[1] + hd_dy
        ),

        (
            bg[0] + bg_dx,
            bg[1] + bg_dy
        ),

        (
            bd[0] + bd_dx,
            bd[1] + bd_dy
        )
    ]

    # ------------------------------------
    # DESSIN
    # ------------------------------------

    preview = draw_validated_shape(
        img_np.copy(),
        corrected_points
    )

    with photo_col:

        st.image(
            preview,
            caption=f"{prefix} - pastilles validées",
            use_container_width=True
        )

    # ------------------------------------
    # MESURES
    # ------------------------------------

    largeur, hauteur = compute_dimensions(
        corrected_points
    )

    m1, m2 = st.columns(2)

    with m1:

        st.metric(
            f"Largeur {prefix}",
            f"{largeur:.1f}px"
        )

    with m2:

        st.metric(
            f"Hauteur {prefix}",
            f"{hauteur:.1f}px"
        )

    return largeur, hauteur


# ======================================================
# CHARGEMENT DES PHOTOS
# ======================================================

st.header("📷 Acquisition")

repos_file = st.file_uploader(
    "Photo Repos",
    type=["jpg", "jpeg", "png"],
    key="repos"
)

tension_x_file = st.file_uploader(
    "Photo Tension X",
    type=["jpg", "jpeg", "png"],
    key="tx"
)

tension_y_file = st.file_uploader(
    "Photo Tension Y",
    type=["jpg", "jpeg", "png"],
    key="ty"
)

# ======================================================
# ANALYSES
# ======================================================

repos = None
tx = None
ty = None

if repos_file:
    st.header("Repos")
    repos = process_image(  repos_file,  "Repos"  )

if tension_x_file:
    st.header("Tension ECC")
    tx = process_image(tension_x_file, "Tension ECC")

if tension_y_file:
    st.header("Tension EML")
    ty = process_image( tension_y_file, "Tension EML" )
    
# ======================================================
# Formules utilisées
# ======================================================
st.header("📐 Formules utilisées")  
st.latex( r""" \Delta Largeur(\%) = \frac{ Largeur_{Tension}  -  Largeur_{Repos} } { Largeur_{Repos} } \times 100 """ )
st.latex(r""" \Delta Hauteur(\%) = \frac{ Hauteur_{Tension} - Hauteur_{Repos} } { Hauteur_{Repos} } \times 100 """)  

# ======================================================
# RESULTATS
# ======================================================

if repos and tx:

    width_var_x = compute_variation(
        repos[0],
        tx[0]
    )

    height_var_x = compute_variation(
        repos[1],
        tx[1]
    )

    st.header(
        "📊 Déformation Tension X"
    )

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

# ------------------------------------------

if repos and ty:

    width_var_y = compute_variation(
        repos[0],
        ty[0]
    )

    height_var_y = compute_variation(
        repos[1],
        ty[1]
    )

    st.header(
        "📊 Déformation Tension Y"
    )

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

# ======================================================
# MESSAGE SI RIEN CHARGÉ
# ======================================================

if (
    repos_file is None
    and tension_x_file is None
    and tension_y_file is None
):

    st.info(
        "Importer les photos Repos, Tension X et/ou "
        "Tension Y pour commencer l'analyse."
    )
# ======================================================    
# SAUVEGARDE    
# ======================================================
if repos and tx and ty:
    if st.button(  "💾 Sauvegarder la séance"  ):

        save_measurements(
            patient_id,
            jour,
            repos,
            tx,
            ty,
            repos_file.name,
            tension_x_file.name,
            tension_y_file.name
        )

        st.success( f"Séance {jour} enregistrée pour {patient_id}" )
       
# ======================================================        
# Affichage historique        
# ======================================================
#if patient_id:
#    try: df = pd.read_csv( "historique.csv"      )
#        patient_df = df[ df["patient_id"] == patient_id ]
#        st.header( "Historique du patient"  )
#        st.dataframe(patient_df  )
#
#    except: pass        
#    