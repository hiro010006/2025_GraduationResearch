import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.stats import pearsonr, spearmanr, kendalltau

# ==============================
# Settings
# ==============================
CSV_FILES = {
    "Measurement1": "trimed_data1.csv",
    "Measurement2": "trimed_data2.csv",
    "Measurement3": "trimed_data3.csv",
}
IDEAL_DATA_PATH = "unity_force_probe_20260105_152827.csv"

CONTACT_THRESHOLD = 0.21

all_u = []
all_i = []

# ==============================
# Time-series plots (separate)
# ==============================
for label, path in CSV_FILES.items():
    df = pd.read_csv(path)
    df = df[df["direction"] == "Pico->Unity"].copy()

    # time normalization
    t0 = df["timestamp"].iloc[0]
    df["time_sec"] = df["timestamp"] - t0

    t = df["time_sec"].astype(float)
    u = df["finger_norm"].astype(float)
    i = df["current"].astype(float)

    fig, ax_u = plt.subplots(figsize=(8, 5))
    ax_i = ax_u.twinx()

    ax_u.plot(t, u, "--", linewidth=2, label="finger_norm")
    ax_i.plot(t, i, linewidth=2, label="current")

    # contact detection
    contact_idx = df[df["finger_norm"] >= CONTACT_THRESHOLD].index
    if len(contact_idx) > 0:
        contact_time = df.loc[contact_idx[0], "time_sec"]
        ax_u.axhline(
            CONTACT_THRESHOLD,
            linestyle=":",
            linewidth=2,
            color="black",
            label="contact threshold (finger_norm = 0.21)"
        )


    ax_u.set_xlabel("Time [s]")
    ax_u.set_ylabel("finger_norm (u)")
    ax_i.set_ylabel("Servo current [mA]")
    ax_u.set_title(f"finger_norm & Servo Current ({label})")
    ax_u.grid(True)

    # --- margin ---
    u_max = u.max()
    ax_u.set_ylim(0, u_max / 0.8)

    i_max = i.max()
    ax_i.set_ylim(0, i_max / 0.8)

    lines_u, labels_u = ax_u.get_legend_handles_labels()
    lines_i, labels_i = ax_i.get_legend_handles_labels()
    ax_u.legend(lines_u + lines_i, labels_u + labels_i, loc="upper right")

    plt.tight_layout()
    plt.show()

    # store contact-region data
    mask = u >= CONTACT_THRESHOLD
    all_u.append(u[mask])
    all_i.append(i[mask])

# ==============================
# Correlation analysis (merged)
# ==============================
u_contact = pd.concat(all_u, ignore_index=True)
i_contact = pd.concat(all_i, ignore_index=True)

# iの正規化 (最小値を0, 最大値を1に変換)
if len(i_contact) > 0:
    i_min = i_contact.min()
    i_max = i_contact.max()
    i_contact_norm = (i_contact - i_min) / (i_max - i_min)
else:
    i_contact_norm = i_contact

if os.path.exists(IDEAL_DATA_PATH):
    df_ideal = pd.read_csv(IDEAL_DATA_PATH)
else:
    print(f"Error: {IDEAL_DATA_PATH} not found.")
    df_ideal = pd.DataFrame()

pearson_r, pearson_p = pearsonr(u_contact, i_contact_norm)
spearman_r, spearman_p = spearmanr(u_contact, i_contact_norm)
kendall_r, kendall_p = kendalltau(u_contact, i_contact_norm)

print("=== Contact-region correlations (merged Measurements) ===")
print(f"Pearson  r = {pearson_r:.3f} (p = {pearson_p:.3e})")
print(f"Spearman r = {spearman_r:.3f} (p = {spearman_p:.3e})")
print(f"Kendall  τ = {kendall_r:.3f} (p = {kendall_p:.3e})")

# ==============================
# Scatter plot (contact region)
# ==============================
fig, ax1 = plt.subplots(figsize=(7, 5))

ax1.scatter(u_contact, i_contact_norm, s=10, alpha=0.3, color="orange", label="Measured Current (Scatter)")

if len(u_contact) > 0:
    poly_coeffs = np.polyfit(u_contact, i_contact_norm, 2)
    poly_func = np.poly1d(poly_coeffs)
    u_fit = np.linspace(u_contact.min(), u_contact.max(), 100)
    ax1.plot(u_fit, poly_func(u_fit), color="red", linewidth=3, label="Measured Fit (Trend)")

if not df_ideal.empty:
    ax1.plot(df_ideal["u_normalized"], df_ideal["f_normalized"], 
             color="blue", linestyle="--", linewidth=2.5, label="Ideal Force (Target)")

ax1.set_xlabel("finger_norm (u)")
ax1.set_ylabel("Normalized Scale (0.0 - 1.0)", fontsize=12)
ax1.set_ylim(-0.05, 1.05)

plt.title("Comparison: Normalized Current vs Ideal Force Model", fontsize=14)
ax1.grid(True, linestyle=":", alpha=0.6)

lines1, labels1 = ax1.get_legend_handles_labels()
ax1.legend(lines1, labels1, loc="upper left")

plt.tight_layout()
plt.show()