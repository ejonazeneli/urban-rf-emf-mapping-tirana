from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scipy.interpolate import griddata

# ==========================================================
# Spatial RF-EMF field maps from anonymized local coordinates
# ==========================================================
# Input data are anonymized: original latitude/longitude, zone names,
# dates, times and raw file names are not included in the public dataset.
# Local X/Y coordinates are UTM-derived coordinates shifted to an arbitrary
# origin, expressed in meters.

ROOT = Path(__file__).resolve().parents[1]
INPUT_XLSX = ROOT / "data" / "anonymized_rf_emf_dataset_local_xy.xlsx"
INPUT_CSV = ROOT / "data" / "anonymized_rf_emf_dataset_local_xy.csv"
OUT = ROOT / "outputs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

MAPS = {
    "LTE800": "LTE 800",
    "GSM900": "GSM 900",
    "LTE1800": "LTE 1800",
    "UMTS2100": "UMTS 2100",
    "LTE2600": "LTE 2600",
    "NR3600": "5G NR 3600",
    "E_total": "TOTAL RF-EMF EXPOSURE (RSS)",
}

POSITIONS = [
    ("LTE800", 0, 0),
    ("GSM900", 0, 1),
    ("LTE1800", 0, 2),
    ("UMTS2100", 0, 3),
    ("LTE2600", 1, 0),
    ("NR3600", 1, 1),
    ("E_total", 1, 2),
]

GRID_RESOLUTION = 420
DPI = 300
CMAP = "turbo"

BAND_VMIN = 0.50
BAND_VMAX = 2.50
TOTAL_VMIN = 1.20
TOTAL_VMAX = 5.30

mpl.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.titlesize": 8.7,
        "axes.titleweight": "bold",
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    }
)


def add_geographic_north(ax):
    ax.annotate(
        "N",
        xy=(1.035, 0.94),
        xytext=(1.035, 0.83),
        xycoords="axes fraction",
        ha="center",
        va="center",
        fontsize=7.5,
        fontweight="bold",
        color="black",
        arrowprops=dict(
            facecolor="black",
            edgecolor="black",
            width=2.0,
            headwidth=7.8,
            headlength=9.0,
        ),
        annotation_clip=False,
        zorder=8,
    )


def load_anonymized_dataset():
    if INPUT_XLSX.exists():
        df = pd.read_excel(INPUT_XLSX)
    elif INPUT_CSV.exists():
        df = pd.read_csv(INPUT_CSV)
    else:
        raise FileNotFoundError(
            f"Input dataset not found. Expected {INPUT_XLSX} or {INPUT_CSV}"
        )

    required_columns = ["x_local_m", "y_local_m"] + list(MAPS.keys())
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in anonymized dataset: {missing}")
    return df


def make_grid(df):
    x = df["x_local_m"].to_numpy()
    y = df["y_local_m"].to_numpy()
    margin_x = 0.04 * (x.max() - x.min())
    margin_y = 0.04 * (y.max() - y.min())

    xi = np.linspace(x.min() - margin_x, x.max() + margin_x, GRID_RESOLUTION)
    yi = np.linspace(y.min() - margin_y, y.max() + margin_y, GRID_RESOLUTION)
    return np.meshgrid(xi, yi)


def interpolate_linear_field(df, variable, xx, yy):
    x = df["x_local_m"].to_numpy()
    y = df["y_local_m"].to_numpy()
    z = df[variable].to_numpy()

    zi_linear = griddata((x, y), z, (xx, yy), method="linear")
    zi_nearest = griddata((x, y), z, (xx, yy), method="nearest")

    # Linear interpolation is used inside the convex hull; nearest-neighbour
    # values only fill rectangular display edges to keep the figure continuous.
    return np.where(np.isnan(zi_linear), zi_nearest, zi_linear)


def draw_panel(ax, df, variable, title, xx, yy, is_total=False):
    zi = interpolate_linear_field(df, variable, xx, yy)
    vmin, vmax = (TOTAL_VMIN, TOTAL_VMAX) if is_total else (BAND_VMIN, BAND_VMAX)
    levels = np.linspace(vmin, vmax, 36)

    contour = ax.contourf(
        xx,
        yy,
        zi,
        levels=levels,
        cmap=CMAP,
        vmin=vmin,
        vmax=vmax,
        extend="both",
    )
    ax.scatter(
        df["x_local_m"],
        df["y_local_m"],
        s=9,
        facecolors="white",
        edgecolors="black",
        linewidths=0.35,
        alpha=0.85,
        zorder=4,
    )

    ax.set_title(title, pad=4)
    ax.set_xlabel("X (m)", fontsize=7)
    ax.set_ylabel("Y (m)", fontsize=7)
    ax.tick_params(labelsize=6, length=2)
    ax.set_aspect("auto")
    ax.grid(color="white", linewidth=0.22, alpha=0.24)
    add_geographic_north(ax)
    for spine in ax.spines.values():
        spine.set_linewidth(0.7)
        spine.set_edgecolor("#303030")
    return contour


def draw_side_panel(fig, panel_spec, band_contour, total_contour):
    side = fig.add_subplot(panel_spec)
    side.axis("off")

    band_cax = side.inset_axes([0.05, 0.55, 0.26, 0.34])
    band_cbar = fig.colorbar(band_contour, cax=band_cax)
    band_cbar.ax.set_title("Band E\n(V/m)", fontsize=7.2, pad=6)
    band_cbar.set_ticks([BAND_VMIN, 1.00, 1.50, 2.00, BAND_VMAX])
    band_cbar.ax.set_yticklabels([f"<= {BAND_VMIN:.2f}", "1.00", "1.50", "2.00", f">= {BAND_VMAX:.2f}"])
    band_cbar.ax.tick_params(labelsize=6.8)

    total_cax = side.inset_axes([0.05, 0.10, 0.26, 0.34])
    total_cbar = fig.colorbar(total_contour, cax=total_cax)
    total_cbar.ax.set_title("Total RSS\nE (V/m)", fontsize=7.2, pad=6)
    total_cbar.set_ticks([TOTAL_VMIN, 2.00, 3.00, 4.00, TOTAL_VMAX])
    total_cbar.ax.set_yticklabels([f"<= {TOTAL_VMIN:.2f}", "2.00", "3.00", "4.00", f">= {TOTAL_VMAX:.2f}"])
    total_cbar.ax.tick_params(labelsize=6.8)

    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="black",
            markerfacecolor="white",
            markeredgecolor="black",
            markersize=4.5,
            linewidth=0,
            label="Measurement point",
        ),
    ]
    side.legend(
        handles=handles,
        loc="upper left",
        bbox_to_anchor=(0.43, 0.60),
        frameon=True,
        fancybox=False,
        edgecolor="#606060",
        title="Map elements",
        fontsize=6.8,
        title_fontsize=7.4,
    )

    side.text(
        0.43,
        0.43,
        "Geographic north: +Y\nLocal origin shifted\nfor anonymization",
        transform=side.transAxes,
        fontsize=6.7,
        ha="left",
        va="top",
        bbox=dict(facecolor="white", edgecolor="#606060", boxstyle="square,pad=0.35"),
    )


def main():
    df = load_anonymized_dataset()
    xx, yy = make_grid(df)

    fig = plt.figure(figsize=(11.8, 9.2), dpi=DPI)
    gs = fig.add_gridspec(
        2,
        5,
        width_ratios=[1.08, 1.08, 1.08, 1.08, 0.46],
        left=0.035,
        right=0.987,
        top=0.878,
        bottom=0.066,
        wspace=0.015,
        hspace=0.115,
    )

    band_contour = None
    total_contour = None
    for variable, row, column in POSITIONS:
        ax = fig.add_subplot(gs[row, column])
        contour = draw_panel(
            ax,
            df,
            variable,
            MAPS[variable],
            xx,
            yy,
            is_total=variable == "E_total",
        )
        if variable == "LTE800":
            band_contour = contour
        if variable == "E_total":
            total_contour = contour
        if row == 0:
            ax.set_xlabel("")
            ax.tick_params(labelbottom=False)
        if column > 0:
            ax.set_ylabel("")
            ax.tick_params(labelleft=False)

    draw_side_panel(fig, gs[1, 3:5], band_contour, total_contour)

    fig.suptitle(
        "Spatial distribution of RF-EMF exposure in urban Tirana",
        fontsize=15.0,
        fontweight="bold",
        y=0.976,
    )
    fig.text(
        0.5,
        0.925,
        "Anonymized local-coordinate field maps from 171 measurement points; linear interpolation",
        ha="center",
        fontsize=9.6,
    )
    fig.text(
        0.035,
        0.026,
        "Coordinate display: UTM-derived local X/Y in meters from an arbitrary origin; geographic north follows +Y; no area labels, road map, or comparison between sampling areas.",
        fontsize=7.2,
    )

    out_png = OUT / "Figure_3_RF_EMF_171_points_local_XY_linear_compact.png"
    out_tif = OUT / "Figure_3_RF_EMF_171_points_local_XY_linear_compact.tif"
    out_pdf = OUT / "Figure_3_RF_EMF_171_points_local_XY_linear_compact.pdf"

    fig.savefig(out_png, dpi=DPI, bbox_inches="tight", pad_inches=0.08)
    fig.savefig(out_tif, dpi=DPI, bbox_inches="tight", pad_inches=0.08)
    fig.savefig(out_pdf, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)

    print("Total measurement points:", len(df))
    print("Saved PNG:", out_png)
    print("Saved TIF:", out_tif)
    print("Saved PDF:", out_pdf)


if __name__ == "__main__":
    main()
