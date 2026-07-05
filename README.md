[README.md](https://github.com/user-attachments/files/29680581/README.md)
# Urban RF-EMF Mapping - Tirana

This repository contains the anonymized dataset, Python script and publication-ready figures for the spatial mapping of multi-band radiofrequency electromagnetic field (RF-EMF) exposure in urban Tirana.

## Repository contents

```text
urban-rf-emf-mapping-tirana/
├── data/
│   ├── anonymized_rf_emf_dataset_local_xy.xlsx
│   └── anonymized_rf_emf_dataset_local_xy.csv
├── scripts/
│   └── field_maps_171_points_local_xy_compact.py
├── outputs/
│   └── figures/
│       ├── Figure_3_RF_EMF_171_points_local_XY_linear_compact.png
│       ├── Figure_3_RF_EMF_171_points_local_XY_linear_compact.tif
│       └── Figure_3_RF_EMF_171_points_local_XY_linear_compact.pdf
├── README.md
├── requirements.txt
├── LICENSE
├── CITATION.cff
└── CHANGELOG.md
```

## Data anonymization

The public dataset is anonymized. Original latitude/longitude coordinates, raw file names, sampling-area labels, dates and times are not included.

The coordinate columns `x_local_m` and `y_local_m` are UTM-derived local coordinates shifted to an arbitrary origin. They preserve the relative spatial distribution of the 171 measurement points while avoiding publication of exact field locations.

## Main outputs

The script generates a compact multi-panel figure showing:

- LTE 800 exposure map;
- GSM 900 exposure map;
- LTE 1800 exposure map;
- UMTS 2100 exposure map;
- LTE 2600 exposure map;
- 5G NR 3600 exposure map;
- total RF-EMF exposure calculated as root-sum-square (RSS).

The figure is exported in PNG, TIFF and PDF formats.

## How to reproduce

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the script from the repository root:

```bash
python scripts/field_maps_171_points_local_xy_compact.py
```

Generated figures will be saved in:

```text
outputs/figures/
```

## Version information

Version `v1.1` updates the dataset, script and generated figures following peer-review revisions.

## License

This repository is distributed under the MIT License.
