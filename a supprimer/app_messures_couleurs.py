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
    compute_variation,
    extract_roi_color,
    save_mean_color_image
)

from ui import (
    draw_validated_shape
)

# ======================================================
# CONFIG
# ======================================================
st.set_page_config( page_title="MVP Cicatrices", layout="wide")
st.title("🩹 MVP Cicatrices")

st.info( "Mesure de déformation de la peau à partir de 4 pastilles "
    "(outil d'aide à la mesure, sans diagnostic médical)." )

st.header("Patient")
patient_id = st.text_input( "Identifiant Patient", value="")
jour = st.selectbox( "Jour",["J0","J9","J18"])
tab1, tab2 = st.tabs(  ["📐 Déformation", "🎨 Couleur" ])

with tab1:   
   
   # ======================================================
   # TRAITEMENT D'UNE PHOTO
   # ======================================================
   
   def process_image(uploaded_file, prefix, correction):
   
       image = Image.open(uploaded_file).convert("RGB")   
       img_np = np.array(image)   
       detected_points, mask = detect_markers(img_np )
   
       if len(detected_points) == 4:   
           hg, hd, bg, bd = sort_points( detected_points )
       else:   
           st.error(
               f"{prefix} : {len(detected_points)} "
               f"pastille(s) détectée(s)."
           )   
           hg = (0, 0)
           hd = (0, 0)
           bg = (0, 0)
           bd = (0, 0)
   
       photo_col, control_col = st.columns( [3, 1]  )
   
       # ------------------------------------
       # CORRECTIONS
       # ------------------------------------
   
       with control_col:   
           st.markdown( "### Correction ±correction px" )   
           st.markdown("#### HG")   
           hg_dx = st.slider( "HG ΔX", -correction, correction, 0, key=f"{prefix}_hg_dx" )   
           hg_dy = st.slider( "HG ΔY", -correction, correction, 0, key=f"{prefix}_hg_dy" )   
           st.markdown("#### HD")   
           hd_dx = st.slider( "HD ΔX", -correction, correction, 0, key=f"{prefix}_hd_dx" )
           hd_dy = st.slider( "HD ΔY", -correction, correction, 0, key=f"{prefix}_hd_dy" )
           st.markdown("#### BG")  
           bg_dx = st.slider( "BG ΔX", -correction, correction, 0, key=f"{prefix}_bg_dx" )
           bg_dy = st.slider( "BG ΔY", -correction, correction, 0, key=f"{prefix}_bg_dy" )  
           st.markdown("#### BD")
           bd_dx = st.slider( "BD ΔX", -correction, correction, 0, key=f"{prefix}_bd_dx" )
           bd_dy = st.slider( "BD ΔY", -correction, correction, 0, key=f"{prefix}_bd_dy" )            
   
       # ------------------------------------
       # APPLICATION DES CORRECTIONS
       # ------------------------------------
       corrected_points = [
           ( hg[0] + hg_dx, hg[1] + hg_dy ),   
           ( hd[0] + hd_dx, hd[1] + hd_dy ),
           ( bg[0] + bg_dx, bg[1] + bg_dy ),   
           ( bd[0] + bd_dx, bd[1] + bd_dy )
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
   
       largeur, hauteur = compute_dimensions( corrected_points )   
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
       "Photo Tension ECC",
       type=["jpg", "jpeg", "png"],
       key="tx"
   )
   
   tension_y_file = st.file_uploader(
       "Photo Tension EML",
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
       repos = process_image(  repos_file,  "Repos" , 10 )
   
   if tension_x_file:
       st.header("Tension ECC")
       tx = process_image(tension_x_file, "Tension ECC", 10)
   
   if tension_y_file:
       st.header("Tension EML")
       ty = process_image( tension_y_file, "Tension EML", 10 )
       
   # ======================================================
   # Formules utilisées
   # ======================================================
   st.header("📐 Formules utilisées")  
   st.latex(r"""\Delta Largeur (\%)=\frac{Largeur_{Tension} - Largeur_{Repos}}{Largeur_{Repos}}\times 100 """ )
   st.latex(r"""\Delta Hauteur (\%)=\frac{Hauteur_{Tension} - Hauteur_{Repos}}{Hauteur_{Repos}}\times 100 """)  
   
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
   
       st.header( "📊 Déformation Tension ECC"  )   
       c1, c2 = st.columns(2)   
       with c1:   
           st.metric(
               "Variation largeur ECC",
               f"{width_var_x:.1f}%"
           )   
       with c2:   
           st.metric(
               "Variation hauteur ECC",
               f"{height_var_x:.1f}%"
           )
   
   # ------------------------------------------
   
   if repos and ty:   
       width_var_y  = compute_variation( repos[0], ty[0] )   
       height_var_y = compute_variation( repos[1], ty[1] )
   
       st.header( "📊 Déformation Tension EML" )
   
       c1, c2 = st.columns(2)   
       with c1:   
           st.metric(
               "Variation largeur EML",
               f"{width_var_y:.1f}%"
           )   
       with c2:   
           st.metric(
               "Variation hauteur EML",
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
           "Importer les photos Repos, Tension ECC et/ou "
           "Tension EML pour commencer l'analyse."
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

   
with tab2:
    from storage_color import save_color_measurement
    st.header( "Analyse colorimétrique"  )
    couleur_file = st.file_uploader( "Photo Couleur", type=["jpg","jpeg","png"], key="couleur" )  
    
    if couleur_file:
        st.header("Couleur")
        couleur = process_image(  couleur_file,  "Couleur" , 50) 
        image = Image.open( couleur_file ).convert("RGB")
        img_np = np.array(image)
        points_detectes, mask = detect_markers( img_np )
        
        r,g,b = extract_roi_color( img_np, sort_points(points_detectes) )
        output_file = save_mean_color_image( patient_id, jour, couleur_file.name, r, g, b)
        st.subheader("Couleur moyenne mesurée")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔴 Rouge", f"{r:.1f}")
        with col2:
            st.metric("🟢 Vert", f"{g:.1f}")
        with col3:
            st.metric("🔵 Bleu", f"{b:.1f}")
        
        
    if st.button( "💾 Sauvegarder couleur"):
      save_color_measurement( patient_id, jour, r, g, b, couleur_file.name  )
      st.image(  output_file,  caption="Couleur moyenne")
      st.success(  "Mesure couleur enregistrée." )       
      st.subheader( "Historique couleur")
      if patient_id:
        if os.path.exists( "historique_couleur.csv"  ):
          df_color = pd.read_csv( "historique_couleur.csv" )
          patient_color = df_color[ df_color["patient_id"] == patient_id ]
          st.dataframe( patient_color, use_container_width=True )
        