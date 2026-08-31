import pandas as pd
import os
from config import *
from datetime import datetime

def save_measurements(
    patient_id,
    day,
    repos,
    tx,
    ty,
    repos_filename,
    tx_filename,
    ty_filename
):
    variation_width_x  = abs(((tx[0] - repos[0]) / repos[0]) * 100)
    variation_height_x = abs(((tx[1] - repos[1]) / repos[1]) * 100)
    variation_width_y  = abs(((ty[0] - repos[0]) / repos[0]) * 100)
    variation_height_y = abs(((ty[1] - repos[1]) / repos[1]) * 100)
    variation_m = abs(( variation_width_x + variation_height_x + variation_width_y + variation_height_y) / 4)

    row = {
        "date_mesure": datetime.now().strftime( "%Y-%m-%d %H:%M:%S" ),
        "patient_id": patient_id,
        "jour": day,
        "photo_repos": repos_filename,
        "photo_tx": tx_filename,
        "photo_ty": ty_filename,

        "width_repos": repos[0],
        "height_repos": repos[1],

        "width_tx": tx[0],
        "height_tx": tx[1],

        "width_ty": ty[0],
        "height_ty": ty[1], 
        
        "variation_width_x": variation_width_x,
        "variation_height_x": variation_height_x,
        "variation_width_y": variation_width_y,
        "variation_height_y": variation_height_y,
        "variation_m": variation_m
    }
    file_path = "historique.csv"

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df = pd.concat( [df, pd.DataFrame([row])], ignore_index=True )
    else:
        df = pd.DataFrame([row])
    df.to_csv(
        file_path,
        index=False
    )