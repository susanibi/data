#testing interaction significance using two-way Hardcoded dataset (grouped by cell conc).
# Calculates Surfactant Index and Runs a two-way ANOVA with interaction

import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols

# Hardcoded dataset
data = {
    "Cell Conc": [
        "≤40", "≤40", "≤40", "≤40", "≤40", 200, 200, 200, 200, 200, 200,
        300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 400, 400
    ],
    "F68 (%)": [
        0.02, 0.02, 0.05, 0.05, 0.05, 0.01, 0.01, 0.02, 0.02, 0.03, 0.04,
        0.00, 0.00, 0.00, 0.00, 0.01, 0.01, 0.05, 0.05, 0.05, 0.05, 0.01, 0.02
    ],
    "RG (%)": [
        0.00, 0.05, 0.15, 0.00, 0.00, 0.00, 0.00, 0.00, 0.01, 0.00, 0.00,
        0.00, 0.00, 0.00, 0.05, 0.00, 0.05, 0.00, 0.00, 0.00, 0.00, 0.00, 0.01
    ],
    "Split Eff": [
        97.27, 96.88, 100, 100, 98.44, 0, 9.38, 1.56, 65.23, 9.38, 50,
        0, 0, 0, 10.94, 5, 100, 90.63, 78.13, 93.36, 98.44, 53.13, 64.00
    ]
}

# Load and process
df = pd.DataFrame(data)
df["Surfactant Index"] = 2 * df["F68 (%)"] + df["RG (%)"]

# Fit two-way ANOVA with interaction
model = ols("Q('Split Eff') ~ Q('Cell Conc') * Q('Surfactant Index')", data=df).fit()
anova_table = sm.stats.anova_lm(model, typ=2)

# Output result
print("\nTwo-Way ANOVA: Cell Conc × Surfactant Index")
print(anova_table.round(4))
