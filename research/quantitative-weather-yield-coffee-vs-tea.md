# Quantitative Weather–Yield Relationships: Coffee vs Tea + Quality Effects

**Research Note** | Comparative climate risk analysis for commodity alpha

## 1. Quantitative Yield Sensitivities

### Coffee (primarily Arabica, Brazil focus)

| Variable | Stage / Context | Approximate Effect | Source type |
|----------|-----------------|--------------------|-------------|
| Growing Degree Days (GDD) | Blooming | Elasticity ≈ +0.27 | Econometric (Brazil municipalities) |
| Harmful Degree Days (HDD) | Blooming | Elasticity ≈ −0.06 | Same |
| Extreme heat (> ~33–35 °C) | General | Sharp negative; “killing degree days” strongly reduce log yields | Brazil panel studies |
| Precipitation | Flowering & fruit-bearing | +0.5% yield per 10% more rain | Brazil |
| Precipitation | Harvest | Negative | Brazil |
| Monthly temp > 26.6 °C | Assam-like conditions | −3.8% yield per +1 °C | India studies |
| Frost / freezing days | Dormant / winter | Multi-year damage; tree mortality | Historical Brazil events |

- Nonlinear response is critical: beneficial warming up to a threshold, then rapid damage above ~33–35 °C.
- Stage-specific effects matter more than annual averages.

### Tea

| Variable | Context | Approximate Effect | Source type |
|----------|---------|--------------------|-------------|
| Monthly temperature > 26.6 °C | Assam, India | −3.8% yield per +1 °C at higher baselines | Duncan et al. type studies |
| Extreme cold days (0–4 °C) | China | −2% to −4% yield per such day | China extreme-temperature study |
| Extreme heat days (~34–36 °C) | China | ≈ −3.7% yield per day | Same |
| Heat + water stress | Kenya | Mid-century yield decline estimates ~5–10% (range −15% to +1% depending on soil moisture) | Satellite + model studies |
| Rainfall reduction | Sri Lanka examples | 100 mm less monthly rain → 30–80 kg/ha/month lower made tea | Earlier Sri Lankan work |

- Tea also shows strong sensitivity once temperatures exceed regional optima.
- Continuous flush harvesting means weather impacts are more frequent/seasonal than coffee’s single main crop cycle.

### Side-by-side Summary

| Aspect | Coffee (Arabica) | Tea |
|--------|------------------|-----|
| Critical high-temp threshold | ~33–35 °C (sharp damage) | ~26–28 °C already negative in many regions; extreme heat >34 °C costly |
| Cold / frost | Extremely damaging (Brazil) | Damaging but secondary in many current zones |
| Precipitation elasticity | Positive in key growth stages, negative at harvest | Generally positive but timing-critical; drought interacts with heat |
| Nonlinearity | Strong | Strong |
| Best quantitative evidence | Brazil municipality panels, stage-specific GDD/HDD | Assam, China extreme-day studies, Kenya satellite work |

Both crops exhibit clear nonlinear temperature responses. Coffee has richer stage-specific econometric evidence (especially Brazil); tea has good extreme-day and regional suitability studies.

---

## 2. Quality Effects

### Coffee Quality
- Higher altitude / cooler temperatures during maturation → slower ripening → denser beans, better sensory scores (acidity, aroma, complexity).
- Excess heat accelerates ripening → smaller beans, lower cup scores, more bitter/earthy notes.
- Water stress and light exposure also influence secondary metabolites (chlorogenic acids, sugars, volatiles).
- Consistent finding: increased altitude associated with improved sensory attributes; excess light often reduces them.

### Tea Quality
- Temperature strongly modulates key compounds:
  - **Theanine** (umami / sweetness): often peaks around cooler conditions (~20 °C in controlled studies).
  - **Catechins / EGCG** (astringency, health compounds): responses vary; high temperature can reduce some desirable catechins or shift ratios.
  - **Caffeine**: frequently increases with higher temperature.
- Higher altitude / cooler conditions generally improve the polyphenol-to-amino-acid ratio that drives preferred green-tea taste.
- Rising temperatures tend to reduce theanine and some aroma compounds while increasing bitterness/astringency potential → quality deterioration for premium grades.
- Seasonality and drought also shift phenolic profiles (sometimes increasing certain compounds under mild stress).

**Implication**: Climate change can reduce *both* volume and quality premiums. For specialty coffee and high-grade teas, quality loss may matter as much as (or more than) pure yield loss for price formation.

---

## 3. Key Regional Deep Dives

### Kenya (Tea)
- Highly exposed. Optimal suitability projected to decline significantly (one major modelling study ~26% loss of optimal zones by 2050).
- Yield driven by soil moisture + temperature interactions. Heat alone points to ~10% mid-century decline; concurrent soil-moisture changes can partially offset or worsen it.
- Smallholder-dominated → limited adaptation capacity in the short run.

### Assam / Northeast India (Tea)
- Already seeing higher maximum temperatures.
- Clear yield penalty above ~26.6 °C monthly average.
- Erratic rainfall and declining relative humidity add stress.
- Quality (especially for orthodox and premium teas) at risk from warmer, less stable conditions.

### China (Tea)
- Largest producer. Currently more limited by cold extremes in northern zones.
- Warming reduces cold damage but introduces new heat-stress losses (projected 11–26% heat-induced yield reductions in key provinces under 1.5–2 °C pathways).
- Quality shifts (theanine ↓, caffeine ↑, catechin profile changes) likely as important as volume for domestic premium markets.

### Brazil (Coffee – for comparison)
- Stage-specific weather (blooming GDD positive, HDD negative; rainfall timing critical) dominates inter-annual yield variation.
- Extreme heat and frost remain the highest-impact tail risks for global balances.

---

## 4. Alpha-Relevant Takeaways

1. **Nonlinear thresholds** are more important than average temperature trends. Monitoring extreme-heat days and stage-specific weather in Brazil (coffee) and Assam/Kenya (tea) offers higher signal value.
2. **Quality channels** can amplify price moves in specialty segments even when bulk production is only moderately affected.
3. **Cross-crop monitoring**: Simultaneous heat/drought stress in Brazil coffee + Kenya/Assam tea would represent a broader beverage-crop climate shock.
4. Best next quantitative steps for this repo:
   - Build comparable extreme-heat-day and soil-moisture indices for key coffee and tea regions.
   - Estimate simple yield response functions using public yield + ERA5 data.
   - Test whether weather anomalies improve short-term price forecast models beyond standard supply/stock variables.

---

*Last updated: September 2026*
