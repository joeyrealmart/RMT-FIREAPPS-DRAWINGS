import xml.etree.ElementTree as ET
from PIL import Image
import json
import os
import sys

def validate():
    floors = ['lower_ground', 'ground', 'level1', 'upper', 'roof', 'site_plan']
    passed = 0
    failed = 0

    print("=== STARTING DETERMINISTIC QA CHECKS FOR ADMIRAL MARINA CLUB ===")

    for name in floors:
        print(f"\nChecking floor: {name}...")

        # 1. Validate Metadata JSON
        meta_path = f'admiral_{name}_metadata.json'
        if not os.path.exists(meta_path):
            print(f"  [FAIL] Missing metadata JSON: {meta_path}")
            failed += 1
            continue
        with open(meta_path) as f:
            meta = json.load(f)

        if meta.get('site') != 'Admiral Marina Club':
            print(f"  [FAIL] Invalid site name in {meta_path}")
            failed += 1
        elif meta.get('review_status') != 'REVIEW_REQUIRED':
            print(f"  [FAIL] Missing REVIEW_REQUIRED status in {meta_path}")
            failed += 1
        elif not meta.get('identity_evidence'):
            print(f"  [FAIL] Missing identity_evidence in {meta_path}")
            failed += 1
        else:
            print(f"  [PASS] Metadata JSON valid and records identity evidence.")
            passed += 1

        # 2. Validate Device Pins JSON
        dev_path = f'admiral_{name}_devices.json'
        if not os.path.exists(dev_path):
            print(f"  [FAIL] Missing device JSON: {dev_path}")
            failed += 1
            continue
        with open(dev_path) as f:
            devs = json.load(f)
        print(f"  [PASS] Device JSON valid (separate pins: {len(devs)} devices).")
        passed += 1

        # 3. Validate SVG parsing and structure
        svg_path = f'admiral_{name}_mimic.svg'
        if not os.path.exists(svg_path):
            print(f"  [FAIL] Missing SVG: {svg_path}")
            failed += 1
            continue
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            if not root.tag.endswith('svg'):
                print(f"  [FAIL] Root tag is not svg in {svg_path}")
                failed += 1
            else:
                viewbox = root.attrib.get('viewBox')
                if not viewbox:
                    print(f"  [FAIL] Missing viewBox in {svg_path}")
                    failed += 1
                else:
                    print(f"  [PASS] SVG parses cleanly as valid XML (viewBox: {viewbox}).")
                    passed += 1
        except Exception as e:
            print(f"  [FAIL] XML parse error in {svg_path}: {e}")
            failed += 1

        # 4. Validate PNG image non-blank and bounds
        png_path = f'admiral_{name}_mimic.png'
        if not os.path.exists(png_path):
            print(f"  [FAIL] Missing PNG: {png_path}")
            failed += 1
            continue
        try:
            img = Image.open(png_path)
            w, h = img.size
            if w < 500 or h < 500 or os.path.getsize(png_path) < 10000:
                print(f"  [FAIL] PNG image blank or too small: {png_path} ({w}x{h})")
                failed += 1
            else:
                print(f"  [PASS] High-res PNG image valid and non-blank ({w}x{h}, {os.path.getsize(png_path)} bytes).")
                passed += 1
        except Exception as e:
            print(f"  [FAIL] PNG load error in {png_path}: {e}")
            failed += 1

        # 5. Validate Visual Comparison image
        comp_path = f'admiral_{name}_visual_comparison.png'
        if not os.path.exists(comp_path):
            print(f"  [FAIL] Missing comparison PNG: {comp_path}")
            failed += 1
        else:
            img_comp = Image.open(comp_path)
            print(f"  [PASS] Visual comparison image exists ({img_comp.width}x{img_comp.height}).")
            passed += 1

        # 6. Validate Review HTML
        html_path = f'admiral_{name}_review.html'
        if not os.path.exists(html_path):
            print(f"  [FAIL] Missing review HTML: {html_path}")
            failed += 1
        else:
            with open(html_path) as f:
                html = f.read()
            if 'REVIEW_REQUIRED' not in html or 'Admiral Marina Club' not in html:
                print(f"  [FAIL] Review HTML missing REVIEW_REQUIRED flag in {html_path}")
                failed += 1
            else:
                print(f"  [PASS] Review HTML valid and flagged REVIEW_REQUIRED.")
                passed += 1

    print(f"\nQA Summary: {passed} checks passed, {failed} checks failed.")
    if failed > 0:
        sys.exit(1)
    else:
        print("ALL DETERMINISTIC QA CHECKS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    validate()
