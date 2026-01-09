# NDT Literature Search

Systematic literature search for the paper: **"From Detection to Design Value: A Systematic Review of Non-Destructive Testing Capabilities for Circular Construction"**

## Overview

This repository contains the automated literature search methodology aligned with PRISMA guidelines for identifying NDT studies across four structural materials and five assessment tasks.

### Five Assessment Tasks

1. **Geometry verification** - dimensions, cross-section, reinforcement layout, connections
2. **Strength estimation** - characteristic strength values, design requirements
3. **Deterioration assessment** - corrosion, decay, chemical attack, residual capacity
4. **Defect identification** - cracks, voids, delaminations, hidden damage
5. **Moisture condition** - moisture content, moisture-related degradation

### Four Structural Materials

- Reinforced Concrete
- Structural Steel
- Timber
- Masonry

## Files

| File | Description |
|------|-------------|
| `literature_search_paper_aligned.py` | Main search script using OpenAlex API |
| `ndt_restricted_612_results.csv` | Search results (CSV format) |
| `ndt_restricted_612_references.bib` | BibTeX references |
| `prisma_restricted_612.json` | PRISMA statistics with task breakdown |
| `NDT_Review_main.tex` | Main LaTeX paper |

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the literature search
python literature_search_paper_aligned.py
```

### Configuration

Edit `literature_search_paper_aligned.py` to customize:

```python
# Replace with your email for OpenAlex API (optional but recommended)
searcher = RestrictedPaperSearcher(email="YOUR_EMAIL@institution.edu")

# Adjust search parameters
results = searcher.search(
    start_year=2014,
    end_year=2024,
    max_pages_per_term=3  # Increase for more results
)
```

## Search Methodology

The systematic search for the paper was conducted across **Scopus, Web of Science, and Engineering Village**. This repository provides a replication script using the [OpenAlex API](https://openalex.org/), which indexes content from multiple academic sources.

The script uses:
- **70 targeted search terms** covering all five assessment tasks
- **Strict inclusion criteria**: Must mention NDT method + structural material + assessment task
- **Exclusion filters**: Medical, food science, aerospace, automotive, and geoscience domains

### Search Strategy (PRISMA)

```
("non-destructive testing" OR "NDT" OR "NDE" OR "ultrasonic" OR "GPR" OR 
"rebound hammer" OR "half-cell" OR "infrared thermography") 
AND 
("reinforced concrete" OR "structural steel" OR "timber structure" OR 
"masonry structure" OR "heritage building") 
AND 
("geometry verification" OR "strength estimation" OR "deterioration" OR 
"defect detection" OR "moisture" OR "corrosion" OR "condition assessment" 
OR "structural reuse" OR "characteristic value")
```

## Output

The script generates:
- **CSV file** with paper metadata (title, authors, year, DOI, journal, abstract)
- **BibTeX file** for LaTeX citation
- **JSON file** with PRISMA statistics broken down by:
  - Assessment task
  - Material type
  - Publication year
  - Top journals

## License

This project is for academic research purposes.

## Citation

If you use this search methodology, please cite:

```bibtex
@article{ndt_circular_construction_2024,
  title={From Detection to Design Value: A Systematic Review of Non-Destructive Testing Capabilities for Circular Construction},
  author={[Authors]},
  journal={[Journal]},
  year={2024}
}
```
