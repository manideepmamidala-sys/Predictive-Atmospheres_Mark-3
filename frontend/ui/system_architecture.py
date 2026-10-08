import streamlit as st
import plotly.graph_objects as go

def render_system_architecture():
    st.subheader("Scientific ML Architecture & Data Pipelines")
    
    st.markdown('<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,100,0,0" rel="stylesheet">', unsafe_allow_html=True)
    
    nodes = {
        "VR": {"icon": "visibility", "label": "VR Space Exposure", "x": 0.5, "y": 10},
        "EEG": {"icon": "psychology", "label": "EEG (F3/F4)", "x": 0.3, "y": 9},
        "ECG": {"icon": "monitor_heart", "label": "ECG Signal", "x": 0.5, "y": 9},
        "SAM": {"icon": "assignment", "label": "SAM Questionnaires", "x": 0.7, "y": 9},
        "AB_Ext": {"icon": "waves", "label": "Alpha (α) & Beta (β)<br>Extraction", "x": 0.3, "y": 8},
        "HRV_Ext": {"icon": "monitor_heart", "label": "HRV / R-Peak<br>Extraction", "x": 0.5, "y": 8},
        "Obj_V": {"icon": "sentiment_satisfied", "label": "Objective<br>Valence", "x": 0.2, "y": 7},
        "BA_HRV": {"icon": "functions", "label": "Beta/Alpha Ratio<br>+ HRV", "x": 0.5, "y": 7},
        "Subj_C": {"icon": "tune", "label": "Subjective<br>Calibration", "x": 0.8, "y": 7},
        "Obj_A": {"icon": "speed", "label": "Objective<br>Arousal", "x": 0.5, "y": 6},
        "SSOT": {"icon": "calculate", "label": "Neuro-Score<br>Calculation (SSOT)", "x": 0.5, "y": 5},
        "Spatial": {"icon": "architecture", "label": "11 Spatial<br>Parameters", "x": 0.8, "y": 5},
        "RF": {"icon": "forest", "label": "Random Forest<br>Ensemble Hub", "x": 0.5, "y": 4},
        "T1_Root": {"icon": "account_tree", "label": "Tree 1<br>[Height < 3.0m]", "x": 0.15, "y": 3},
        "T2_Root": {"icon": "account_tree", "label": "Tree 2<br>[Daylight Factor < 0.4]", "x": 0.5, "y": 3},
        "TN_Root": {"icon": "account_tree", "label": "Tree N<br>[Window Area < 5m²]", "x": 0.85, "y": 3},
        "T1_L": {"label": "[Volume > 150m³]", "x": 0.05, "y": 2},
        "T1_R": {"label": "[Walkable Area < 20m²]", "x": 0.25, "y": 2},
        "T2_L": {"label": "[CCT_K > 4000]", "x": 0.4, "y": 2},
        "T2_R": {"label": "[Illuminance < 300lux]", "x": 0.6, "y": 2},
        "TN_L": {"label": "[Door Area < 2m²]", "x": 0.75, "y": 2},
        "TN_R": {"label": "[Day_or_Night]", "x": 0.95, "y": 2},
        "Agg": {"icon": "hub", "label": "Ensemble Aggregation<br>(Mean / Voting)", "x": 0.5, "y": 1},
        "Output": {"icon": "insights", "label": "Predictive Output:<br>Atmosphere", "x": 0.5, "y": 0}
    }
    
    edges = [
        ("VR", "EEG"), ("VR", "ECG"), ("VR", "SAM"),
        ("EEG", "AB_Ext"), ("ECG", "HRV_Ext"),
        ("AB_Ext", "Obj_V"), ("AB_Ext", "BA_HRV"),
        ("HRV_Ext", "BA_HRV"),
        ("BA_HRV", "Obj_A"),
        ("SAM", "Subj_C"),
        ("Obj_V", "SSOT"), ("Obj_A", "SSOT"), ("Subj_C", "SSOT"),
        ("SSOT", "RF"), ("Spatial", "RF"),
        ("RF", "T1_Root"), ("RF", "T2_Root"), ("RF", "TN_Root"),
        ("T1_Root", "T1_L"), ("T1_Root", "T1_R"),
        ("T2_Root", "T2_L"), ("T2_Root", "T2_R"),
        ("TN_Root", "TN_L"), ("TN_Root", "TN_R"),
        ("T1_L", "Agg"), ("T1_R", "Agg"), ("T2_L", "Agg"), ("T2_R", "Agg"), ("TN_L", "Agg"), ("TN_R", "Agg"),
        ("Agg", "Output")
    ]
    
    edge_x = []
    edge_y = []
    for source, target in edges:
        x0, y0 = float(nodes[source]["x"]), float(nodes[source]["y"])
        x1, y1 = float(nodes[target]["x"]), float(nodes[target]["y"])
        
        if target == "SSOT" and source in ["Obj_V", "Subj_C"]:
            mid_y = 5.3  # Drop completely beneath Obj_A text
        else:
            mid_y = y0 - (y0 - y1) * 0.7
            
        edge_x.extend([x0, x0, x1, x1, None])
        edge_y.extend([y0, mid_y, mid_y, y1, None])
        
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=1.5, color='#B0B0B0'),
        hoverinfo='none'
    )
    
    node_x_icons, node_y_icons, node_icons = [], [], []
    node_x_labels, node_y_labels, node_labels = [], [], []
    
    for k, v in nodes.items():
        if "icon" in v:
            node_x_icons.append(float(v["x"]))
            node_y_icons.append(float(v["y"]))
            node_icons.append(v["icon"])
            node_x_labels.append(float(v["x"]))
            node_y_labels.append(float(v["y"]) - 0.4)
            node_labels.append(v["label"])
        else:
            # Render leaf nodes as text-only natively
            node_x_labels.append(float(v["x"]))
            node_y_labels.append(float(v["y"]))
            node_labels.append(v["label"])
    
    node_trace_icons = go.Scatter(
        x=node_x_icons, y=node_y_icons,
        mode='markers+text',
        marker=dict(
            size=45,
            color='#0E1117',
            line=dict(color='white', width=1.5)
        ),
        text=node_icons,
        textposition='middle center',
        textfont=dict(family='Material Symbols Outlined', size=24, color='white'),
        hoverinfo='none'
    )
    
    node_trace_labels = go.Scatter(
        x=node_x_labels, y=node_y_labels,
        mode='text',
        text=node_labels,
        textposition='middle center',
        textfont=dict(family='Inter, sans-serif', size=12, color='white'),
        hoverinfo='none'
    )
    
    fig = go.Figure(data=[edge_trace, node_trace_icons, node_trace_labels],
                 layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False, range=[-0.1, 1.1]),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False, range=[-1, 11]),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=1000
                 ))
                 
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})

