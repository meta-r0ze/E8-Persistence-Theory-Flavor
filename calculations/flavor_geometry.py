#!python3

import math
import cmath
import argparse
from dataclasses import dataclass

# ==========================================
# 0. EXTERNAL REFERENCE VALUES (Source of Truth)
# ==========================================
@dataclass
class MeasuredVal:
    value: float
    uncertainty: float
    units: str
    citation: str

REFS = {
    # PDG 2024 Global Fit (CKM) - DOI: 10.1103/PhysRevD.110.030001
    "vus": MeasuredVal(0.22500, 0.00067, "", "navas_review_2024"),
    "vub": MeasuredVal(0.00382, 0.00020, "", "navas_review_2024"),
    "vcb": MeasuredVal(0.0410, 0.0014, "", "navas_review_2024"),
    "vud": MeasuredVal(0.97373, 0.00031, "", "navas_review_2024"),
    "vcd": MeasuredVal(0.22480, 0.00067, "", "navas_review_2024"),
    "vcs": MeasuredVal(0.97310, 0.00020, "", "navas_review_2024"),
    "vts": MeasuredVal(0.0400, 0.0027, "", "navas_review_2024"),
    "vtb": MeasuredVal(0.999100, 0.000034, "", "navas_review_2024"),
    "vtd": MeasuredVal(0.00870, 0.00020, "", "navas_review_2024"),

    # CP Violation
    "jarlskog": MeasuredVal(3.06e-5, 0.20e-5, "", "navas_review_2024"),
    "delta_cp": MeasuredVal(68.0, 5.0, "\\degree", "navas_review_2024"),
    
    # Wolfenstein (PDG 2024)
    "lambda": MeasuredVal(0.22500, 0.00067, "", "navas_review_2024"),
    "A": MeasuredVal(0.826, 0.012, "", "navas_review_2024"),
    "rho_bar": MeasuredVal(0.159, 0.010, "", "navas_review_2024"),
    "eta_bar": MeasuredVal(0.348, 0.009, "", "navas_review_2024"),
    
    # Quark Masses (PDG 2024, running at 2 GeV MS-bar)
    "mass_ratio_ds": MeasuredVal(0.0503, 0.0026, "", "navas_review_2024"),
    
    # NuFIT 6.0 (October 2024) - arXiv:2410.05380
    "theta_12_sin2": MeasuredVal(0.304, 0.012, "", "esteban_nufit-60_2024"),      # ±1σ range: 0.292-0.316
    "theta_23_sin2": MeasuredVal(0.574, 0.016, "", "esteban_nufit-60_2024"),      # ±1σ range: 0.558-0.590 (best fit)
    "theta_23_sin2_sym": MeasuredVal(0.5, 0.0, "", "esteban_nufit-60_2024"),       # Maximal mixing hypothesis
    "theta_13_sin2": MeasuredVal(0.02225, 0.00056, "", "esteban_nufit-60_2024"),  # ±1σ range: 0.02169-0.02281
    "delta_cp_neutrino": MeasuredVal(197.0, 27.0, "\\degree", "esteban_nufit-60_2024"),  # ±1σ range: 170°-224°

    # Paper I Input (Weak Mixing Angle at Z-pole, PDG 2024)
    "sin2_w": MeasuredVal(0.23121, 0.00004, "", "navas_review_2024"),  # (on-shell scheme)
    
    # https://hflav.web.cern.ch (March 2024 update)
    "gamma": MeasuredVal(66.2, 2.1, "\\degree", "navas_review_2024"),
    "sin2beta": MeasuredVal(0.699, 0.017, "", "navas_review_2024"),
}

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================

def format_float_latex(num, precision=9):
    return f"{num:.{precision}f}".rstrip('0').rstrip('.')

def to_latex_sci(num, precision=4):
    if num == 0: return "0"
    exponent = int(math.floor(math.log10(abs(num))))
    mantissa = num / (10**exponent)
    if -3 <= exponent < 6:
        if abs(num - round(num)) < 1e-9:
            return f"{int(num)}"
        return f"{num:.{precision}f}".rstrip('0').rstrip('.')
    return f"{mantissa:.{precision}f} \\times 10^{{{exponent}}}"

def to_latex_sci_with_err(val, err, precision=4):
    if val == 0: return f"0 \\pm {err}"
    exponent = int(math.floor(math.log10(abs(val))))
    mantissa_val = val / (10**exponent)
    mantissa_err = err / (10**exponent)
    return f"({mantissa_val:.{precision}f} \\pm {mantissa_err:.{precision}f}) \\times 10^{{{exponent}}}"

def print_latex_tag(tag, content):
    print(f"%<*{tag}>{content}%</{tag}>")

def mag(z):
    """Safe magnitude for complex or float"""
    return abs(z)

def print_derivation(name, tag, latex_eq, calc_val, ref_key, unit="", latex_mode=False):
    # If unit is empty but ref has one, use ref's unit
    if ref_key and ref_key in REFS and unit == "":
        unit = REFS[ref_key].units

    if latex_mode:
        # Value
        val_str = format_float_latex(calc_val) if 0.001 < abs(calc_val) < 1000 else to_latex_sci(calc_val, 5)
        if unit: val_str += f" \\unit{{{unit}}}"
        print_latex_tag(tag + "Val", val_str)

        # Equation
        if latex_eq:
            print_latex_tag(tag + "Eq", latex_eq)

        # Experimental comparison
        if ref_key and ref_key in REFS:
            ref = REFS[ref_key]
            cite_str = f"~\\cite{{{ref.citation}}}" if ref.citation else ""
            if 0.001 < abs(ref.value) < 1000:
                exp_str = f"\\qty{{{format_float_latex(ref.value)} \\pm {format_float_latex(ref.uncertainty)}}}{{{unit}}}{cite_str}"
            else:
                exp_str = f"${to_latex_sci_with_err(ref.value, ref.uncertainty, 5)}$ {cite_str}"
            
            print_latex_tag(tag + "ExperimentalValue", exp_str)

            diff = calc_val - ref.value
            sigma = abs(diff / ref.uncertainty) if ref.uncertainty > 0 else 0.0
            
            print_latex_tag(tag + "Diff", f"{diff:.2e}")
            print_latex_tag(tag + "Sigma", f"{sigma:.2f}")

            if sigma < 1.0:
                acc_text = f"matches the experimental consensus {exp_str} to within ${sigma:.2f}\\sigma$."
            elif sigma < 3.0:
                acc_text = f"lies within ${sigma:.2f}\\sigma$ of the observed value {exp_str}."
            else:
                acc_text = f"deviates by ${sigma:.2f}\\sigma$ from the observed value {exp_str}."
            print_latex_tag(tag + "AccText", acc_text)
        return

    # Console Mode
    print(f"--- {name} ---")
    if latex_eq: print(f"Formula:    {latex_eq}")
    print(f"Calculated: {calc_val:.12f} {unit}")
    if ref_key and ref_key in REFS:
        ref = REFS[ref_key]
        sigma = (calc_val - ref.value) / ref.uncertainty if ref.uncertainty > 0 else 0
        print(f"Target:     {ref.value:.6f} +/- {ref.uncertainty:.6f}")
        print(f"Deviation:  {sigma:+.2f}σ")
    print("")

def check_unitarity(matrix, latex_mode=False):
    if latex_mode: return
    print("\n--- Unitarity Kill-Switch Audit ---")
    rows = [sum(abs(x)**2 for x in row) for row in matrix]
    cols = [sum(abs(matrix[i][j])**2 for i in range(3)) for j in range(3)]
    for i, r in enumerate(rows):
        print(f"Row {i+1}: {r:.15f} [{'PASS' if abs(r-1)<1e-12 else 'FAIL'}]")
    for j, c in enumerate(cols):
        print(f"Col {j+1}: {c:.15f} [{'PASS' if abs(c-1)<1e-12 else 'FAIL'}]")
    print("-" * 40)

def validate_jarlskog_invariance(V, latex_mode=False):
    J1 = abs((V[0][0] * V[1][1] * V[0][1].conjugate() * V[1][0].conjugate()).imag)
    J2 = abs((V[1][1] * V[2][2] * V[1][2].conjugate() * V[2][1].conjugate()).imag)
    J3 = abs((V[0][1] * V[1][2] * V[0][2].conjugate() * V[1][1].conjugate()).imag)


    if not latex_mode:
        print(f"\n--- Jarlskog Formula Check ---")
        print(f"Form 1 (Vud Vub* Vcd* Vcb): {J1:.6e}")
        print(f"Form 2 (Vus Vcb Vub* Vcd*): {J2:.6e}")
        print(f"Form 3 (Vud Vus* Vcb Vtd*): {J3:.6e}")
        # floating point fun
        match = math.isclose(J1, J2, rel_tol=1e-9) and math.isclose(J2, J3, rel_tol=1e-9)
        status = "PASS" if match else "FAIL"      
        print(f"Unitarity Consistency: {status}")
    return J1

def run_global_audit(vals_dict, refs, latex_mode=False):
    chi2 = 0
    dof = 0
    
    if not latex_mode:
        print("\nGlobal Fit Summary:")
        
    for key, val in vals_dict.items():
        if key not in refs: continue
        ref = REFS[key]
        dev = ((val - ref.value)/ref.uncertainty)**2
        chi2 += dev
        dof += 1
        if not latex_mode:
            print(f"{key.upper():<10}: {val:.6f} (Chi2: {dev:.4f})")
            
    if latex_mode:
        print_latex_tag("flavorTotalChiVal", f"{chi2:.4f}")
        print_latex_tag("flavorReducedChiVal", f"{chi2/dof:.4f}")
    else:
        print(f"TOTAL CHI2: {chi2:.4f} (DOF={dof})")
        print(f"REDUCED:    {chi2/dof:.4f}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--latex', action='store_true')
    args = parser.parse_args()

    # --- INVARIANTS ---
    D     = 4
    DELTA = 43
    SIGMA = 5
    NU    = 16
    CHI   = 2
    
    # Derived Loads
    L_INTRINSIC = NU + SIGMA + CHI
    L_EMBED = L_INTRINSIC + (2 * D)
    L_SUBSTRATE = (DELTA * D) + NU
    N = 2 * NU

    PI = math.pi

    # ALPHA_INV
    comp_CAP = PI * DELTA
    comp_MAP = CHI
    comp_PRO = -1 / ((D * DELTA) - SIGMA)
    comp_GOV = -(CHI / DELTA)
    comp_TOL = (1 / pow(N, 3)) * (CHI / SIGMA) * (1 - (SIGMA / (D * DELTA)))
    comp_MAR = 1 / (L_EMBED * (SIGMA + 1) * pow(DELTA, 2))
    # Summation
    ALPHA_INV_GEO = comp_CAP + comp_MAP + comp_PRO + comp_GOV + comp_TOL + comp_MAR
    ALPHA_GEO = 1.0 / ALPHA_INV_GEO
    ALPHA_INV = ALPHA_INV_GEO

    PHI = (1 + math.sqrt(5)) / 2

    if not args.latex:
        print("\n" + "="*60)
        print("  SYSTEM IV-C: CKM MATRIX (EXACT GEOMETRIC)")
        print("="*60 + "\n")

    # Geometric Transition Angles (The underlying physics)
    s12_geo = PI / (NU - CHI) 
    vcb_geo = (PI + CHI) / (ALPHA_INV - (D * PI))
    s13_geo = 1.0 / (CHI * ALPHA_INV + PI)
    delta_rad = math.atan(SIGMA / CHI)
    delta_deg = delta_rad * 180 / PI

    # --- 2. MATRIX CONSTRUCTION ---
    s12, c12 = s12_geo, math.sqrt(1 - s12_geo**2)
    s13, c13 = s13_geo, math.sqrt(1 - s13_geo**2)
    s23 = vcb_geo / c13  # Inversion: s23 = |Vcb| / c13
    c23 = math.sqrt(1 - s23**2)
    phase = cmath.exp(1j * delta_rad)

    # Elements
    Vud = c12 * c13
    Vus = s12 * c13
    Vub = s13 * phase.conjugate()
    Vcd = (-s12 * c23) - (c12 * s23 * s13 * phase)
    Vcs = (c12 * c23) - (s12 * s23 * s13 * phase)
    Vcb = s23 * c13
    Vtd = (s12 * s23) - (c12 * c23 * s13 * phase)
    Vts = (-c12 * s23) - (s12 * c23 * s13 * phase)
    Vtb = c23 * c13

    CKM = [[Vud, Vus, Vub], [Vcd, Vcs, Vcb], [Vtd, Vts, Vtb]]

    # --- 3. OUTPUTS: MATRIX ---
   
    # Primary Inputs (Show the Geometry)
    print_derivation("s_12 (Primary Mixing)", "s12", r"\frac{\pi}{\nu - \chi}", s12_geo, "vus", "", args.latex)
    print_derivation("CabibboSineVal", "CabibboSine", r"\frac{\pi}{\nu - \chi}", s12_geo, "vus", "", args.latex)
    print_derivation("|V_cb| (Orthogonal Transition)", "Vcb", r"\frac{\pi + \chi}{\alpha^{-1} - D\pi}", vcb_geo, "vcb", "", args.latex)
    print_derivation("s_13 (Boundary Leakage)", "s13", r"\frac{1}{\chi\alpha^{-1} + \pi}", s13_geo, "vub", "", args.latex)
    print_derivation("CP Phase", "CPPhase", r"\arctan\left(\frac{\sigma}{\chi}\right)", delta_deg, "delta_cp", "^\\circ", args.latex)

    # Derived Diagonal Elements (Unitary Persistence)
    # Using 'c' notation implies 1 - s^2
    print_derivation("Derived: Vud", "Vud", r"c_{12}c_{13}", mag(Vud), "vud", "", args.latex)
    print_derivation("Derived: Vus", "Vus", r"s_{12}c_{13}", mag(Vus), "vus", "", args.latex)
    print_derivation("Derived: Vub", "Vub", r"s_{13}phase.conjugate()", mag(Vub), "vub", "", args.latex)
    print_derivation("Derived: Vcs", "Vcs", r"c_{12}c_{23} - s_{12}s_{23}s_{13}e^{i\delta}", mag(Vcs), "vcs", "", args.latex)
    print_derivation("Derived: Vtb", "Vtb", r"c_{23}c_{13}", mag(Vtb), "vtb", "", args.latex)

    # Derived Off-Diagonal Elements (Interference)
    # Standard Parametrization matches the vector logic perfectly
    print_derivation("Derived: Vcd", "Vcd", r"|-s_{12}c_{23} - c_{12}s_{23}s_{13}e^{i\delta}|", mag(Vcd), "vcd", "", args.latex)
    print_derivation("Derived: Vtd", "Vtd", r"|s_{12}s_{23} - c_{12}c_{23}s_{13}e^{i\delta}|", mag(Vtd), "vtd", "", args.latex)
    print_derivation("Derived: Vts", "Vts", r"|-c_{12}s_{23} - s_{12}c_{23}s_{13}e^{i\delta}|", mag(Vts), "vts", "", args.latex)

    J_exact = validate_jarlskog_invariance(CKM, args.latex)
    print_derivation("Jarlskog Inv", "JarlskogMatrix", r"\Im(V_{ud} V_{cs} V_{us}^* V_{cd}^*)", J_exact, "jarlskog", "", args.latex)

    # --- J-CONSISTENCY ---
    N_BITS = 2 * NU
    MANIFOLD_FRICTION = 1.0 - (1.0 / (D * DELTA))
    T_GEO = (1.0 / pow(N_BITS, 3)) * (CHI / SIGMA) * (1.0 - (SIGMA / (D * DELTA)))
    PHI_SQ = pow(PHI, 2)
    J_GEO = PHI_SQ * MANIFOLD_FRICTION * T_GEO
    if args.latex: print_latex_tag("JarlskogGeoVal", f"{J_GEO:.9f}") 

    J_diff_pct = (abs(J_exact - J_GEO) / J_GEO) * 100
    if args.latex:
        print_latex_tag("JConsistencyPct", f"{J_diff_pct:.2f}")
    else:
        print(f"--- J-Consistency ---")
        print(f"Matrix: {J_exact:.6e} | Geom: {J_GEO:.6e} | Diff: {J_diff_pct:.2f}%")
        print("")

    check_unitarity(CKM, args.latex)

    # --- 4. OUTPUTS: WOLFENSTEIN & MASS ---
    if not args.latex: 
        print("\n--- Geometric Wolfenstein Parameters ---")
        print("NOTE: Wolfenstein params are O(lambda^3) approximations.")
        print("Deviations >1sigma are expected artifacts of the expansion.")
    lambda_geo = mag(Vus)
    A_geo = mag(Vcb) / (lambda_geo**2)
    complex_rho_eta = Vub.conjugate() / (A_geo * lambda_geo**3)
    
    print_derivation("Lambda", "WolfLambda", r"|V_{us}|", lambda_geo, "lambda", "", args.latex)
    print_derivation("A", "WolfA", r"|V_{cb}| / \lambda^2", A_geo, "A", "", args.latex)
    print_derivation("Rho_bar", "WolfRho", r"\Re(V_{ub} / A\lambda^3)", complex_rho_eta.real, "rho_bar", "", args.latex)
    print_derivation("Eta_bar", "WolfEta", r"\Im(V_{ub} / A\lambda^3)", complex_rho_eta.imag, "eta_bar", "", args.latex)
    print_derivation("Mass Ratio (d/s)", "MassRatio", r"\sin^2(\theta_c)", mag(Vus)**2, "mass_ratio_ds", "", args.latex)

    # --- 5. OUTPUTS: UNITARITY TRIANGLE ---
    if not args.latex: print("\n--- Unitarity Triangle ---")
    num_gamma = -(Vud * Vub.conjugate())
    den_gamma = (Vcd * Vcb.conjugate())
    gamma_deg = math.degrees(cmath.phase(num_gamma / den_gamma))
    
    num_beta = -(Vcd * Vcb.conjugate())
    den_beta = (Vtd * Vtb.conjugate())
    beta_deg = math.degrees(cmath.phase(num_beta / den_beta))
    
    alpha_deg = 180.0 - beta_deg - gamma_deg
    sin_2beta = math.sin(2 * math.radians(beta_deg))

    print_derivation("Angle Gamma", "AngleGamma", r"\arg(-V_{ud}V_{ub}^*/V_{cd}V_{cb}^*)", gamma_deg, "gamma", "\\degree", args.latex)
    print_derivation("Angle Beta", "AngleBeta", r"\arg(-V_{cd}V_{cb}^*/V_{td}V_{tb}^*)", beta_deg, None, "\\degree", args.latex)
    print_derivation("Angle Alpha", "AngleAlpha", r"180^\circ - \beta - \gamma", alpha_deg, None, "\\degree", args.latex)
    print_derivation("Sin(2Beta)", "SinTwoBeta", r"\sin(2\beta)", sin_2beta, "sin2beta", "", args.latex)

    # --- 6. OUTPUTS: NEUTRINOS ---
    if not args.latex: print("\n--- PMNS (Neutrinos) ---")
    sin2_12 = 1.0 / (2.0 * PHI)
    
    # Atmospheric Bare Symmetry
    sin2_23_bare = 1.0 / CHI 
    # Volumetric Bulk Shift (Mixing Gen 2 -> Gen 3)
    bulk_shift = 1.0 + (PI / (NU + SIGMA))
    sin2_23_dressed = sin2_23_bare * bulk_shift

    sin2_13 = (SIGMA - CHI) / ALPHA_INV
    delta_nu = 360.0 / PHI

    print_derivation("Solar (12)", "SolarAngle", r"\frac{1}{2\phi}", sin2_12, "theta_12_sin2", "", args.latex)
    
    # Use the dressed value and compare to the actual experimental target
    print_derivation("Atmos (23)", "AtmosAngle", r"\frac{1}{\chi}\left(1 + \frac{\pi}{\nu+\sigma}\right)", sin2_23_dressed, "theta_23_sin2", "", args.latex)
    
    print_derivation("Reactor (13)", "ReactorAngle", r"\frac{\sigma - \chi}{\alpha^{-1}}", sin2_13, "theta_13_sin2", "", args.latex)
    print_derivation("Nu CP Phase", "NuCP", r"\frac{360^{\circ}}{\phi}", delta_nu, "delta_cp_neutrino", "\\degree", args.latex)

    # --- PMNS MATRIX SYNTHESIS ---
    if not args.latex: print("\n--- PMNS Matrix Synthesis ---")
    s12_nu = math.sqrt(sin2_12)
    c12_nu = math.sqrt(1 - sin2_12)
    s23_nu = math.sqrt(sin2_23_dressed)
    c23_nu = math.sqrt(1 - sin2_23_dressed)
    s13_nu = math.sqrt(sin2_13)
    c13_nu = math.sqrt(1 - sin2_13)
    phase_nu = cmath.exp(1j * math.radians(delta_nu))

    Ue1 = c12_nu * c13_nu
    Ue2 = s12_nu * c13_nu
    Ue3 = s13_nu * phase_nu.conjugate()
    Umu1 = (-s12_nu * c23_nu) - (c12_nu * s23_nu * s13_nu * phase_nu)
    Umu2 = (c12_nu * c23_nu) - (s12_nu * s23_nu * s13_nu * phase_nu)
    Umu3 = s23_nu * c13_nu
    Utau1 = (s12_nu * s23_nu) - (c12_nu * c23_nu * s13_nu * phase_nu)
    Utau2 = (-c12_nu * s23_nu) - (s12_nu * c23_nu * s13_nu * phase_nu)
    Utau3 = c23_nu * c13_nu

    PMNS = [[Ue1, Ue2, Ue3], [Umu1, Umu2, Umu3], [Utau1, Utau2, Utau3]]

    print_derivation("Ue1", "Ue1", "", mag(Ue1), None, "", args.latex)
    print_derivation("Ue2", "Ue2", "", mag(Ue2), None, "", args.latex)
    print_derivation("Ue3", "Ue3", "", mag(Ue3), None, "", args.latex)
    print_derivation("Umu1", "Umu1", "", mag(Umu1), None, "", args.latex)
    print_derivation("Umu2", "Umu2", "", mag(Umu2), None, "", args.latex)
    print_derivation("Umu3", "Umu3", "", mag(Umu3), None, "", args.latex)
    print_derivation("Utau1", "Utau1", "", mag(Utau1), None, "", args.latex)
    print_derivation("Utau2", "Utau2", "", mag(Utau2), None, "", args.latex)
    print_derivation("Utau3", "Utau3", "", mag(Utau3), None, "", args.latex)
    
    check_unitarity(PMNS, args.latex)

    # --- GST CHECK ---
    eta_manifold = 1.0 - (1.0/(D*DELTA))
    denom_weak = (D*DELTA) + (NU*eta_manifold) + SIGMA
    sin2_w = DELTA / denom_weak
    diff_gst = abs(mag(Vus) - sin2_w)
    gst_gap_pct = (diff_gst / sin2_w) * 100
    if args.latex:
        print_derivation("Gauge-Flavor Unity", "UnityGap", r"|\sin\theta_C - \sin^2\theta_W|", diff_gst, "unity_gap", "", args.latex)
        print_latex_tag("GSTGapPct", f"{gst_gap_pct:.3f}")
    else:
        print(f"\n--- GST Check ---")
        print(f"Gap: {diff_gst:.6f} ({gst_gap_pct:.3f}%)")

    # ==========================================
    # APPENDIX E: GEOMETRIC AUDITS
    # ==========================================
    if not args.latex: print("\n" + "="*60 + "\n  APPENDIX E: GEOMETRIC AUDITS\n" + "="*60)

    # 3. Gauge Width Ratio (W/Z)
    gamma_w_exp = 2.085
    gamma_z_exp = 2.4952
    gamma_ratio_exp = gamma_w_exp / gamma_z_exp
    gamma_ratio_err = gamma_ratio_exp * math.sqrt((0.042/2.085)**2 + (0.0023/2.4952)**2)
    
    REFS["gamma_ratio"] = MeasuredVal(gamma_ratio_exp, gamma_ratio_err, "", "navas_review_2024")
    
    gamma_ratio_geo = SIGMA / (SIGMA + 1.0)
    print_derivation("Gauge Width Ratio", "GammaRatio", r"\frac{\sigma}{\sigma + 1}", gamma_ratio_geo, "gamma_ratio", "", args.latex)

    # 4. Unitarity Triangle Area
    area_geo = J_exact / 2.0
    print_derivation("Unitarity Triangle Area", "Area", r"\frac{J}{2}", area_geo, None, "", args.latex)

    # --- 9. GLOBAL AUDIT ---
    audit_dict = {
        # Quark Sector (CKM & Unitarity)
        "vud": mag(Vud), "vus": mag(Vus), "vub": mag(Vub),
        "vcd": mag(Vcd), "vcs": mag(Vcs), "vcb": mag(Vcb),
        "vtd": mag(Vtd), "vts": mag(Vts), "vtb": mag(Vtb),
        "jarlskog": J_exact, "delta_cp": delta_deg,
        "gamma": gamma_deg, "sin2beta": sin_2beta,
        
        # Lepton Sector (PMNS)
        "theta_12_sin2": sin2_12,
        "theta_23_sin2": sin2_23_dressed,
        "theta_13_sin2": sin2_13,
        "delta_cp_neutrino": delta_nu
    }

    run_global_audit(audit_dict, REFS, args.latex)

if __name__ == "__main__":
    main()
