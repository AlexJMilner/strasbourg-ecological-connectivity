# Strasbourg Ecology GIS — Corridors & connectivité écologique

Projet d’écologie spatiale : création de noyaux d’habitats, surface de friction, corridors (least-cost) et goulots d’étranglement à partir de données d’occupation du sol (OSM) avec Python + QGIS.

## Contenu
- `src/` : scripts Python (pipeline)
- `data/` : données (raw/interim/processed)
- `outputs/` : cartes/export finaux
- `rapport.pdf` : rapport du projet (si présent)

## Lancer (ordre simple)
Depuis la racine du projet :

```bash
python src/03_core_habitats.py
python src/04_resistance_prep.py
python src/05_rasterize_resistance.py
python src/06_corridors_lcp.py
python src/07_corridor_zones.py
python src/08_bottlenecks.py
