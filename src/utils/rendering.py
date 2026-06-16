import plotly.graph_objects as go
import numpy as np


def _interpolate_color(norm_v: float) -> str:
    """Red-to-amber-to-green mapping for neuro-score from 0.0 to 1.0."""
    norm_v = max(0.0, min(1.0, float(norm_v)))
    anchors = [
        (0.0, (255, 107, 138)),
        (0.5, (246, 199, 109)),
        (1.0, (56, 211, 159)),
    ]

    left, right = anchors[0], anchors[-1]
    for idx in range(len(anchors) - 1):
        if anchors[idx][0] <= norm_v <= anchors[idx + 1][0]:
            left, right = anchors[idx], anchors[idx + 1]
            break

    span = max(right[0] - left[0], 1e-6)
    ratio = (norm_v - left[0]) / span
    rgb = tuple(int(left[1][i] + ratio * (right[1][i] - left[1][i])) for i in range(3))
    return f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"


def render_3d_room(length, width, height, valence=None):
    """
    Renders a 3D Cuboid using Plotly.
    Color changes based on predicted Valence (Blue/Green=Positive, Red=Negative).
    Valence range: -1.0 (Bad) to 1.0 (Good).
    """
    
    # Define vertices of a cuboid
    x = [0, length, length, 0, 0, length, length, 0]
    y = [0, 0, width, width, 0, 0, width, width]
    z = [0, 0, 0, 0, height, height, height, height]
    
    # Define indices for mesh triangles (standard cube triangulation)
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    
    # Map Valence (-1 to 1) to Color
    if valence is not None:
        norm_v = (valence + 1.0) / 2.0
        norm_v = max(0.0, min(1.0, norm_v))
    else:
        norm_v = 0.5

    color_hex = _interpolate_color(norm_v)

    fig = go.Figure()
    fig.add_trace(
        go.Mesh3d(
            x=x,
            y=y,
            z=z,
            i=i,
            j=j,
            k=k,
            opacity=0.42,
            color=color_hex,
            flatshading=False,
            lighting=dict(ambient=0.55, diffuse=0.8, fresnel=0.12, roughness=0.22, specular=0.5),
            lightposition=dict(x=120, y=200, z=280),
            name="Spatial Envelope",
            hovertemplate="Length: %{x:.2f} m<br>Width: %{y:.2f} m<br>Height: %{z:.2f} m<extra></extra>",
        )
    )

    # Draw explicit room edges for a cleaner architectural read.
    edge_pairs = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    ]
    for a, b in edge_pairs:
        fig.add_trace(
            go.Scatter3d(
                x=[x[a], x[b]],
                y=[y[a], y[b]],
                z=[z[a], z[b]],
                mode="lines",
                line=dict(color="#4F8BF9", width=5),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    max_dim = max(length, width, 1.0)
    grid_limit = max(max_dim * 1.15, 12.0)
    grid_step = max(1, int(round(grid_limit / 10.0)))
    grid_points = np.arange(0, grid_limit + grid_step, grid_step)

    for gx in grid_points:
        fig.add_trace(
            go.Scatter3d(
                x=[gx, gx],
                y=[0, grid_limit],
                z=[0, 0],
                mode="lines",
                line=dict(color="rgba(255, 255, 255, 0.1)", width=1),
                hoverinfo="skip",
                showlegend=False,
            )
        )
    for gy in grid_points:
        fig.add_trace(
            go.Scatter3d(
                x=[0, grid_limit],
                y=[gy, gy],
                z=[0, 0],
                mode="lines",
                line=dict(color="rgba(255, 255, 255, 0.1)", width=1),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    score = (float(valence) + 1.0) / 2.0 if valence is not None else None
    score_label = f"Neuro-Score {score:.2f}" if score is not None else "Neuro-Score Pending"
    limit_z = max(height * 1.45, 6.0)

    fig.update_layout(
        title={"text": score_label, "x": 0.02, "font": {"size": 16, "color": "#FAFAFA"}},
        scene=dict(
            xaxis=dict(
                range=[-0.8, grid_limit],
                title=dict(text="Length (m)", font=dict(color="#FAFAFA")),
                showbackground=True,
                backgroundcolor="rgba(0,0,0,0)",
                gridcolor="rgba(255, 255, 255, 0.1)",
                zerolinecolor="rgba(255, 255, 255, 0.2)",
                tickfont=dict(color="#FAFAFA"),
            ),
            yaxis=dict(
                range=[-0.8, grid_limit],
                title=dict(text="Width (m)", font=dict(color="#FAFAFA")),
                showbackground=True,
                backgroundcolor="rgba(0,0,0,0)",
                gridcolor="rgba(255, 255, 255, 0.1)",
                zerolinecolor="rgba(255, 255, 255, 0.2)",
                tickfont=dict(color="#FAFAFA"),
            ),
            zaxis=dict(
                range=[0, limit_z],
                title=dict(text="Height (m)", font=dict(color="#FAFAFA")),
                showbackground=True,
                backgroundcolor="rgba(0,0,0,0)",
                gridcolor="rgba(255, 255, 255, 0.1)",
                zerolinecolor="rgba(255, 255, 255, 0.2)",
                tickfont=dict(color="#FAFAFA"),
            ),
            aspectmode="manual",
            aspectratio=dict(
                x=max(length, 1.0) / max_dim,
                y=max(width, 1.0) / max_dim,
                z=max(height, 1.0) / max_dim,
            ),
            camera=dict(eye=dict(x=1.45, y=1.55, z=0.85)),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FAFAFA"),
        margin=dict(r=0, l=0, b=0, t=0),
        showlegend=False,
        height=460,
    )

    return fig


def render_2d_affective_map(val, aro, centroids=None):
    """
    Renders a 2D plot of Valence (X) vs Arousal (Y) with colored quadrants.
    Supports trajectory arrays (val, aro) over time, as per Nature paper emotion maps.
    """
    if isinstance(val, (list, np.ndarray)) and isinstance(aro, (list, np.ndarray)):
        val_list = val
        aro_list = aro
    else:
        val_list = [val]
        aro_list = [aro]

    fig = go.Figure()

    quadrants = [
        (0, 0, 1.2, 1.2, "rgba(47,212,200,0.10)", "Engaged Positive"),
        (-1.2, 0, 0, 1.2, "rgba(255,107,138,0.10)", "Activated Stress"),
        (-1.2, -1.2, 0, 0, "rgba(79,124,255,0.10)", "Low-Energy Negative"),
        (0, -1.2, 1.2, 0, "rgba(139,124,255,0.10)", "Calm Positive"),
    ]
    for x0, y0, x1, y1, fillcolor, _ in quadrants:
        fig.add_shape(
            type="rect",
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
            fillcolor=fillcolor,
            line=dict(width=0),
            layer="below",
        )

    # Axes lines
    fig.add_hline(y=0, line=dict(color="rgba(255, 255, 255, 0.2)", width=1, dash="dot"))
    fig.add_vline(x=0, line=dict(color="rgba(255, 255, 255, 0.2)", width=1, dash="dot"))

    labels = [
        (1.16, 1.14, "Q1 • ENGAGED POSITIVE", "right", "top", "rgba(47,212,200,0.22)", "rgba(47,212,200,0.55)"),
        (-1.16, 1.14, "Q2 • ACTIVATED STRESS", "left", "top", "rgba(255,107,138,0.22)", "rgba(255,107,138,0.55)"),
        (-1.16, -1.14, "Q3 • LOW-ENERGY NEGATIVE", "left", "bottom", "rgba(79,124,255,0.22)", "rgba(79,124,255,0.55)"),
        (1.16, -1.14, "Q4 • CALM POSITIVE", "right", "bottom", "rgba(139,124,255,0.22)", "rgba(139,124,255,0.55)"),
    ]
    for lx, ly, txt, xanchor, yanchor, bgcolor, bordercolor in labels:
        fig.add_annotation(
            x=lx,
            y=ly,
            text=txt,
            showarrow=False,
            xanchor=xanchor,
            yanchor=yanchor,
            font=dict(color="rgba(232,236,247,0.95)", size=10),
            bgcolor=bgcolor,
            bordercolor=bordercolor,
            borderwidth=1,
            borderpad=4,
        )

    # Plot Reference Centroids
    if centroids:
        c_names = list(centroids.keys())
        c_x = [v[0] for v in centroids.values()]
        c_y = [v[1] for v in centroids.values()]
        
        fig.add_trace(go.Scatter(
            x=c_x, y=c_y, mode='markers+text',
            text=c_names, textposition="top center",
            marker=dict(size=8, color='rgba(167,177,203,0.85)', line=dict(color='rgba(9,11,18,0.95)', width=1)),
            textfont=dict(size=10, color='rgba(220,226,241,0.92)'),
            hoverinfo='text', name='Reference'
        ))

    # Plot Trajectory (if multiple points)
    if len(val_list) > 1:
        fig.add_trace(go.Scatter(
            x=val_list, y=aro_list, mode='lines+markers',
            line=dict(width=3, color='rgba(139,124,255,0.70)', dash='dot'),
            marker=dict(size=6, color='rgba(139,124,255,0.95)'),
            name='Trajectory'
        ))

    # Plot Current (Final) Prediction
    fig.add_trace(go.Scatter(
        x=[val_list[-1]], y=[aro_list[-1]], mode='markers',
        marker=dict(size=16, color='#4F8BF9', symbol='circle', line=dict(width=2, color='#FAFAFA')),
        name='Result (End State)'
    ))

    fig.update_layout(
        width=440,
        height=360,
        xaxis=dict(
            range=[-1.2, 1.2],
            title=dict(text="Valence", font=dict(color="#FAFAFA")),
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(255, 255, 255, 0.1)",
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor="rgba(255, 255, 255, 0.2)",
            tickfont=dict(color="#FAFAFA"),
        ),
        yaxis=dict(
            range=[-1.2, 1.2],
            title=dict(text="Arousal", font=dict(color="#FAFAFA")),
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(255, 255, 255, 0.1)",
            zeroline=False,
            tickfont=dict(color="#FAFAFA"),
        ),
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FAFAFA')
    )
    return fig
