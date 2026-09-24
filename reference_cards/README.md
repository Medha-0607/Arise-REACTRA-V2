# REACTRA V2 — PHYSICAL DEMO REFERENCE CARD
### Software Test & Optical Calibration Fixture

> **MANDATORY NOTICE: CALIBRATION AID ONLY**  
> `REACTRA DEMO REFERENCE CARD`  
> `SOFTWARE TEST / CALIBRATION AID — NOT A CHEMICAL TEST`  
> This reference card is an optical reference standard and test fixture engineered specifically to validate camera acquisition, homography detection, color calibration, and region-of-interest (ROI) extraction in the REACTRA computer vision pipeline. It does **NOT** contain real chemical reagents and does **NOT** represent an actual chemical reaction.

---

## 1. Generated Assets

The following authoritative files have been generated in the `reference_cards/` directory:

| File | Format | Resolution / Dimensions | Purpose |
| :--- | :--- | :--- | :--- |
| **`REACTRA_DEMO_REFERENCE_CARD_HIGHRES.png`** | PNG | 2400 × 1600 px @ 300 DPI | High-resolution standalone reference card master image. |
| **`REACTRA_DEMO_REFERENCE_CARD.pdf`** | PDF | 150.0 mm × 100.0 mm @ 300 DPI | Exact physical size single-card PDF for direct cardstock printing. |
| **`REACTRA_DEMO_REFERENCE_CARD_A4_PRINT_SHEET.png`** | PNG | 2480 × 3508 px (A4 @ 300 DPI) | Complete printable sheet with 1:1 scale card, cutting marks, and 100 mm scale ruler. |
| **`REACTRA_DEMO_REFERENCE_CARD_A4_PRINT_SHEET.pdf`** | PDF | ISO A4 (210 mm × 297 mm) | Print-ready PDF sheet with verified physical dimensions. |

---

## 2. Physical & Optical Specifications

- **Profile Identifier:** `MARQUIS-STANDARD-V1` (Canonical Profile `STANDARD_GRID_PROFILE`)
- **Card ID:** `REF-CARD-GRID-3X2`
- **Physical Dimensions:** **150.0 mm (Width) × 100.0 mm (Height)** (Aspect Ratio: **1.50**)
- **Base Canonical Grid:** 600 × 400 pixels
- **High-Res Master Resolution:** 2400 × 1600 pixels (4.0× scale factor)
- **Print Resolution:** 300 DPI (11.811 pixels per mm)

### 2.1 Reference Calibration Patches (6-Patch Colorimetric Array)

All 6 patches measure **60 × 60 px** on the base 600×400 grid (**240 × 240 px** on the 2400×1600 high-res card; **15.0 mm × 15.0 mm** physical):

| # | Patch Name | Canonical ROI `[x, y, w, h]` | Reference Target CIE L\*a\*b\* | Nominal sRGB `[R, G, B]` |
| :-: | :--- | :--- | :--- | :--- |
| 1 | **White Reference** | `[40, 30, 60, 60]` | `[95.0, 0.0, 0.0]` | `[245, 245, 245]` |
| 2 | **Light Gray (70%)** | `[130, 30, 60, 60]` | `[70.0, 0.0, 0.0]` | `[178, 178, 178]` |
| 3 | **Mid Gray (50%)** | `[220, 30, 60, 60]` | `[50.0, 0.0, 0.0]` | `[128, 128, 128]` |
| 4 | **Black Reference** | `[310, 30, 60, 60]` | `[10.0, 0.0, 0.0]` | `[25, 25, 25]` |
| 5 | **Cyan Reference** | `[400, 30, 60, 60]` | `[60.0, -30.0, -25.0]` | `[0, 180, 200]` |
| 6 | **Magenta Reference** | `[490, 30, 60, 60]` | `[50.0, 55.0, -15.0]` | `[200, 40, 150]` |

### 2.2 Reaction Wells (Circular ROIs)

| # | Well Identifier | Canonical Center `(x, y)` | Radius | Description / Simulated State | Nominal sRGB | Target CIE L\*a\*b\* |
| :-: | :--- | :--- | :-: | :--- | :--- | :--- |
| 1 | **`well_1`** | `(140, 240)` | 50 px (12.5 mm) | **Primary Reaction Well** (Simulated Marquis Purple Positive) | `[128, 0, 128]` | `[35.0, 30.0, -15.0]` |
| 2 | **`well_2`** | `(460, 240)` | 50 px (12.5 mm) | **Negative Control Well** (Simulated Blank Substrate) | `[230, 230, 220]` | `[90.0, 0.0, 2.0]` |

---

## 3. Printing & Physical Preparation Guide

1. **Intended Print Scale:**
   - Always print at **100% Scale / "Actual Size"**.
   - **DO NOT** select "Fit to Page", "Shrink to Printable Area", or scale-to-fit options.
   - Verify the physical scale by measuring the printed 100 mm scale ruler at the bottom of the A4 sheet with a physical metric ruler.

2. **Paper Recommendation:**
   - **Recommended:** Heavy white matte cardstock (**200 – 300 gsm**).
   - **Surface Finish:** **Matte or uncoated only**.
   - **Avoid:** Glossy photo paper, semi-gloss, or laminated sheets. Glossy finishes produce specular reflections under overhead lights that will trigger the Adaptive Capture Guard glare rejection gate (`glare_ratio > 5%`).

3. **Cutting & Boundary Rules:**
   - Cut along the 4 corner crop marks.
   - **CRITICAL:** The continuous black perimeter border (thickness: 4 px / 1.0 mm) and 4 corner alignment markers **must remain fully intact and visible**. The contour detection and perspective rectification algorithm uses this outer boundary to detect corners and compute the homography matrix.

---

## 4. Optical Acquisition & Camera Guidance

1. **Which Side Faces the Camera:**
   - Place the card face-up on a flat, neutral, matte horizontal surface (e.g., tabletop or bench).
   - All color patches, reaction wells, and corner markers must directly face the camera lens.

2. **Camera Distance & Framing:**
   - Maintain a distance of **20 cm to 35 cm** (8 to 14 inches) between the mobile/webcam lens and the card.
   - Ensure the card occupies **40% to 80%** of the live preview frame.

3. **Plane & Skew Alignment:**
   - Hold the camera plane-parallel to the card surface (looking straight down).
   - The card detection algorithm tolerates minor perspective distortion, but excessive skew exceeding **20.0°** will be flagged by the Adaptive Capture Guard.

4. **Lighting Protocol:**
   - Use uniform, diffuse white illumination (indirect daylight, diffuse soft-white LED, or overhead room lighting).
   - Avoid direct point-source flashlights or direct camera flash over the reaction wells.

---

## 5. Automated Pipeline Validation Results

The generated high-resolution card was verified through the backend scientific test pipeline:

- **Image Ingest:** 2400 × 1600 px (SHA-256: `e1a57abb4142684e...`)
- **Card Detection:** `Detected = True`, `Confidence = 1.00`, `Aspect Ratio = 1.52`, `Skew = 0.0°`
- **Adaptive Capture Guard Quality Gates:**
  - **Blur Variance:** `3878.7` (Threshold $\ge 120.0$) $\rightarrow$ **PASS (SHARP)**
  - **Specular Glare:** `0.0%` (Threshold $\le 5.0\%$) $\rightarrow$ **PASS (NO GLARE)**
  - **Calibration Residual:** `0.86 ΔE` (Threshold $\le 18.0\text{ ΔE}$) $\rightarrow$ **PASS (ACCURATE)**
- **Overall Quality Gating:** **`READY`**
- **Classification Status:** Successfully classified as **Presumptive Positive** on `well_1` ($\Delta E \le 12.0\text{ \Delta E}$).
