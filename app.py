import streamlit as st
import numpy as np
import cv2
import json
import pandas as pd
import plotly.graph_objects as go
import os

from config import *

from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image

from detection import detect_markers
from storage import save_measurements

from graphs import (
    build_rgb_population_graph,
    build_deformation_bar_chart
    )

from analyse import (
    sort_points,
    compute_dimensions,
    compute_variation,
    extract_roi_color,
    save_mean_color_image
)

from ui import ( draw_validated_shape)

from photo_processing import ( 
    apply_processing,
    draw_virtual_markers
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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(  
            ["📐 Déformation", 
            "🎨 Couleur", 
            "📊 Statistiques", 
            "🗄️ Données" , 
            "🖍️ Placement manuel des pastilles",
            "🖼️ Traitement photos"])

#**********************************************************************************          
#**********************************************************************************
# Déformation
#**********************************************************************************
#**********************************************************************************
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
           st.error( f"{prefix} : {len(detected_points)} " f"pastille(s) détectée(s)." )   
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
       preview = draw_validated_shape( img_np.copy(), corrected_points )
       with photo_col:   
           st.image( preview, caption=f"{prefix} - pastilles validées", width='stretch'  )
   
       # ------------------------------------
       # MESURES
       # ------------------------------------
       largeur, hauteur = compute_dimensions( corrected_points )   
       m1, m2 = st.columns(2)   
       with m1:   
           st.metric( f"Largeur {prefix}", f"{largeur:.1f}px" )   
       with m2:   
           st.metric( f"Hauteur {prefix}", f"{hauteur:.1f}px" )   
       return largeur, hauteur   
   
   # ======================================================
   # CHARGEMENT DES PHOTOS
   # ======================================================
   st.header("📷 Acquisition")   
   repos_file = st.file_uploader( "Photo Repos", type=["jpg", "jpeg", "png"], key="repos" )   
   tension_x_file = st.file_uploader( "Photo Tension ECC", type=["jpg", "jpeg", "png"], key="tx")   
   tension_y_file = st.file_uploader( "Photo Tension EML", type=["jpg", "jpeg", "png"], key="ty" )
   
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
       width_var_x  = compute_variation( repos[0], tx[0] )   
       height_var_x = compute_variation( repos[1], tx[1] )   
       st.header( "📊 Déformation Tension ECC"  )   
       c1, c2 = st.columns(2)   
       with c1:   
           st.metric( "Variation largeur ECC", f"{width_var_x:.1f}%" )   
       with c2:   
           st.metric( "Variation hauteur ECC", f"{height_var_x:.1f}%" )
   # ------------------------------------------
   
   if repos and ty:   
       width_var_y  = compute_variation( repos[0], ty[0] )   
       height_var_y = compute_variation( repos[1], ty[1] )  
       st.header( "📊 Déformation Tension EML" )
       c1, c2 = st.columns(2)   
       with c1:   
           st.metric( "Variation largeur EML", f"{width_var_y:.1f}%" )   
       with c2:   
           st.metric( "Variation hauteur EML", f"{height_var_y:.1f}%" )
   
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
          
#**********************************************************************************          
#**********************************************************************************
# Couleur
#**********************************************************************************
#**********************************************************************************  
 
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
          st.dataframe( patient_color, width='stretch' )
          
#**********************************************************************************          
#**********************************************************************************
# Statistiques
#**********************************************************************************
#**********************************************************************************
with tab3:
    st.header("📊 Statistiques")
    import pandas as pd
    import os
    # ========================================
    # DEFORMATION
    # ========================================
    st.subheader("📐 Analyse de déformation")
    st.info("Outil d'aide à la mesure. Les résultats dépendent de la qualité des images et du protocole de prise de vue.")
    if os.path.exists("historique.csv"):
        df = pd.read_csv( "historique.csv" )
        st.write(f"Nombre de mesures : {len(df)}")
        mesures = { "Δ Largeur X": "variation_width_x",
                    "Δ Hauteur X": "variation_height_x",
                    "Δ Largeur Y": "variation_width_y",
                    "Δ Hauteur Y": "variation_height_y",
                    "Δ Moyenne": "variation_m"
                  }    
        selection = st.selectbox( "Indicateur", list(mesures.keys()))
        metric = mesures[selection]    
        fig = build_deformation_bar_chart( df, metric)
        st.plotly_chart(    fig,   width='stretch')        
    else :
        st.warning("Le fichier historique.csv est introuvable.")
    # ========================================
    # COULEUR
    # ========================================
    st.markdown("---")
    st.subheader("🎨 Colorimétrie")
    if os.path.exists( "historique_couleur.csv" ):
        df_color = pd.read_csv( "historique_couleur.csv" )
        st.metric( "Mesures couleur",  len(df_color) )
        # ====================================
        # Pourcentages RGB
        # ====================================
        def rgb_percentages( row ):
            total = ( row["r"] + row["g"] + row["b"] )
            if total == 0:
                return pd.Series([ 0, 0, 0 ] )
            return pd.Series( [ row["r"] / total * 100, row["g"] / total * 100, row["b"] / total * 100 ] )
        df_color[ [ "r_pct", "g_pct", "b_pct" ]] = df_color.apply( rgb_percentages, axis=1 )

        # ====================================
        # MOYENNES RGB %
        # ====================================
        st.subheader( "Répartition RGB moyenne"  )
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric( "Rouge %", f"{df_color['r_pct'].mean():.1f}%" )
        with c2:                                                    
            st.metric( "Vert %", f"{df_color['g_pct'].mean():.1f}%" )
        with c3:                                                    
            st.metric( "Bleu %", f"{df_color['b_pct'].mean():.1f}%" )

        # ====================================
        # REFERENCES CAUCASIENNES
        # ====================================
        REF_R = 40.0
        REF_G = 32.5
        REF_B = 27.5
        st.subheader( "Comparaison référence caucasienne" )
        ref_df = pd.DataFrame(
            {
                "Canal": [ "Rouge", "Vert", "Bleu" ],
                "Mesuré": [ round( df_color["r_pct" ].mean(), 1 ), 
                            round( df_color["g_pct" ].mean(), 1 ),
                            round( df_color["b_pct" ].mean(), 1 ) ],
                "Référence": [ REF_R, REF_G, REF_B ]
            }
        )
        # ====================================
        # GRAPH COULEURS 
        # ====================================       
        st.dataframe(  ref_df,  width='stretch'  )
        fig = build_rgb_population_graph( df_color)
        st.plotly_chart( fig, width='stretch')

#**********************************************************************************          
#**********************************************************************************
# Gestion des données
#**********************************************************************************
#**********************************************************************************
with tab4:
    st.header("🗄️ Gestion des données")
    import pandas as pd
    import os

    # ==========================================
    # HISTORIQUE DEFORMATION
    # ==========================================
    st.subheader("📐 Historique Déformation")
    if os.path.exists("historique.csv"):
        df = pd.read_csv("historique.csv" )
        st.dataframe( df, width='stretch' )
        ligne = st.selectbox( "Sélectionner une ligne à supprimer", options=df.index, key="delete_def"  )
        if st.button( "🗑️ Supprimer la ligne Déformation" ):
            df = df.drop( index=ligne  )
            df.to_csv( "historique.csv", index=False  )
            st.success( "Ligne supprimée." )
            st.rerun()
    else:
        st.info(  "historique.csv introuvable." )

    # ==========================================
    # HISTORIQUE COULEUR
    # ==========================================
    st.markdown("---")
    st.subheader("🎨 Historique Couleur")
    if os.path.exists("historique_couleur.csv" ):
        df_color = pd.read_csv("historique_couleur.csv" )
        st.dataframe( df_color,  width='content' )
        ligne_color = st.selectbox(
            "Sélectionner une ligne couleur à supprimer",
            options=df_color.index,
            key="delete_color"
        )
        if st.button( "🗑️ Supprimer la ligne Couleur" ):
            df_color = df_color.drop( index=ligne_color  )
            df_color.to_csv( "historique_couleur.csv", index=False  )
            st.success( "Ligne supprimée." )
            st.rerun()
    else:
        st.info(  "historique_couleur.csv introuvable." )
#**********************************************************************************          
#**********************************************************************************
# Traitement photos - ajouter des pastilles
#**********************************************************************************
#**********************************************************************************        
with tab6:
    st.header("🖼️ Traitement photos" )        
    photo_file = st.file_uploader( "Photo",type=["jpg","jpeg","png"], key="traitement")
    if photo_file:
        image = Image.open( photo_file ).convert("RGB")
        img_np = np.array(image)
        col1, col2 = st.columns([5,1])
    # =========================================
    #Parametres 
        with col1:
            st.image( img_np, caption="Original" )
        with col2:
            luminosite = st.slider( "Luminosité", -100, 100, 0 )
            contraste = st.slider( "Contraste", 0.5, 3.0, 1.0 )
            saturation = st.slider( "Saturation", 0.5, 3.0, 1.0 )
            rotation = st.slider( "Rotation", -20, 20, 0 )
            processed = apply_processing( img_np, luminosite, contraste, rotation)     

#**********************************************************************************          
#**********************************************************************************
# 🖍️ Placement manuel des pastilles
#**********************************************************************************
#**********************************************************************************        
with tab5:
    st.header( "🖍️ Placement manuel des pastilles" )
    st.info("Cliquer successivement sur les points Haut-Gauche, Haut-Droit, Bas-Gauche puis Bas-Droit." )
    photo_file = st.file_uploader( "Photo à annoter",  type=["jpg", "jpeg", "png"], key="placement_manuel" )
    if photo_file:
        image = Image.open( photo_file ).convert("RGB")
        img_np = np.array(image)
        # -----------------------------------
        # Initialisation session
        # -----------------------------------
        if "manual_points" not in st.session_state:
            st.session_state.manual_points = []
        # -----------------------------------
        # Affichage instruction
        # -----------------------------------
        labels = [ "HG","HD", "BG", "BD"]
        if ( len( st.session_state.manual_points ) < 4
        ):
            st.warning(
                f"Sélectionner : "
                f"{labels[len(st.session_state.manual_points)]}"
            )
        # -----------------------------------
        # Clic
        # -----------------------------------
        clicked = streamlit_image_coordinates( image, key="click_manual" )
        if ( clicked and len( st.session_state.manual_points ) < 4
        ):
            point = ( clicked["x"], clicked["y"] )
            if (len(st.session_state.manual_points ) == 0
                or point != st.session_state.manual_points[-1] ):
                st.session_state.manual_points.append( point )
                st.rerun()

        # -----------------------------------
        # Dessin
        # -----------------------------------
        preview = img_np.copy()
        current_points = ( st.session_state.manual_points )
        colors = {
            "HG": (255, 0, 0),
            "HD": (0, 255, 0),
            "BG": (255, 255, 0),
            "BD": (255, 0, 255)
        }
        for i, p in enumerate( current_points ):
            label = labels[i]
            cv2.circle( preview, p, 12, colors[label], -1            )
            cv2.putText(
                preview,
                label,
                ( p[0] + 15, p[1] ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                colors[label],
                2 )
        if len(current_points) == 4:
            cv2.line( preview, current_points[0], current_points[1], (0, 255, 0), 2 )
            cv2.line( preview, current_points[1], current_points[3], (0, 255, 0), 2 )
            cv2.line( preview, current_points[3], current_points[2], (0, 255, 0), 2 )
            cv2.line( preview, current_points[2], current_points[0], (0, 255, 0), 2 )
        st.image( preview, caption="Prévisualisation")

        # -----------------------------------
        # Coordonnées
        # -----------------------------------
        st.subheader( "Coordonnées" )
        st.write(st.session_state.manual_points )

        # -----------------------------------
        # Boutons
        # -----------------------------------
        col1, col2 = st.columns(2)
        with col1:
            if st.button( "↩ Dernier point" ):
                if ( len( st.session_state.manual_points ) > 0
                ):
                    st.session_state.manual_points.pop()
                    st.rerun()
        with col2:
            if st.button( "🗑 Réinitialiser" ):
                st.session_state.manual_points = []
                st.rerun()

        # -----------------------------------
        # Sauvegarde
        # -----------------------------------
        if len(current_points) == 4:
            st.success( "4 points validés" )

            if st.button("💾 Sauvegarder" ):
                save_dir = os.path.join( "data", patient_id, jour )
                os.makedirs( save_dir, exist_ok=True)
                photo_name = os.path.splitext( photo_file.name )[0]
                image_output = os.path.join( save_dir, f"{photo_name}_pastilles.jpg" )
                json_output = os.path.join( save_dir, f"{photo_name}_pastilles.json" )
                cv2.imwrite( image_output, cv2.cvtColor( preview, cv2.COLOR_RGB2BGR ) )
                data = {
                    "HG": current_points[0],
                    "HD": current_points[1],
                    "BG": current_points[2],
                    "BD": current_points[3]
                }
                with open(json_output, "w",  encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                st.success("Image et coordonnées sauvegardées.")
                st.write(image_output)
                st.write(json_output)
