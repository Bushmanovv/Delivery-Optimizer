import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
import time

from utils import generate_test_data, load_data_from_file, manual_input_flow
from sa import simulated_annealing
from ga import genetic_algorithm

from models import Package, Vehicle

# ------------------------------------------------------------------
# Streamlit Page Config
# ------------------------------------------------------------------
st.set_page_config(page_title="Delivery Optimizer", layout="wide")

# ------------------------------------------------------------------
# Session-state init
# ------------------------------------------------------------------
if "landing_done" not in st.session_state:
    st.session_state.landing_done = False
if "pkgs" not in st.session_state:
    st.session_state.pkgs = []
if "vehs" not in st.session_state:
    st.session_state.vehs = []

# ------------------------------------------------------------------
# Helper: encode author photos
# ------------------------------------------------------------------
def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# ------------------------------------------------------------------
# Landing page
# ------------------------------------------------------------------
if not st.session_state.landing_done:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {transform: translateX(-100%); transition: transform 1s ease-in-out;}
        @keyframes fadeInUp {from {opacity: 0; transform: translateY(50px);} to {opacity: 1; transform: translateY(0);}}
        .landing {animation: fadeInUp 1.5s ease-out forwards; text-align: center; padding-top: 100px; opacity: 0;}
        .proceed-btn button {background-color: #2a9d8f; color: white; font-size: 18px;
                             padding: 0.7em 2em; border: none; border-radius: 10px; margin-top: 30px; transition: .4s;}
        .proceed-btn button:hover {background-color: #21867a; transform: scale(1.05);}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="landing">
            <h1 style="font-size: 3rem; color: #264653;">🚚 Welcome to the Delivery Optimizer Project</h1>
            <p style="font-size: 1.5rem; color: #666;">Optimize your local package delivery using AI techniques</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("👉 Proceed", key="proceed_button"):
        with st.spinner("Preparing the dashboard..."):
            time.sleep(1.2)
        st.session_state.landing_done = True
        st.rerun()

    st.stop()

# ------------------------------------------------------------------
# Sidebar animation / style
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    @keyframes slideSidebar {0% {transform: translateX(-100%); opacity: 0;}100% {transform: translateX(0); opacity: 1;}}
    [data-testid="stSidebar"] {animation: slideSidebar 2.5s cubic-bezier(.25,.8,.25,1) forwards;}

    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #0f4c5c, #1a5e63);
        color: white;
        padding: 10px 20px 30px 20px;
        border-right: 3px solid #0a3d45;
        display: flex; flex-direction: column; align-items: center;
    }

    .stButton>button {background-color:#2a9d8f;color:white;border:none;padding:.6em 1.2em;
                       border-radius:8px;font-size:16px;transition:.3s;}
    .stButton>button:hover {background-color:#21867a;transform:scale(1.05);}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Header with authors
# ------------------------------------------------------------------
img1_b64 = encode_image_to_base64("1.jpeg")
img2_b64 = encode_image_to_base64("2.jpeg")


st.markdown(
    f"""
    <div style="margin-top:60px;display:flex;justify-content:space-between;align-items:center;padding-bottom:30px;">
        <h1 style="margin:0;font-size:2.5rem;">📦 Delivery Optimizer Project</h1>
        <div style="display:flex;gap:30px;">
            <div style="text-align:center;">
                <img src="data:image/jpeg;base64,{img1_b64}"
                     style="width:100px;height:100px;border-radius:50%;border:2px solid #ccc;" />
                <div style="font-size:13px;color:white;margin-top:4px;">Mohammad Abu Shamah</div>
            </div>
            <div style="text-align:center;">
                <img src="data:image/jpeg;base64,{img2_b64}"
                     style="width:100px;height:100px;border-radius:50%;border:2px solid #ccc;" />
                <div style="font-size:13px;color:white;margin-top:4px;">Abdalkarim Dwikat</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Sidebar controls
# ------------------------------------------------------------------
st.sidebar.image("birzeit_logo.png", width=300)

#  Data-source selector — first entry is a placeholder, so nothing is chosen by default
data_source = st.sidebar.radio(
    "🗂️ Data Source",
    ["Generate Random", "Manual Input", "Load from File"],
    key="source_select",
    index=None          # ← works only on 1.29+
)


# Algorithm selector
algo_choice = st.sidebar.radio("🧠 Algorithm", ["Simulated Annealing", "Genetic Algorithm"], key="algo_choice")


# ===== ADD THE GUARD RIGHT HERE =====
if data_source is None:
    st.markdown("### 📝 Choose a **Data Source** from the sidebar to begin.")
    st.stop()

# ------------------------------------------------------------------
# Data-handling logic (runs only when a real source is picked)
# ------------------------------------------------------------------
if data_source == "Generate Random":
    n_packages  = st.sidebar.slider("How many packages?", 5, 50, 20)
    n_vehicles  = st.sidebar.slider("How many vehicles?", 1, 10, 3)
    v_capacity  = st.sidebar.slider("Vehicle capacity (kg)", 10, 100, 50)
    r_seed      = st.sidebar.number_input("Random Seed (0 for random)", min_value=0, value=0, step=1)

    st.session_state.pkgs, st.session_state.vehs = generate_test_data(
        n_packages, n_vehicles, v_capacity, seed=r_seed if r_seed != 0 else None
    )

    pkgs, vehs = st.session_state.pkgs, st.session_state.vehs
    if pkgs and vehs:
        st.subheader("📦 Packages ")
        st.dataframe(
            pd.DataFrame(
                {
                    "ID":       [p.id for p in pkgs],
                    "X":        [p.x for p in pkgs],
                    "Y":        [p.y for p in pkgs],
                    "Weight":   [p.weight for p in pkgs],
                    "Priority": [p.priority for p in pkgs],
                }
            ),
            hide_index=True,
            use_container_width=True,
        )

        st.subheader("🚚 Vehicles ")
        st.dataframe(
            pd.DataFrame(
                {
                    "ID":       [v.id for v in vehs],
                    "Capacity": [v.capacity for v in vehs],
                }
            ),
            hide_index=True,
            use_container_width=True,
        )

elif data_source == "Manual Input":
    pkgs, vehs = manual_input_flow()

    # …and stash it in session-state so the rest of the script can see it
    st.session_state.pkgs  = pkgs
    st.session_state.vehs  = vehs

    # If the user hasn’t clicked “Confirm & Proceed” yet,
    # manual_input_flow() returns empty lists – stop here until they do.
    if not pkgs or not vehs:
        st.stop()


elif data_source == "Load from File":
    uploaded_file = st.sidebar.file_uploader("📄 Upload Input File", type=["txt"])
    if uploaded_file:
        with open("uploaded_input.txt", "wb") as f:
            f.write(uploaded_file.read())
        st.session_state.pkgs, st.session_state.vehs = load_data_from_file("uploaded_input.txt")
    else:
        st.warning("Please upload a valid .txt file before continuing.")
        st.stop()

# ------------------------------------------------------------------
# Pull back to local vars for clarity
# ------------------------------------------------------------------
pkgs = st.session_state.pkgs
vehs = st.session_state.vehs

# ------------------------------------------------------------------
# Main-page prompt OR optimisation interface
# ------------------------------------------------------------------
if not pkgs or not vehs:
    st.markdown(
        """
        ### 📝 Choose a **Data Source** from the sidebar to begin.
        Once data are loaded, you’ll see the optimisation controls here.
        """,
        unsafe_allow_html=True,
    )
    st.stop()  # don’t render anything else until user chooses a source

# -----  Adapt algorithm-specific hyper-parameters  ------------------
if algo_choice == "Genetic Algorithm":
    st.sidebar.markdown("### ⚙️ GA Parameters")
    population_size = st.sidebar.slider("Population Size", 20, 300, 80, step=10, key="ga_pop")
    mutation_rate   = st.sidebar.slider("Mutation Rate", 0.01, 0.30, 0.05, step=0.01, format="%.2f", key="ga_mut")
    generations     = st.sidebar.slider("Generations", 100, 2000, 500, step=100, key="ga_gen")
else:  # Simulated Annealing
    st.sidebar.markdown("### ⚙️ SA Parameters")
    cool_rate = st.sidebar.slider("Cooling Rate", 0.90, 0.99, 0.95, step=0.01, key="sa_cool")
    initial_temp, stop_temp, iter_temp = 1000, 1, 100



# ------------------------------------------------------------------
# Start optimisation section (shows only when data exist)
# ------------------------------------------------------------------
if st.button("🚀 Start Optimization"):
    with st.spinner("Optimizing..."):
        if algo_choice == "Simulated Annealing":
            solution = simulated_annealing(pkgs, vehs, initial_temp, cool_rate, stop_temp, iter_temp)
        else:
            solution = genetic_algorithm(pkgs, vehs, population_size, mutation_rate, generations)

    # ✅ Results summary
    st.success(f"Optimization complete using **{algo_choice}**")
    st.markdown(f"### 📏 Total Distance: `{solution.total_distance():.2f} km`")

    for v in solution.vehicles:
        st.markdown(f"**🚚 Vehicle {v.id}** — Load `{v.current_load():.1f}/{v.capacity}` kg")
        st.write("Packages:", ", ".join(f"ID {p.id} (P{p.priority})" for p in v.packages))

    # ------------------------------------------------------------------
    # Animated route plot
    # ------------------------------------------------------------------
    st.subheader("🚚 Animated Route Progression")

    palette = ["red", "blue", "green", "orange", "purple"]
    frames, init_traces, emoji_traces = [], [], []
    max_pts = max(len(v.route()) for v in solution.vehicles)

    for i, v in enumerate(solution.vehicles):
        color = palette[i % len(palette)]
        x0, y0 = zip(*v.route()[:1])
        init_traces.append(go.Scatter(
            x=x0, y=y0, mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(size=8, color=color),
            name=f"Vehicle {v.id}"))
        emoji_traces.append(go.Scatter(
            x=x0, y=y0, mode="text",
            text=["🚚"], textposition="top center",
            textfont=dict(color="white", size=16)))

    for step in range(1, max_pts + 1):
        fdata = []
        for i, v in enumerate(solution.vehicles):
            color = palette[i % len(palette)]
            route = v.route()
            x, y = zip(*route[:step]) if step <= len(route) else zip(*route)
            fdata.append(go.Scatter(
                x=x, y=y, mode="lines+markers",
                line=dict(color=color, width=2),
                marker=dict(size=8, color=color),
                name=f"Vehicle {v.id}"))
            if step <= len(route):
                fdata.append(go.Scatter(
                    x=[route[step-1][0]], y=[route[step-1][1]],
                    mode="text", text=["🚚"], textposition="top center",
                    textfont=dict(color="white", size=16)))
        frames.append(go.Frame(data=fdata, name=str(step)))

    fig = go.Figure(
        data=init_traces + emoji_traces,
        layout=go.Layout(
            paper_bgcolor="#000", plot_bgcolor="#000",
            title=dict(text="Animated Vehicle Routes", font=dict(color="white")),
            xaxis=dict(range=[-5, 105],
                       title=dict(text="X (km)", font=dict(color="white")),
                       tickfont=dict(color="white"), gridcolor="gray"),
            yaxis=dict(range=[-5, 105],
                       title=dict(text="Y (km)", font=dict(color="white")),
                       tickfont=dict(color="white"), gridcolor="gray"),
            legend=dict(font=dict(color="white")),  # legend labels white
            updatemenus=[{
                "type": "buttons", "x": 0.1, "y": -0.15,
                "buttons": [
                    {"label": "▶ Play", "method": "animate",
                     "args": [None, {"frame": {"duration": 1200, "redraw": True}}]},
                    {"label": "⏸ Pause", "method": "animate",
                     "args": [[None], {"mode": "immediate",
                                       "frame": {"duration": 0},
                                       "transition": {"duration": 0}}]},
                ],
            }],
        ),
        frames=frames,
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------
st.markdown("---")
st.markdown("**👨‍💼 Authors:** Abdalkarim Dwikat `1210288` • Mohammad Abu Shamah `1200270`")
