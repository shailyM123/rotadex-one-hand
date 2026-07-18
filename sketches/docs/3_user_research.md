# User Research & Ergonomic Analysis

## 1. Ergonomic Principles & Human Factors

### Pinch Grip vs. Palm Press
Research on arthritis and post-stroke recovery shows that fine motor movements (such as the tip pinch, pad pinch, or lateral pinch) are the first to degrade and cause the most pain. 
- **Pinch Force limits**: Elderly individuals with osteoarthritis often have pinch strengths below $15\text{ N}$ (approx. $1.5\text{ kgf}$), and opening snap-lids can require forces exceeding $20\text{ N}$.
- **Palm/Fist Press**: In contrast, large-muscle groups and gross motor movements (such as pushing down with the palm of the hand, the side of the hand, or the forearm/elbow) remain highly functional. The palm press allows the user to leverage their body weight and arm strength, accommodating forces up to $50\text{ N}$ with ease and minimal joint strain.

### Actuation Force Design Goal
For the **Rotadex**, our target actuation force for the central button is **$8\text{ N}$ to $12\text{ N}$** (approx. $0.8\text{ to }1.2\text{ kgf}$). This is low enough for frail users but high enough to prevent accidental activation from accidental bumps.

---

## 2. Dimensional Sizing & Volumetric Capacity

### Pill Size Calibration
To ensure the organizer is truly useful, it must accommodate a wide variety of medication sizes and shapes. We surveyed common pill dimensions:
- **Standard Round Aspirin**: $\varnothing 8\text{ mm} \times 3\text{ mm}$ thick.
- **Large Capsule (Size 000)**: $26.1\text{ mm}$ length $\times \varnothing 9.9\text{ mm}$.
- **Typical Softgel Multivitamin**: $25\text{ mm}$ length $\times 15\text{ mm}$ width $\times 10\text{ mm}$ thick.

```
       ┌─────────────────── 26.1 mm ───────────────────┐
       ├───────────────────────────────────────────────┤ 9.9 mm
       └───────────────────────────────────────────────┘
                     (Size 000 Capsule)
```

### Compartment Sizing
Each of the 7 pie-shaped compartments in the Rotadex carousel is designed with the following dimensions:
- **Inner Radius ($R_i$):** $15\text{ mm}$
- **Outer Radius ($R_o$):** $55\text{ mm}$
- **Depth ($H$):** $30\text{ mm}$
- **Angular Width:** $360^\circ / 7 \approx 51.4^\circ$
- **Calculated Volume ($V$):**
  \[
  V = \frac{1}{7} \times \pi \times (R_o^2 - R_i^2) \times H \approx \frac{1}{7} \times 3.1416 \times (3025 - 225) \times 30 \approx 37,600\text{ mm}^3 \approx 37.6\text{ mL}
  \]
This volume is highly generous and can easily fit up to **8–10 large capsules** or capsules mixed with tablets, ensuring it meets the capacity requirements of heavy medication schedules.

---

## 3. Stability and Friction Calculations

To prevent the device from sliding during one-handed button presses, the frictional force between the base of the device and the tabletop must exceed the horizontal force component generated during use.

```
             F_actuation (Downwards, e.g., 10 N)
                    │
                    ▼
          ┌───────────────────┐
          │      Rotadex      │ ───> F_sliding (due to off-center press)
          ├───────────────────┤
          └───────────────────┘
         ======================= (Tabletop)
             ▲             ▲
             │             │
             F_friction = μ * (M_device * g + F_actuation)
```

### Friction Model:
- **Weight of empty device ($M_{device}$):** $300\text{ g} = 0.3\text{ kg}$ (weighted with steel weights in the base).
- **Frictional Coefficient ($\mu$):** For high-friction silicone rubber on a smooth kitchen counter (laminate/glass/granite), $\mu \approx 0.8$.
- **Normal Force ($F_N$):** $F_N = M_{device} \cdot g + F_{actuation} \approx (0.3 \cdot 9.81) + 10 = 12.94\text{ N}$.
- **Resisting Friction Force ($F_{friction}$):**
  \[
  F_{friction} = \mu \cdot F_N = 0.8 \times 12.94\text{ N} \approx 10.35\text{ N}
  \]
Because the vertical force of the press increases the normal force, the grip increases dynamically during actuation! An actuation force of $10\text{ N}$ directed slightly sideways (up to $10.35\text{ N}$ lateral force) will not slide the device.

---

## 4. Materials and Sanitization

### Part Breakdown and Material Selection:
1. **Outer Shell & Button:** **ABS (Acrylonitrile Butadiene Styrene)**. High impact resistance, highly scratch-resistant, durable, and easily cleaned with isopropyl alcohol or soap.
2. **Internal Carousel:** **Food-Grade Polypropylene (PP)**. Highly chemical-resistant, hydrophobic, non-toxic, and certified for direct food/drug contact.
3. **Ratchet Mechanism (Internal Pawl & Gears):** **POM (Polyoxymethylene / Acetal)**. Extremely low friction, high wear resistance, and high dimensional stability to prevent the mechanical teeth from wearing out over years of clicks.
4. **Base Non-Slip Ring:** **TPU (Thermoplastic Polyurethane) or Silicone Rubber**. Provides high coefficient of friction ($\mu > 0.8$) against surfaces.
