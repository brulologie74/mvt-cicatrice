import pandas as pd
import os
from datetime import datetime
from config import *

def save_color_measurement(
    patient_id,
    day,
    r,
    g,
    b,
    photo_repos
):
    row = {
        "patient_id": patient_id,
        "jour": day,
        "r": r,
        "g": g,
        "b": b,
        "date_mesure": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "photo_repos": photo_repos
    }

    file_path = "historique_couleur.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df = pd.concat([ df, pd.DataFrame([row])], ignore_index=True )
    else:
        df = pd.DataFrame([row])

    df.to_csv( file_path, index=False )