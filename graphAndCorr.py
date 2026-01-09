import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr, kendalltau

# ==============================
# Settings
# ==============================
CSV_FILES = {
    "trial1": "trimed_data1.csv",
    "trial2": "trimed_data2.csv",
    "trial3": "trimed_data3.csv",
}

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

    fig, ax_u = plt.subplots(figsize=(8, 4))
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
    ax_u.set_ylabel("Finger command (finger_norm)")
    ax_i.set_ylabel("Servo current [mA]")
    ax_u.set_title(f"Finger Command & Servo Current ({label})")
    ax_u.grid(True)

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

pearson_r, pearson_p = pearsonr(u_contact, i_contact)
spearman_r, spearman_p = spearmanr(u_contact, i_contact)
kendall_r, kendall_p = kendalltau(u_contact, i_contact)

print("=== Contact-region correlations (merged trials) ===")
print(f"Pearson  r = {pearson_r:.3f} (p = {pearson_p:.3e})")
print(f"Spearman r = {spearman_r:.3f} (p = {spearman_p:.3e})")
print(f"Kendall  τ = {kendall_r:.3f} (p = {kendall_p:.3e})")

# ==============================
# Scatter plot (contact region)
# ==============================
plt.figure(figsize=(5, 5))
plt.scatter(u_contact, i_contact, s=12, alpha=0.7)
plt.xlabel("Finger command (finger_norm)")
plt.ylabel("Servo current [mA]")
plt.title("Finger Command vs Servo Current (contact region)")
plt.grid(True)
plt.tight_layout()
plt.show()
