import pandas as pd
import matplotlib.pyplot as plt

def plot_u_f(csv_path: str) -> None:
    """
    CSVファイルから u_normalized を横軸、
    f_normalized を縦軸としてプロットする。
    """

    # CSV読み込み
    df = pd.read_csv(csv_path)

    # 必要なカラムの存在確認（防御的実装）
    required_columns = {"u_normalized", "f_normalized"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"CSVに必要なカラムが存在しません: {required_columns}")

    # プロット
    plt.figure()
    plt.plot(df["u_normalized"], df["f_normalized"], marker="o")
    plt.xlabel("u_normalized")
    plt.ylabel("f_normalized")
    plt.title("u_normalized vs f_normalized")
    plt.grid(True)

    plt.show()


if __name__ == "__main__":
    plot_u_f("unity_force_probe_20260105_152827.csv")
