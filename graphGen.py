import pandas as pd
import matplotlib.pyplot as plt

CSV_PATH = "udp_log_20251227_173344.csv"
CONTACT_THRESHOLD = 0.2

df = pd.read_csv(CSV_PATH)

df = df[
    (df["direction"] == "Pico->Unity") &
    (df["finger_norm"] >= CONTACT_THRESHOLD)
].copy()

# 相関係数
pearson = df["finger_norm"].corr(df["current"], method="pearson")
spearman = df["finger_norm"].corr(df["current"], method="spearman")

print(f"Contact-region Pearson  : {pearson:.3f}")
print(f"Contact-region Spearman : {spearman:.3f}")

# 散布図
plt.scatter(df["finger_norm"], df["current"], s=10)
plt.xlabel("Finger Norm [-]")
plt.ylabel("Servo Current [mA]")
plt.title("Correlation in Contact Region")
plt.grid(True)
plt.show()
