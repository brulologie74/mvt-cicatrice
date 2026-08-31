import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from config import *


def build_rgb_population_graph(df_color):
    df = df_color.copy()
    total = ( df["r"] + df["g"] + df["b"]    )
    df["r_pct"] = ( df["r"] / total ) * 100
    df["g_pct"] = ( df["g"] / total ) * 100
    df["b_pct"] = ( df["b"] / total ) * 100
    
    ordre = { "J0":0, "J09":1, "J18":2 }
    
    df["sort_jour"] = ( df["jour"].map(ordre))
    df = df.sort_values( ["patient_id","sort_jour" ] )
    x_labels = []
    r_values = []
    g_values = []
    b_values = []

    current_patient = None

    for _, row in df.iterrows():
        patient = row["patient_id"]
        if (
            current_patient is not None
            and patient != current_patient
        ):
            x_labels.append(" ")
            r_values.append(None)
            g_values.append(None)
            b_values.append(None)
        x_labels.append(f"{patient}\n{row['jour']}" )
        r_values.append( row["r_pct"] )
        g_values.append( row["g_pct"] )
        b_values.append( row["b_pct"] )
        current_patient = patient

    fig = go.Figure()

    fig.add_trace( go.Scatter( x=x_labels, y=r_values, mode="lines+markers", name="Rouge", line=dict( color="red", width=3 ) ) )
    fig.add_trace( go.Scatter( x=x_labels, y=g_values, mode="lines+markers", name="Vert", line=dict( color="darkgreen", width=3 ) ) )
    fig.add_trace( go.Scatter( x=x_labels, y=b_values, mode="lines+markers", name="Bleu", line=dict( color="royalblue", width=3 ) ) )

    # -------------------------
    # Références caucasiennes
    # -------------------------
    REF_R = 40.0
    REF_G = 32.5
    REF_B = 27.5

    fig.add_hline( y=REF_R, line_color="red", opacity=0.2, line_width=10, annotation_text="R" )
    fig.add_hline( y=REF_G, line_color="green", opacity=0.2, line_width=10, annotation_text="G" )
    fig.add_hline( y=REF_B, line_color="blue", opacity=0.2, line_width=10, annotation_text="B" )

    fig.update_layout(  title="Colorimétrie", height=500, yaxis_title="% RGB", yaxis=dict( ticksuffix="%" ), legend=dict( orientation="h", y=-0.2 ))

    return fig
        
def build_deformation_bar_chart(
    df,
    metric
):

    pivot = df.pivot_table(  index="patient_id", columns="jour", values=metric, aggfunc="mean" )

    # assure l'ordre des colonnes
    jours = ["J0", "J9", "J18"]
    for jour in jours:
        if jour not in pivot.columns:
            pivot[jour] = None

    pivot = pivot[jours]
    fig = go.Figure()
    fig.add_trace( go.Bar( name="J0", x=pivot.index, y=pivot["J0"], marker_color="#f7c1bd" ) )
    fig.add_trace( go.Bar( name="J9", x=pivot.index, y=pivot["J9"], marker_color="#fde3d7" ) )
    fig.add_trace( go.Bar( name="J18", x=pivot.index, y=pivot["J18"], marker_color="#8dd974" ) )

    fig.update_layout(
        title="Déformation",
        barmode="group",
        xaxis_title="Patient",
        yaxis_title="Variation (%)",
        legend_title="Jour",
        height=300
    )

    return fig    