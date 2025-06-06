import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ----------------------------
# Helper functions: calculations
# ----------------------------
def calculate_design(params):
    """
    Given a dict of input parameters, compute:
      - pontoon geometry (volumes, surface areas)
      - weights (foam, coating, frame)
      - buoyancy / safety factors
      - draft, displacement, etc.
    Returns a dict of computed values and explanatory strings.
    """
    # Unpack inputs
    payload = params['payload']
    safety_factor = params['safety_factor']
    submersion_pct = params['submersion_pct'] / 100.0
    diameter_in = params['diameter_in']
    # Convert diameter to feet
    diameter_ft = diameter_in / 12.0
    length_ft = params['length_ft']
    cone_pct = params['cone_pct'] / 100.0
    foam_density = params['foam_density']  # lb/ft³
    coating_weight = params['coating_weight']  # lb/ft²
    water_density = params['water_density']  # lb/ft³
    cross_beam_length = params['cross_beam_length']  # ft
    num_cross_beams = params['num_cross_beams']
    tube_weight = params['tube_weight']  # lb/ft

    # 1) Pontoon geometry
    radius_ft = diameter_ft / 2.0
    cone_length_ft = length_ft * cone_pct
    cylinder_length_ft = length_ft * (1 - cone_pct)

    # Cylinder volume: π r² h
    cylinder_volume = 3.141592653589793 * radius_ft**2 * cylinder_length_ft
    # Cone volume: (1/3) π r² h
    cone_volume = (1.0 / 3.0) * 3.141592653589793 * radius_ft**2 * cone_length_ft
    total_volume_per_pontoon = cylinder_volume + cone_volume
    total_volume_both = 2 * total_volume_per_pontoon

    # Surface areas
    # Cylinder side area: 2 π r h
    cylinder_surface_area = 2 * 3.141592653589793 * radius_ft * cylinder_length_ft
    # Cone slant height: √(r² + h²)
    slant_height = (radius_ft**2 + cone_length_ft**2)**0.5
    # Cone lateral area: π r * slant_height
    cone_surface_area = 3.141592653589793 * radius_ft * slant_height
    # End cap: π r² (assume one circular end on the cone side)
    end_cap_area = 3.141592653589793 * radius_ft**2
    total_surface_area_per_pontoon = cylinder_surface_area + cone_surface_area + end_cap_area
    total_surface_area_both = 2 * total_surface_area_per_pontoon

    # 2) Weight calculations
    # Foam weight: volume × density
    foam_weight_per_pontoon = total_volume_per_pontoon * foam_density
    coating_weight_per_pontoon = total_surface_area_per_pontoon * coating_weight
    pontoon_weight = 2 * (foam_weight_per_pontoon + coating_weight_per_pontoon)

    # Frame weight: aluminum tubes
    total_tube_length = (num_cross_beams * cross_beam_length) + (2 * length_ft)
    frame_weight = total_tube_length * tube_weight

    # Total boat weight:
    total_boat_weight = payload + pontoon_weight + frame_weight

    # 3) Buoyancy and displacement
    submerged_volume_per_pontoon = total_volume_per_pontoon * submersion_pct
    total_buoyant_force = 2 * submerged_volume_per_pontoon * water_density

    required_displacement = total_boat_weight * safety_factor

    # Draft: how deep the pontoon sits, in feet (diameter × submersion fraction)
    draft_ft = diameter_ft * submersion_pct

    # Actual safety factor based on buoyancy:
    actual_safety_factor = total_buoyant_force / total_boat_weight
    reserve_buoyancy = total_buoyant_force - total_boat_weight

    # 4) Status
    if total_buoyant_force < required_displacement:
        status = 'INSUFFICIENT BUOYANCY'
    else:
        status = 'VIABLE'

    # Prepare explanatory texts
    explanation_steps = []

    explanation_steps.append(
        f"1) Pontoon Geometry:\n"
        f"   - Diameter = {diameter_in:.1f}\" ({diameter_ft:.2f} ft) → Radius = {radius_ft:.2f} ft.\n"
        f"   - Length = {length_ft:.2f} ft, of which {cone_pct*100:.1f}% is cone ({cone_length_ft:.2f} ft) and {100-cone_pct*100:.1f}% is cylinder ({cylinder_length_ft:.2f} ft)."
    )
    explanation_steps.append(
        f"   - Cylinder Volume = π r² h = {cylinder_volume:.2f} ft³.\n"
        f"   - Cone Volume = (1/3)π r² h = {cone_volume:.2f} ft³.\n"
        f"   - Total Volume per Pontoon = {total_volume_per_pontoon:.2f} ft³. → Both Pontoons = {total_volume_both:.2f} ft³."
    )
    explanation_steps.append(
        f"   - Cylinder Surface Area = 2π r h = {cylinder_surface_area:.2f} ft².\n"
        f"   - Cone Lateral Area = π r × slant height (slant = {slant_height:.2f} ft) = {cone_surface_area:.2f} ft².\n"
        f"   - End Cap Area = π r² = {end_cap_area:.2f} ft².\n"
        f"   - Total Surface Area per Pontoon = {total_surface_area_per_pontoon:.2f} ft². → Both Pontoons = {total_surface_area_both:.2f} ft²."
    )

    explanation_steps.append(
        f"2) Weight Calculations:\n"
        f"   - Foam Weight per Pontoon = Volume × Foam Density = {total_volume_per_pontoon:.2f} ft³ × {foam_density:.2f} lb/ft³ = {foam_weight_per_pontoon:.2f} lb.\n"
        f"   - Coating Weight per Pontoon = Surface Area × Coating Weight = {total_surface_area_per_pontoon:.2f} ft² × {coating_weight:.2f} lb/ft² = {coating_weight_per_pontoon:.2f} lb.\n"
        f"   - Pontoon Weight (both) = 2 × ({foam_weight_per_pontoon:.2f} + {coating_weight_per_pontoon:.2f}) = {pontoon_weight:.2f} lb.\n"
        f"   - Frame Weight = Total Tube Length ({total_tube_length:.2f} ft) × Tube Weight ({tube_weight:.2f} lb/ft) = {frame_weight:.2f} lb.\n"
        f"   - Payload = {payload:.2f} lb.\n"
        f"   - → Total Boat Weight = {payload:.2f} + {pontoon_weight:.2f} + {frame_weight:.2f} = {total_boat_weight:.2f} lb."
    )

    explanation_steps.append(
        f"3) Buoyancy & Safety:\n"
        f"   - Submerged Volume per Pontoon = {total_volume_per_pontoon:.2f} ft³ × {submersion_pct*100:.1f}% = {submerged_volume_per_pontoon:.2f} ft³.\n"
        f"   - Total Buoyant Force = 2 × {submerged_volume_per_pontoon:.2f} ft³ × Water Density ({water_density:.2f} lb/ft³) = {total_buoyant_force:.2f} lb.\n"
        f"   - Required Displacement (with Safety Factor {safety_factor:.2f}×) = {total_boat_weight:.2f} × {safety_factor:.2f} = {required_displacement:.2f} lb.\n"
        f"   - Actual Safety Factor = Buoyant Force / Total Weight = {total_buoyant_force:.2f} ÷ {total_boat_weight:.2f} = {actual_safety_factor:.2f}×.\n"
        f"   - Reserve Buoyancy = {total_buoyant_force:.2f} − {total_boat_weight:.2f} = {reserve_buoyancy:.2f} lb.\n"
        f"   - Draft = Diameter ({diameter_ft:.2f} ft) × Submersion Fraction ({submersion_pct:.2f}) = {draft_ft:.2f} ft ({draft_ft*12:.1f} in).\n"
        f"   - Status = {status}."
    )

    # Collect results
    results = {
        'total_boat_weight': total_boat_weight,
        'total_buoyant_force': total_buoyant_force,
        'actual_safety_factor': actual_safety_factor,
        'reserve_buoyancy': reserve_buoyancy,
        'draft_in': draft_ft * 12.0,
        'volume_per_pontoon': total_volume_per_pontoon,
        'cylinder_length': cylinder_length_ft,
        'cone_length': cone_length_ft,
        'pontoon_weight': pontoon_weight,
        'frame_weight': frame_weight,
        'total_volume_both': total_volume_both,
        'total_surface_area_both': total_surface_area_both,
        'total_tube_length': total_tube_length,
        'status': status,
        'explanation': "\n\n".join(explanation_steps)
    }
    return results

def optimize_design(params):
    """
    Given some primary params (payload, safety_factor, submersion_pct, water_density),
    compute an “optimized” diameter & length by assuming:
      - estimated total weight ≈ payload × 1.4
      - required displacement = estimated_weight × safety_factor
      - required submerged volume per pontoon = (required_displacement / 2) / (water_density × submersion_pct)
      - assume an L/D ratio of 4:1 (length:diameter) for hydrodynamic efficiency
    Returns new diameter_in (rounded) and length_ft.
    """
    payload = params['payload']
    safety_factor = params['safety_factor']
    submersion_pct = params['submersion_pct'] / 100.0
    water_density = params['water_density']

    estimated_weight = payload * 1.4
    required_disp = estimated_weight * safety_factor
    required_vol_per_pontoon = (required_disp / 2.0) / (water_density * submersion_pct)

    # Solve: required_vol = π (d/2)² × (Lₚ) × [assuming no cone for rough size]
    # But we want L/D = 4 → L = 4 D
    # So π (D/2)² (4 D) = required_vol  → (π/4) D² × 4D = π D³ = required_vol
    # → D³ = required_vol / π  → D = (required_vol/π)^(1/3)
    import math
    diameter_ft = (required_vol_per_pontoon / math.pi) ** (1.0 / 3.0)
    length_ft = diameter_ft * 4.0

    diameter_in = diameter_ft * 12.0

    return round(diameter_in), round(length_ft, 2)


# ----------------------------
# GUI application
# ----------------------------
class PontoonCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pontoon Boat Design Calculator")

        # -- Main frames --
        self.frame_inputs = ttk.Frame(root, padding="10 10 10 10")
        self.frame_inputs.grid(row=0, column=0, sticky="nsew")

        self.frame_buttons = ttk.Frame(root, padding="5 5 5 5")
        self.frame_buttons.grid(row=1, column=0, sticky="ew")

        self.frame_results = ttk.LabelFrame(root, text="Design Results", padding="10 10 10 10")
        self.frame_results.grid(row=2, column=0, sticky="nsew", pady=5)

        self.frame_chart = ttk.LabelFrame(root, text="Performance Chart", padding="10 10 10 10")
        self.frame_chart.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=5, pady=5)

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(2, weight=1)

        # -- Input fields --
        self._build_input_fields()

        # -- Buttons --
        btn_calc = ttk.Button(self.frame_buttons, text="🧮 Calculate Design", command=self.on_calculate)
        btn_opt = ttk.Button(self.frame_buttons, text="⚡ Auto-Optimize", command=self.on_optimize)
        btn_calc.pack(side="left", padx=5)
        btn_opt.pack(side="left", padx=5)

        # -- Results text area --
        self.text_results = ScrolledText(self.frame_results, height=20, wrap="word")
        self.text_results.pack(fill="both", expand=True)

        # -- Matplotlib Figure --
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_chart)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # -- Explanation text below chart --
        self.text_chart_explanation = tk.Text(self.frame_chart, height=6, wrap="word", background="#f0f0f0")
        self.text_chart_explanation.pack(fill="x", pady=(10, 0))

        # Initialize with default calculation
        self.on_calculate()

    def _build_input_fields(self):
        """
        Build the four sections of inputs:
          1) Mission Requirements
          2) Pontoon Geometry
          3) Materials
          4) Frame Structure
        """
        # Use a grid of 2×2 inside frame_inputs
        for i in range(2):
            self.frame_inputs.columnconfigure(i, weight=1)

        # 1) Mission Requirements
        lf_mission = ttk.LabelFrame(self.frame_inputs, text="Mission Requirements", padding="10 10 10 10")
        lf_mission.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        sf1 = lf_mission

        ttk.Label(sf1, text="Payload Weight (lbs):").grid(row=0, column=0, sticky="w")
        self.var_payload = tk.DoubleVar(value=100.0)
        ttk.Entry(sf1, textvariable=self.var_payload, width=10).grid(row=0, column=1, pady=2)

        ttk.Label(sf1, text="Safety Factor:").grid(row=1, column=0, sticky="w")
        self.var_safety = tk.DoubleVar(value=1.8)
        ttk.Entry(sf1, textvariable=self.var_safety, width=10).grid(row=1, column=1, pady=2)

        ttk.Label(sf1, text="Submersion Percentage (%):").grid(row=2, column=0, sticky="w")
        self.var_submersion = tk.DoubleVar(value=60.0)
        ttk.Entry(sf1, textvariable=self.var_submersion, width=10).grid(row=2, column=1, pady=2)

        # 2) Pontoon Geometry
        lf_geometry = ttk.LabelFrame(self.frame_inputs, text="Pontoon Geometry", padding="10 10 10 10")
        lf_geometry.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        sf2 = lf_geometry

        ttk.Label(sf2, text="Pontoon Diameter (inches):").grid(row=0, column=0, sticky="w")
        self.var_diameter = tk.DoubleVar(value=12.0)
        ttk.Entry(sf2, textvariable=self.var_diameter, width=10).grid(row=0, column=1, pady=2)

        ttk.Label(sf2, text="Total Length (ft):").grid(row=1, column=0, sticky="w")
        self.var_length = tk.DoubleVar(value=6.0)
        ttk.Entry(sf2, textvariable=self.var_length, width=10).grid(row=1, column=1, pady=2)

        ttk.Label(sf2, text="Cone Length (% of total):").grid(row=2, column=0, sticky="w")
        self.var_cone_pct = tk.DoubleVar(value=25.0)
        ttk.Entry(sf2, textvariable=self.var_cone_pct, width=10).grid(row=2, column=1, pady=2)

        # 3) Materials
        lf_materials = ttk.LabelFrame(self.frame_inputs, text="Materials", padding="10 10 10 10")
        lf_materials.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        sf3 = lf_materials

        ttk.Label(sf3, text="Foam Density (lb/ft³):").grid(row=0, column=0, sticky="w")
        self.var_foam_density = tk.DoubleVar(value=1.0)
        ttk.Entry(sf3, textvariable=self.var_foam_density, width=10).grid(row=0, column=1, pady=2)

        ttk.Label(sf3, text="Coating Weight (lb/ft²):").grid(row=1, column=0, sticky="w")
        self.var_coating_weight = tk.DoubleVar(value=0.03)
        ttk.Entry(sf3, textvariable=self.var_coating_weight, width=10).grid(row=1, column=1, pady=2)

        ttk.Label(sf3, text="Water Density (lb/ft³):").grid(row=2, column=0, sticky="w")
        self.var_water_density = tk.DoubleVar(value=64.0)
        ttk.Entry(sf3, textvariable=self.var_water_density, width=10).grid(row=2, column=1, pady=2)

        # 4) Frame Structure
        lf_frame = ttk.LabelFrame(self.frame_inputs, text="Frame Structure", padding="10 10 10 10")
        lf_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        sf4 = lf_frame

        ttk.Label(sf4, text="Cross Beam Length (ft):").grid(row=0, column=0, sticky="w")
        self.var_cross_beam_length = tk.DoubleVar(value=4.0)
        ttk.Entry(sf4, textvariable=self.var_cross_beam_length, width=10).grid(row=0, column=1, pady=2)

        ttk.Label(sf4, text="Number of Cross Beams:").grid(row=1, column=0, sticky="w")
        self.var_num_cross_beams = tk.IntVar(value=4)
        ttk.Entry(sf4, textvariable=self.var_num_cross_beams, width=10).grid(row=1, column=1, pady=2)

        ttk.Label(sf4, text="Aluminum Tube Weight (lb/ft):").grid(row=2, column=0, sticky="w")
        self.var_tube_weight = tk.DoubleVar(value=0.78)
        ttk.Entry(sf4, textvariable=self.var_tube_weight, width=10).grid(row=2, column=1, pady=2)

    def _gather_inputs(self):
        """
        Collect all input values into a dict.
        """
        return {
            'payload': float(self.var_payload.get()),
            'safety_factor': float(self.var_safety.get()),
            'submersion_pct': float(self.var_submersion.get()),
            'diameter_in': float(self.var_diameter.get()),
            'length_ft': float(self.var_length.get()),
            'cone_pct': float(self.var_cone_pct.get()),
            'foam_density': float(self.var_foam_density.get()),
            'coating_weight': float(self.var_coating_weight.get()),
            'water_density': float(self.var_water_density.get()),
            'cross_beam_length': float(self.var_cross_beam_length.get()),
            'num_cross_beams': int(self.var_num_cross_beams.get()),
            'tube_weight': float(self.var_tube_weight.get()),
        }

    def on_calculate(self):
        """
        Called when “Calculate Design” is clicked.
        """
        params = self._gather_inputs()
        results = calculate_design(params)

        # Build a formatted results string
        rs = []
        rs.append(f"→ Status: {results['status']}")
        rs.append("\n🔹 Performance Analysis:")
        rs.append(f"   • Total Boat Weight: {results['total_boat_weight']:.1f} lb")
        rs.append(f"   • Total Buoyant Force: {results['total_buoyant_force']:.1f} lb")
        rs.append(f"   • Actual Safety Factor: {results['actual_safety_factor']:.2f}×")
        rs.append(f"   • Reserve Buoyancy: {results['reserve_buoyancy']:.1f} lb")
        rs.append(f"   • Draft (loaded): {results['draft_in']:.1f} in")

        rs.append("\n🔹 Pontoon Specifications:")
        rs.append(f"   • Each Pontoon Volume: {results['volume_per_pontoon']:.2f} ft³")
        rs.append(f"   • Cylinder Section: {results['cylinder_length']:.1f} ft × {params['diameter_in']/12.0:.1f} ft dia")
        rs.append(f"   • Cone Section: {results['cone_length']:.1f} ft × {params['diameter_in']/12.0:.1f} ft dia")

        rs.append("\n🔹 Weight Breakdown:")
        rs.append(f"   • Payload: {params['payload']:.1f} lb")
        rs.append(f"   • Pontoons (both): {results['pontoon_weight']:.1f} lb")
        rs.append(f"   • Frame: {results['frame_weight']:.1f} lb")
        rs.append(f"   • Total: {results['total_boat_weight']:.1f} lb")

        rs.append("\n🔹 Material Requirements:")
        rs.append(f"   • EPS Foam: {results['total_volume_both']:.1f} ft³")
        rs.append(f"   • Coating Area: {results['total_surface_area_both']:.1f} ft²")
        rs.append(f"   • Aluminum Tubing: {results['total_tube_length']:.1f} ft")

        # Insert into the results Text widget
        self.text_results.delete("1.0", tk.END)
        self.text_results.insert(tk.END, "\n".join(rs))
        self.text_results.insert(tk.END, "\n\n--- Detailed Calculations & Explanations ---\n\n")
        self.text_results.insert(tk.END, results['explanation'])

        # Update chart
        self._update_chart(results)

    def on_optimize(self):
        """
        Called when “Auto-Optimize” is clicked.
        Updates diameter & length fields, then recalculates.
        """
        params = self._gather_inputs()
        new_dia, new_len = optimize_design(params)
        # Update fields
        self.var_diameter.set(new_dia)
        self.var_length.set(new_len)
        # Recalculate
        self.on_calculate()

    def _update_chart(self, results):
        """
        Draw a bar chart with: Weight, Buoyancy, Safety Factor(%)
        Then add an explanatory text below the chart.
        """
        self.ax.clear()

        labels = ['Weight', 'Buoyancy', 'Safety Factor (×100)']
        data = [
            results['total_boat_weight'],
            results['total_buoyant_force'],
            results['actual_safety_factor'] * 100.0
        ]
        colors = ['#FF6384', '#36A2EB', '#4BC0C0']

        bars = self.ax.bar(labels, data, color=colors, edgecolor='black', linewidth=1)

        # Title
        dia_in = float(self.var_diameter.get())
        length_ft = float(self.var_length.get())
        self.ax.set_title(f"Pontoon Design: {dia_in:.0f}\" × {length_ft:.1f} ft", fontsize=14)

        # Y-axis label
        self.ax.set_ylabel("lb / Safety Factor ×100", fontsize=10)
        self.ax.set_ylim(0, max(data) * 1.2)

        # Annotate bars with values
        for bar, val in zip(bars, data):
            height = bar.get_height()
            self.ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + max(data)*0.02,
                f"{val:.1f}",
                ha='center',
                va='bottom',
                fontsize=9
            )

        self.canvas.draw()

        # Explanatory text below the chart
        explanation = (
            "Chart Explanation:\n"
            f" • 'Weight' bar = Total boat weight including payload, pontoons, and frame → {results['total_boat_weight']:.1f} lb.\n"
            f" • 'Buoyancy' bar = Total buoyant force from submerged pontoon volume → {results['total_buoyant_force']:.1f} lb.\n"
            f" • 'Safety Factor (×100)' bar = Actual safety factor ×100 for scale → {results['actual_safety_factor']*100:.1f}.\n\n"
            "A viable design requires the 'Buoyancy' bar to exceed the 'Weight' bar.  "
            "If Buoyancy < Weight, increase pontoon diameter or reduce payload to avoid sinking."
        )
        self.text_chart_explanation.delete("1.0", tk.END)
        self.text_chart_explanation.insert(tk.END, explanation)


if __name__ == "__main__":
    root = tk.Tk()
    app = PontoonCalculatorApp(root)
    root.mainloop()
