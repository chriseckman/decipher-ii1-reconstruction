"""Apply figure titles, witness labels and accessible styles to existing SVGs.

Usage: python presentation_updater.py INPUT_DIRECTORY OUTPUT_DIRECTORY
This changes presentation only; numerical data are not regenerated.
"""
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

CAPTIONS = {'figS1_key_usage.svg': {'340.0': 'Combined source coverage: 224/492 positions; dark blue = forward, grey = '
                                  'reversed.',
                         '22.0': 'Distribution of the 314 cipher numbers (corrected transcription)'},
 'figS2_window_control.svg': {'22.0': 'F1 histogram: 454,033 windows of the MY-restored Wikisource transcription',
                              '70.0': 'Family comparison annotations'},
 'figS3_coverage.svg': {'22.0': 'Dictionary coverage: fraction covered by dictionary spans of 3-18 letters',
                        '160.0': ''},
 'figS4_fold_detection.svg': {'22.0': 'Exploratory fold statistic: far-apart adjacent numbers summing to R',
                              '70.0': 'Observed: blue; shuffle mean: dashed light grey; 99th percentile: solid dark grey',
                              '330.0': 'Adjacent pairs: |a-b| >= 100, |a+b-R| <= 1. Maximum-over-R shuffle p = '
                                       '0.0005 (2,000 shuffles); exploratory.'},
 'fig2_edition_drift.svg': {'22.0': 'Textual alignment: 1801-attributed Wikisource transcription omits MY (Alden '
                                    'positions 94-95)',
                            '142.0': 'Wikisource transcription from 2 letters earlier (post-answer anchor): 260 '
                                     'of 314 letters agree',
                            '270.0': 'Anchors align on opposite sides of MY; first differing source letter: 95 '
                                     '(MY spans 94-95).',
                            '288.0': 'Post-answer alignment identified the shift; the Alden witness supplied MY. '
                                     'Coincidental letter matches can occur.',
                            '56.0': "Wikisource transcription from the paragraph's first letter: 55 of 314 "
                                    'letters agree',
                            '248.0': 'Numbers sorted by source position (1-492); dark blue = agreement with '
                                     'Alden, light grey = difference'},
 'fig1_key_construction.svg': {'26.0': 'Two-way numbering of the 492-letter source (984 key slots)',
                               '318.0': 'Each source position has two key slots (n and 985 - n), including '
                                        'position 492 at slots 492 and 493.'}}

SOURCE_POSITION_LABELS = {'source letter index 1': 'source position 1', 'forward half: number n names source letter n': 'forward half: key slot n names source position n', 'reversed half: number n names source letter 985 - n': 'reversed half: key slot n names source position 985 - n', 'turnaround: 492 and 493 both name source letter 492': 'turnaround: slots 492 and 493 both name source position 492'}

COLORS = {
 'fig1_key_construction.svg': {'#2e7d32': '#1f4e79', '#c62828': '#7c7c7c'},
 'fig2_edition_drift.svg': {'#2e7d32': '#1f4e79', '#c62828': '#d1d5db'},
 'figS1_key_usage.svg': {'#2e7d32': '#1f4e79', '#c62828': '#7c7c7c'},
 'figS2_window_control.svg': {'#c62828': '#1f4e79', '#1f4e8c': '#7c7c7c'},
 'figS3_coverage.svg': {'#c62828': '#1f4e79', '#1f4e8c': '#555555'},
 'figS4_fold_detection.svg': {'#c62828': '#1f4e79'},
}

PRESENTATION_ATTRIBUTES = {'fill', 'stroke', 'stroke-width', 'stroke-dasharray',
 'opacity', 'style', 'font-size', 'font-family', 'font-weight', 'text-anchor',
 'fill-opacity', 'stroke-opacity'}

def escaped(text):
 return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def geometry(svg):
 root = ET.fromstring(svg)
 return [(element.tag, sorted((name, value) for name, value in element.attrib.items()
   if name not in PRESENTATION_ATTRIBUTES)) for element in root.iter()
   if element.tag.split('}')[-1] not in {'text', 'tspan', 'title', 'desc'}]

def update(original, filename):
 updated = original
 if filename == 'fig1_key_construction.svg':
  for old, new in SOURCE_POSITION_LABELS.items():
   updated = updated.replace(escaped(old), escaped(new))
  updated = updated.replace("Gulliver's Travels III.2 (Alden 1911, p. 97): A-Z letters only, 492", "Gulliver's Travels III.2 (Alden witness, 1911 copyright, p. 97): 492 A-Z letters")
 if filename == 'figS1_key_usage.svg':
  updated = updated.replace('source letter index named (1-492)', 'source position named (1-492)')
 for y, caption in CAPTIONS.get(filename, {}).items():
  pattern = r"(<text\b[^>]*\by=['\"]" + re.escape(y) + r"['\"][^>]*>)([^<]*)(</text>)"
  updated, count = re.subn(pattern, lambda match: match.group(1) + escaped(caption) + match.group(3), updated)
  if count != 1:
   raise ValueError(f"Expected one caption at y={y} in {filename}, found {count}")
 for old, new in COLORS[filename].items():
  updated = updated.replace(old, new)
 if filename == 'fig2_edition_drift.svg':
  updated = re.sub(r"(<text\b[^>]*\by=['\"]22\.0['\"][^>]*\bfont-size=)['\"]14['\"]", r"\g<1>'12'", updated)
 if filename == 'figS4_fold_detection.svg':
  updated = re.sub(r"(<text\b[^>]*\by=['\"]70\.0['\"][^>]*\btext-anchor=)['\"]start['\"]", r"\g<1>'end'", updated)
  updated = re.sub(r"(<polyline\b[^>]*\bstroke=['\"]#bbbbbb['\"])(?![^>]*\bstroke-dasharray=)", r"\1 stroke-dasharray='4,3'", updated)
 assert geometry(original) == geometry(updated), filename
 return updated
def main(source, target):
 source, target = Path(source), Path(target)
 if source.resolve() == target.resolve():
  raise SystemExit("Use a new output directory to preserve supplied originals.")
 if target.exists() and any(target.iterdir()):
  raise SystemExit("Output directory must be new or empty.")
 target.mkdir(parents=True, exist_ok=True)
 receipt = {"scope": "presentation replay only; not numerical replication", "files": []}
 for filename in CAPTIONS:
  original = (source / filename).read_text(encoding="utf-8")
  updated = update(original, filename)
  output = target / filename
  output.write_bytes(updated.encode("utf-8"))
  receipt["files"].append({"file": filename, "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "geometry_unchanged": True})
 (target / "presentation-replay-receipt.json").write_bytes((json.dumps(receipt, indent=2) + "\n").encode("utf-8"))
 print(json.dumps(receipt, indent=2))
if __name__ == "__main__":
 if len(sys.argv) != 3:
  raise SystemExit(__doc__)
 main(*sys.argv[1:])
