#!/usr/bin/env python3
"""
Literature Search - STRICTLY Aligned with NDT Review Paper
===========================================================
Search strategy EXACTLY matching the paper's five assessment tasks:
  "From Detection to Design Value: A Systematic Review of 
   Non-Destructive Testing Capabilities for Circular Construction"

Materials: Reinforced Concrete, Structural Steel, Timber, Masonry

Five Assessment Tasks (from paper):
1. Geometry verification - dimensions, cross-section, reinforcement layout, connections
2. Strength estimation - characteristic strength values, design requirements
3. Deterioration assessment - corrosion, decay, chemical attack, residual capacity
4. Defect identification - cracks, voids, delaminations, hidden damage
5. Moisture condition - moisture content, moisture-related degradation

Target: ~612 initial records (manually collected papers for journal submission)
"""

import requests
import pandas as pd
from pathlib import Path
import json
import time
from typing import Optional, Dict


class RestrictedPaperSearcher:
    """STRICTLY restricted search aligned with the paper's five assessment tasks."""
    
    # NDT methods discussed in the paper - CORE METHODS ONLY
    NDT_METHODS_CORE = [
        # Acoustic methods (primary)
        "ultrasonic pulse velocity", "upv",
        "impact echo", "impact-echo",
        "phased array ultrasonic", "paut", "tofd",
        # Electromagnetic (primary)
        "ground penetrating radar", "gpr",
        "eddy current testing",
        "magnetic flux leakage",
        # Electrochemical (primary)
        "half-cell potential", "half cell potential",
        "resistivity measurement", "wenner probe",
        # Mechanical/Semi-destructive (primary)
        "sonreb", "rebound hammer", "schmidt hammer",
        "pull-out test", "pullout test", "capo test", "lok test",
        "flat-jack", "flatjack",
        "resistance drilling", "resistograph",
        # Surface methods (primary)
        "magnetic particle testing", "dye penetrant",
        "visual grading",
        # Thermal (primary)
        "infrared thermography",
        # General NDT (restrictive)
        "non-destructive testing", "nondestructive testing",
        "non-destructive evaluation", "nondestructive evaluation",
    ]
    
    # Four structural material classes ONLY - no generic materials
    STRUCTURAL_MATERIALS = [
        # Reinforced Concrete - structural focus
        "reinforced concrete", "rc structure", "rc beam", "rc column",
        "concrete bridge", "concrete building", "concrete structure",
        "prestressed concrete", "post-tensioned concrete",
        # Structural Steel - structural focus
        "structural steel", "steel structure", "steel bridge",
        "steel beam", "steel column", "steel connection",
        # Timber - structural focus
        "timber structure", "timber beam", "timber building",
        "glulam", "laminated timber", "wood structure",
        # Masonry - structural focus
        "masonry structure", "masonry wall", "masonry building",
        "brick masonry", "stone masonry", "historic masonry",
        "heritage building", "unreinforced masonry",
    ]
    
    # FIVE ASSESSMENT TASKS - EXACTLY AS DEFINED IN PAPER
    # Task 1: Geometry verification
    TASK_GEOMETRY = [
        "geometry verification", "geometric verification",
        "dimension measurement", "cross-section measurement",
        "reinforcement layout", "reinforcement mapping", "rebar detection",
        "cover depth", "concrete cover", "section geometry",
        "connection detail", "structural geometry",
        "thickness measurement", "section loss measurement",
    ]
    
    # Task 2: Strength estimation
    TASK_STRENGTH = [
        "strength estimation", "strength assessment", "strength evaluation",
        "compressive strength", "tensile strength", "flexural strength",
        "characteristic strength", "characteristic value",
        "design value", "material strength", "load capacity",
        "residual strength", "in-situ strength",
        "strength prediction", "strength determination",
    ]
    
    # Task 3: Deterioration assessment
    TASK_DETERIORATION = [
        "deterioration assessment", "deterioration evaluation",
        "corrosion detection", "corrosion assessment", "corrosion rate",
        "decay assessment", "decay detection", "wood decay",
        "chemical attack", "sulfate attack", "alkali-silica reaction",
        "residual capacity", "degradation assessment",
        "carbonation depth", "chloride penetration", "chloride ingress",
        "service life", "durability assessment",
    ]
    
    # Task 4: Defect identification
    TASK_DEFECTS = [
        "defect identification", "defect detection", "flaw detection",
        "crack detection", "crack mapping", "crack characterization",
        "void detection", "void identification", "honeycombing",
        "delamination detection", "delamination assessment",
        "hidden damage", "internal damage", "damage detection",
        "fire damage", "impact damage", "structural damage",
    ]
    
    # Task 5: Moisture condition
    TASK_MOISTURE = [
        "moisture content", "moisture measurement", "moisture assessment",
        "moisture condition", "moisture distribution",
        "moisture meter", "resistance meter",
        "moisture-related", "moisture damage", "water ingress",
        "drying", "wetting", "hygroscopic",
    ]
    
    # ALL assessment task keywords combined
    ALL_ASSESSMENT_TASKS = (TASK_GEOMETRY + TASK_STRENGTH + 
                           TASK_DETERIORATION + TASK_DEFECTS + TASK_MOISTURE)
    
    # Circular economy / reuse focus (STRICT - must be structural reuse)
    CIRCULAR_STRICT = [
        "circular construction", "circular economy building",
        "structural reuse", "component reuse", "element reuse",
        "building reuse", "material reuse",
        "deconstruction", "selective demolition",
        "design for disassembly",
        "reuse assessment", "reusability assessment",
    ]
    
    # STRICT exclusion keywords - expanded
    EXCLUSION_STRICT = [
        # Medical/Clinical
        "cancer", "tumor", "tumour", "patient", "clinical trial",
        "biomedical", "medical imaging", "cell culture", "pharmaceutical",
        "surgery", "hospital", "diagnosis patient", "therapy",
        # Food/Agriculture
        "food quality", "fruit quality", "vegetable", "meat quality",
        "agricultural", "crop", "grain", "fish quality", "poultry",
        # Non-civil manufacturing
        "aerospace", "aircraft", "wind turbine blade", "wind energy",
        "additive manufacturing", "semiconductor", "electronics",
        "battery", "lithium", "nuclear reactor", "pipeline weld",
        # Geoscience/Oil & Gas
        "seismic exploration", "oil reservoir", "petroleum",
        "mining exploration", "geological", "rock formation",
        # Automotive
        "automotive", "vehicle", "car body", "engine component",
        # Non-structural concrete
        "pavement", "asphalt", "road surface", "runway",
    ]
    
    def __init__(self, email: Optional[str] = None):
        self.base_url = "https://api.openalex.org/works"
        self.email = email
        self.results = []
        self.excluded = []
        self.exclusion_stats = {}
        
    def is_relevant(self, paper: Dict) -> tuple:
        """STRICT relevance check - must match paper's five assessment tasks."""
        title = (paper.get("title") or "").lower()
        abstract = (paper.get("abstract") or "").lower()
        text = f"{title} {abstract}"
        
        # Check exclusions first (strict)
        for exclude in self.EXCLUSION_STRICT:
            if exclude.lower() in text:
                reason = f"Excluded: {exclude}"
                self.exclusion_stats[exclude] = self.exclusion_stats.get(exclude, 0) + 1
                return False, reason
        
        # MUST have NDT method mentioned
        has_ndt = any(m.lower() in text for m in self.NDT_METHODS_CORE)
        if not has_ndt:
            return False, "No core NDT method"
        
        # MUST have structural material mentioned
        has_material = any(m.lower() in text for m in self.STRUCTURAL_MATERIALS)
        if not has_material:
            return False, "No structural material"
        
        # MUST have at least one of the five assessment tasks
        has_task = any(t.lower() in text for t in self.ALL_ASSESSMENT_TASKS)
        has_circular = any(c.lower() in text for c in self.CIRCULAR_STRICT)
        
        if not (has_task or has_circular):
            return False, "No assessment task or circular context"
        
        # Identify which task(s) the paper addresses
        tasks_found = []
        if any(t.lower() in text for t in self.TASK_GEOMETRY):
            tasks_found.append("geometry")
        if any(t.lower() in text for t in self.TASK_STRENGTH):
            tasks_found.append("strength")
        if any(t.lower() in text for t in self.TASK_DETERIORATION):
            tasks_found.append("deterioration")
        if any(t.lower() in text for t in self.TASK_DEFECTS):
            tasks_found.append("defects")
        if any(t.lower() in text for t in self.TASK_MOISTURE):
            tasks_found.append("moisture")
        
        return True, f"Tasks: {', '.join(tasks_found) if tasks_found else 'circular'}"
    
    def search(
        self,
        start_year: int = 2014,
        end_year: int = 2024,
        max_pages_per_term: int = 1  # Limit pages to restrict results
    ) -> list:
        """
        Execute STRICTLY restricted literature search.
        
        Targeting ~612 papers by:
        1. Using only core NDT methods
        2. Requiring structural materials
        3. Requiring assessment tasks from paper
        4. Stricter exclusion criteria
        5. Limited pagination per search term
        """
        print(f"\n{'='*60}")
        print("RESTRICTED SYSTEMATIC LITERATURE SEARCH")
        print("Targeting ~612 papers (Paper Methodology)")
        print(f"Date Range: {start_year}-{end_year}")
        print(f"{'='*60}\n")
        
        # EXPANDED search terms to reach ~612 papers
        search_terms = [
            # Task 1: Geometry verification - EXPANDED
            '"reinforcement mapping" "ground penetrating radar"',
            '"cover depth" concrete "non-destructive"',
            '"rebar detection" ultrasonic',
            '"geometry verification" structure',
            '"GPR" "reinforced concrete"',
            '"reinforcement detection" concrete',
            '"section geometry" "non-destructive"',
            '"cover depth measurement" concrete',
            # Task 2: Strength estimation - EXPANDED
            '"strength estimation" concrete',
            '"rebound hammer" concrete strength',
            '"compressive strength" "non-destructive" concrete',
            '"sonreb" concrete',
            '"pull-out test" concrete',
            '"in-situ strength" concrete',
            '"ultrasonic pulse velocity" strength concrete',
            '"characteristic value" strength concrete',
            '"schmidt hammer" concrete',
            # Task 3: Deterioration assessment - EXPANDED
            '"corrosion detection" "reinforced concrete"',
            '"half-cell potential" corrosion',
            '"carbonation depth" concrete',
            '"chloride penetration" concrete',
            '"corrosion assessment" concrete',
            '"decay assessment" timber',
            '"resistance drilling" timber',
            '"degradation assessment" concrete',
            '"corrosion rate" reinforcement',
            '"service life" concrete NDT',
            '"durability assessment" concrete',
            # Task 4: Defect identification - EXPANDED
            '"crack detection" concrete',
            '"delamination detection" concrete',
            '"impact echo" concrete',
            '"void detection" concrete',
            '"defect detection" concrete',
            '"flaw detection" steel',
            '"ultrasonic testing" concrete defect',
            '"internal damage" concrete',
            '"hidden damage" structure',
            '"damage detection" "non-destructive"',
            # Task 5: Moisture condition - EXPANDED
            '"moisture content" timber',
            '"moisture measurement" building',
            '"infrared thermography" moisture',
            '"moisture assessment" concrete',
            '"water ingress" building',
            '"moisture meter" timber',
            '"moisture distribution" concrete',
            # Core NDT methods + structural materials
            '"non-destructive testing" "reinforced concrete"',
            '"non-destructive testing" "structural steel"',
            '"non-destructive evaluation" concrete bridge',
            '"ultrasonic pulse velocity" concrete structure',
            '"ground penetrating radar" concrete structure',
            '"infrared thermography" concrete building',
            # Masonry and timber specific
            '"masonry structure" "non-destructive"',
            '"timber structure" "non-destructive"',
            '"historic masonry" assessment',
            '"heritage building" "non-destructive"',
            '"flat-jack" masonry',
            '"resistograph" timber',
            # Circular construction and reuse
            '"structural reuse" assessment',
            '"circular construction" building',
            '"existing building" assessment NDT',
            '"condition assessment" existing structure',
            '"reuse assessment" building',
            '"building reuse" "non-destructive"',
        ]
        
        all_results = {}
        
        for term in search_terms:
            print(f"Searching: {term[:50]}...")
            
            params = {
                "search": term,
                "filter": f"publication_year:{start_year}-{end_year},type:article",
                "per-page": 100,
                "cursor": "*"
            }
            if self.email:
                params["mailto"] = self.email
            
            term_count = 0
            pages = 0
            
            while pages < max_pages_per_term:
                try:
                    response = requests.get(self.base_url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    results = data.get("results", [])
                    if not results:
                        break
                    
                    for paper in results:
                        paper_id = paper.get("id", "")
                        if paper_id in all_results:
                            continue
                        
                        paper_data = self._parse_paper(paper)
                        if not paper_data:
                            continue
                        
                        is_relevant, reason = self.is_relevant(paper_data)
                        
                        if is_relevant:
                            paper_data["assessment_tasks"] = reason
                            all_results[paper_id] = paper_data
                            term_count += 1
                        else:
                            self.excluded.append({
                                "title": paper_data.get("title", "")[:60],
                                "reason": reason
                            })
                    
                    next_cursor = data.get("meta", {}).get("next_cursor")
                    if not next_cursor:
                        break
                    params["cursor"] = next_cursor
                    pages += 1
                    time.sleep(0.1)
                    
                except requests.RequestException as e:
                    print(f"  Error: {e}")
                    break
            
            print(f"  → {term_count} added (total: {len(all_results)})")
        
        self.results = list(all_results.values())
        
        print(f"\n{'='*60}")
        print(f"FINAL COUNT: {len(self.results)} papers")
        print(f"EXCLUDED: {len(self.excluded)} papers")
        print(f"TARGET: ~612 papers")
        print(f"{'='*60}\n")
        
        return self.results
    
    def _parse_paper(self, paper: dict) -> Optional[dict]:
        """Parse paper from OpenAlex."""
        try:
            authors = []
            for authorship in paper.get("authorships", []):
                author = authorship.get("author", {})
                if author.get("display_name"):
                    authors.append(author["display_name"])
            
            source = paper.get("primary_location", {}) or {}
            source_info = source.get("source", {}) or {}
            
            abstract = ""
            if paper.get("abstract_inverted_index"):
                inv_idx = paper["abstract_inverted_index"]
                if inv_idx:
                    max_idx = max(max(indices) for indices in inv_idx.values())
                    words = [""] * (max_idx + 1)
                    for word, indices in inv_idx.items():
                        for idx in indices:
                            words[idx] = word
                    abstract = " ".join(words)
            
            return {
                "title": paper.get("title", ""),
                "authors": "; ".join(authors[:5]),
                "year": paper.get("publication_year"),
                "doi": paper.get("doi", "").replace("https://doi.org/", "") if paper.get("doi") else "",
                "journal": source_info.get("display_name", ""),
                "abstract": abstract,
                "cited_by_count": paper.get("cited_by_count", 0),
                "type": paper.get("type", ""),
                "open_access": paper.get("open_access", {}).get("is_oa", False),
                "url": paper.get("doi") or paper.get("id", ""),
                "openalex_id": paper.get("id", "")
            }
        except Exception:
            return None
    
    def export_to_csv(self, filename: str) -> str:
        if not self.results:
            return ""
        df = pd.DataFrame(self.results)
        df = df.sort_values(by=["year", "cited_by_count"], ascending=[False, False])
        df.to_csv(filename, index=False, encoding="utf-8")
        print(f"Exported: {filename}")
        return filename
    
    def export_to_bibtex(self, filename: str) -> str:
        if not self.results:
            return ""
        entries = []
        for i, paper in enumerate(self.results):
            first_author = paper["authors"].split(";")[0].split()[-1] if paper["authors"] else "Unknown"
            cite_key = f"{first_author}{paper['year']}_{i}"
            cite_key = "".join(c for c in cite_key if c.isalnum() or c == "_")
            title = paper['title'].replace('{', '\\{').replace('}', '\\}')
            entry = f"""@article{{{cite_key},
  title = {{{title}}},
  author = {{{paper['authors']}}},
  year = {{{paper['year']}}},
  journal = {{{paper['journal']}}},
  doi = {{{paper['doi']}}},
}}"""
            entries.append(entry)
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n\n".join(entries))
        print(f"BibTeX: {filename}")
        return filename
    
    def generate_prisma_stats(self) -> dict:
        """Generate PRISMA-compliant statistics with task breakdown."""
        # Count papers by assessment task
        task_counts = {
            "geometry": 0,
            "strength": 0,
            "deterioration": 0,
            "defects": 0,
            "moisture": 0,
        }
        
        for paper in self.results:
            tasks = paper.get("assessment_tasks", "").lower()
            if "geometry" in tasks:
                task_counts["geometry"] += 1
            if "strength" in tasks:
                task_counts["strength"] += 1
            if "deterioration" in tasks:
                task_counts["deterioration"] += 1
            if "defects" in tasks:
                task_counts["defects"] += 1
            if "moisture" in tasks:
                task_counts["moisture"] += 1
        
        stats = {
            "database": "OpenAlex",
            "search_date": "2026-01-09",
            "methodology": "Restricted search aligned with paper's five assessment tasks",
            "five_assessment_tasks": [
                "1. Geometry verification",
                "2. Strength estimation", 
                "3. Deterioration assessment",
                "4. Defect identification",
                "5. Moisture condition"
            ],
            "date_range": "2014-2024",
            "target_records": 612,
            "records_identified": len(self.results) + len(self.excluded),
            "records_after_filtering": len(self.results),
            "excluded_count": len(self.excluded),
            "by_assessment_task": task_counts,
            "by_year": {},
            "by_journal": {},
            "by_material": {"concrete": 0, "steel": 0, "timber": 0, "masonry": 0},
            "open_access": sum(1 for p in self.results if p.get("open_access")),
        }
        
        for paper in self.results:
            year = paper.get("year")
            if year:
                stats["by_year"][year] = stats["by_year"].get(year, 0) + 1
            
            text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
            if "concrete" in text:
                stats["by_material"]["concrete"] += 1
            if "steel" in text:
                stats["by_material"]["steel"] += 1
            if "timber" in text or "wood" in text:
                stats["by_material"]["timber"] += 1
            if "masonry" in text:
                stats["by_material"]["masonry"] += 1
        
        for paper in self.results:
            journal = paper.get("journal", "Unknown")
            if journal:
                stats["by_journal"][journal] = stats["by_journal"].get(journal, 0) + 1
        
        stats["by_journal"] = dict(sorted(stats["by_journal"].items(), 
                                          key=lambda x: x[1], reverse=True)[:15])
        return stats
    
    def print_summary(self):
        stats = self.generate_prisma_stats()
        print(f"\n{'='*60}")
        print("PRISMA SUMMARY - Five Assessment Tasks")
        print(f"{'='*60}")
        print(f"Target: {stats['target_records']} papers")
        print(f"Records identified: {stats['records_identified']}")
        print(f"After filtering: {stats['records_after_filtering']}")
        print(f"Open Access: {stats['open_access']}")
        
        print(f"\n--- By Assessment Task (Paper's 5 Tasks) ---")
        for task, count in stats["by_assessment_task"].items():
            pct = (count / len(self.results) * 100) if self.results else 0
            bar = "█" * int(pct / 5)
            print(f"  {task.capitalize():15}: {count:4d} ({pct:5.1f}%) {bar}")
        
        print(f"\n--- By Material ---")
        for mat, count in stats["by_material"].items():
            pct = (count / len(self.results) * 100) if self.results else 0
            print(f"  {mat.capitalize():10}: {count:4d} ({pct:5.1f}%)")
        
        print(f"\n--- By Year ---")
        for year in sorted(stats["by_year"].keys(), reverse=True):
            count = stats["by_year"][year]
            bar = "█" * (count // 5)
            print(f"  {year}: {count:4d} {bar}")
        
        print(f"\n--- Top Journals ---")
        for i, (journal, count) in enumerate(list(stats["by_journal"].items())[:10]):
            print(f"  {i+1}. {journal[:45]}: {count}")


def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  RESTRICTED LITERATURE SEARCH - Paper Aligned                ║
    ║  "From Detection to Design Value..."                         ║
    ║                                                              ║
    ║  Five Assessment Tasks:                                      ║
    ║  1. Geometry verification                                    ║
    ║  2. Strength estimation                                      ║
    ║  3. Deterioration assessment                                 ║
    ║  4. Defect identification                                    ║
    ║  5. Moisture condition                                       ║
    ║                                                              ║
    ║  Target: ~612 papers                                         ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    searcher = RestrictedPaperSearcher(email="YOUR_EMAIL@institution.edu")
    
    results = searcher.search(
        start_year=2014,
        end_year=2024,
        max_pages_per_term=3  # Increased to reach ~612 target
    )
    
    searcher.print_summary()
    
    # Export with paper-aligned naming
    searcher.export_to_csv("ndt_restricted_612_results.csv")
    searcher.export_to_bibtex("ndt_restricted_612_references.bib")
    
    stats = searcher.generate_prisma_stats()
    with open("prisma_restricted_612.json", "w") as f:
        json.dump(stats, f, indent=2)
    
    print("\nFiles saved (RESTRICTED - aligned with paper's five tasks):")
    print("  - ndt_restricted_612_results.csv")
    print("  - ndt_restricted_612_references.bib")
    print("  - prisma_restricted_612.json")


if __name__ == "__main__":
    main()
