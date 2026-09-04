# Weather Impact on Coffee Yields

**Research Note** | Part of finding alpha in coffee as a commodity

## Summary

Coffee (especially Arabica) is one of the most weather-sensitive major agricultural commodities. Temperature extremes, frost, drought, and rainfall timing drive large yield swings that frequently move global prices. Understanding these relationships is core to generating alpha.

---

## 1. Optimal Climate Requirements

| Factor              | Arabica (*C. arabica*)          | Robusta (*C. canephora*)       |
|---------------------|---------------------------------|--------------------------------|
| Optimal mean temp   | 18–22/23 °C                    | 22–26/28 °C                   |
| Frost tolerance     | Very low (damage near 0 °C)    | Very low                      |
| Heat sensitivity    | High                           | Moderate (more tolerant)      |
| Drought sensitivity | High                           | High (often understated)      |
| Annual rainfall     | ~1,200–1,800/2,000 mm          | Similar or higher             |

- Arabica prefers higher altitudes and cooler conditions → more vulnerable to warming.
- Robusta is more heat-tolerant but still highly sensitive to prolonged dry periods. Recent research calls the idea of Robusta as a climate “savior” an oversimplification.

---

## 2. Key Weather Risks & Yield Effects

### Frost
- Extremely damaging, especially in southern Brazil (Minas Gerais, São Paulo, Paraná).
- Can kill trees or severely damage them → multi-year production impact.
- Famous events: 1975 “black frost”, 2021 frost (after drought).

### Drought / High Vapour Pressure Deficit (VPD)
- One of the strongest yield reducers.
- Critical stages: flowering and bean filling.
- Extreme dry years can cut yields 50–80% in rain-fed areas.
- Vietnam (Robusta) and Brazil frequently affected.

### Excessive Heat
- Accelerates ripening → smaller beans, lower quality.
- Can cause flower abortion.
- Growing number of “coffee-harming heat” days already observed due to climate change (extra 50–70 days/year in top producers).

### Rainfall Timing & Extremes
- Coffee needs a dry period to trigger flowering, followed by rain for fruit set.
- Rain on flowering day reduces pollination.
- Excess rain during harvest lowers quality (mold, delayed drying).
- La Niña often brings excess rain to Colombia → yield drops.

### Compound Events (ENSO-driven)
- El Niño typically → warmer + drier conditions in many coffee belts.
- Simultaneous hazards across major producers (Brazil + Vietnam + Colombia) create the biggest supply shocks and price spikes.

---

## 3. Climate Change Outlook

- Suitable land for Arabica projected to shrink significantly (studies often cite ~50% reduction by 2050 under higher warming scenarios).
- Yield declines of 15–35% projected in major Latin American and African regions by mid-to-late century (depending on scenario and model).
- Impacts are highly local: some higher-altitude or currently cooler areas may temporarily benefit, while current heartlands (e.g. Minas Gerais) face stronger pressure.
- Irrigation and agroforestry (shade) offer partial adaptation but have limits.

---

## 4. Historical Price-Relevant Events

- **2021 Brazil**: Severe drought followed by frost → major Arabica shortfall, strong price rally.
- **Recent years**: Repeated drought/heat in Brazil + Vietnam, excess rain in Colombia → elevated volatility and multi-year price strength into 2024–2025.
- Production shortfalls in top suppliers quickly tighten global balances because coffee stocks are relatively low and demand is inelastic in the short term.

---

## 5. Data Sources for Quantitative Work

**Yields & Production**
- USDA Foreign Agricultural Service coffee reports
- ICO (International Coffee Organization)
- Brazilian IBGE / CONAB
- FAOSTAT

**Weather**
- ERA5 / ERA5-Land (temperature, precipitation, VPD)
- NOAA / NCEI Climate Data Online
- Berkeley Earth temperature
- GPCC precipitation
- NASA POWER

**Useful derived variables**
- Growing Degree Days (GDD)
- Harmful Degree Days / extreme heat days
- Freezing Degree Days
- Consecutive dry days / drought indices
- Stage-specific precipitation (blooming, ripening, harvest)

---

## 6. Alpha Implications

Weather is a primary driver of coffee supply shocks. Key research directions for this repo:

1. Build stage-specific weather indices for Brazil (Arabica), Vietnam (Robusta), and Colombia.
2. Quantify historical yield response elasticities to temperature, precipitation, and VPD anomalies.
3. Test leading indicators (seasonal forecasts, soil moisture, ENSO state) for price prediction.
4. Monitor real-time weather anomalies vs. market-implied production expectations.

---

*Last updated: September 2026*
