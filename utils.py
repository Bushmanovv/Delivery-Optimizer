import random
from models import Package, Vehicle
import streamlit as st
import pandas as pd
from io import StringIO  # Keep support for text-based input

def generate_test_data(num_packages, num_vehicles, vehicle_capacity, seed=None):
    if seed is not None:
        random.seed(seed)

    # Generate vehicles
    vehicles = [Vehicle(id=i, capacity=vehicle_capacity) for i in range(num_vehicles)]

    # Generate packages with random positions, weights, and priorities
    packages = []
    for i in range(num_packages):
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        weight = round(random.uniform(1, 10), 2)
        priority = random.randint(1, 5)
        packages.append(Package(id=i, x=x, y=y, weight=weight, priority=priority))

    return packages, vehicles

def load_data_from_file(filepath):
    packages = []
    vehicles = []
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        # First line: number of vehicles and vehicle capacity
        vehicle_info = lines[0].split()
        num_vehicles = int(vehicle_info[0])
        vehicle_capacity = float(vehicle_info[1])
        vehicles = [Vehicle(id=i, capacity=vehicle_capacity) for i in range(num_vehicles)]

        # Remaining lines: package info
        for line in lines[1:]:
            parts = line.split()
            if len(parts) == 5:
                pid, x, y, weight, priority = parts
                packages.append(Package(
                    id=int(pid),
                    x=float(x),
                    y=float(y),
                    weight=float(weight),
                    priority=int(priority)
                ))

    return packages, vehicles


def manual_input_flow():
    st.subheader("✏️ Manual Package Entry ")

    # Initialize session state
    if "manual_table" not in st.session_state:
        st.session_state.manual_table = []
        st.session_state.pkgs_ready = False

    # === Sidebar Input for Vehicles
    if "n_vehicles" not in st.session_state:
        st.session_state.n_vehicles = 3
    if "v_capacity" not in st.session_state:
        st.session_state.v_capacity = 50

    st.session_state.n_vehicles = st.sidebar.slider("How many vehicles?", 1, 10, st.session_state.n_vehicles)
    st.session_state.v_capacity = st.sidebar.slider("Vehicle capacity (kg)", 10, 100, st.session_state.v_capacity)

    # === Package Entry Form
    with st.form("add_row_form"):
        col1, col2, col3, col4, col5 = st.columns(5)
        id_val = col1.number_input("ID", min_value=0, step=1, key="id_input")
        x_val = col2.number_input("X", step=1.0, key="x_input")
        y_val = col3.number_input("Y", step=1.0, key="y_input")
        weight_val = col4.number_input("Weight", min_value=0.1, step=1.0, key="w_input")
        priority_val = col5.number_input("Priority", min_value=1, max_value=5, step=1, key="p_input")
        add_btn = st.form_submit_button("➕ Add Row")

        if add_btn:
            if any(pkg["ID"] == id_val for pkg in st.session_state.manual_table):
                st.error(f"❌ Package ID {id_val} already exists. Please use a unique ID.")
            else:
                st.session_state.manual_table.append({
                    "ID": id_val,
                    "X": x_val,
                    "Y": y_val,
                    "Weight": weight_val,
                    "Priority": priority_val
                })
                st.success(f"✅ Added package ID {id_val}")

    # === Auto-Save unsaved row if valid, unique, and NOT the untouched default row
    unsaved = {
        "ID": st.session_state.get("id_input"),
        "X": st.session_state.get("x_input"),
        "Y": st.session_state.get("y_input"),
        "Weight": st.session_state.get("w_input"),
        "Priority": st.session_state.get("p_input")
    }
    is_default = unsaved == {"ID": 0, "X": 0.0, "Y": 0.0, "Weight": 0.1, "Priority": 1}

    if not is_default and all(v is not None for v in unsaved.values()) and not any(pkg["ID"] == unsaved["ID"] for pkg in st.session_state.manual_table):
        if st.session_state.get("auto_saved") != unsaved:
            st.session_state.manual_table.append(unsaved)
            st.session_state.auto_saved = unsaved
            st.info(f"ℹ️ Auto-saved unsaved row ID {unsaved['ID']}")

    # === Show Table
    if st.session_state.manual_table:
        st.dataframe(pd.DataFrame(st.session_state.manual_table))

        if st.button("✅ Confirm & Proceed"):
            try:
                pkgs = [
                    Package(int(r["ID"]), float(r["X"]), float(r["Y"]), float(r["Weight"]), int(r["Priority"]))
                    for r in st.session_state.manual_table
                ]
                st.session_state.confirmed_packages = pkgs
                st.session_state.vehs = [Vehicle(i, st.session_state.v_capacity) for i in range(st.session_state.n_vehicles)]
                st.session_state.pkgs_ready = True
                st.success(f"🚚 Registered {len(pkgs)} packages successfully.")
            except Exception as e:
                st.error(f"❌ Error in data: {e}")

    if st.session_state.get("pkgs_ready", False):
        return st.session_state.confirmed_packages, st.session_state.vehs

    return [], []