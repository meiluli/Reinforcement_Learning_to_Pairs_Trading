import pandas as pd
import statsmodels.tsa.stattools as ts
import statsmodels.api as sm

def ols_reg():
    ols = pd.read_excel('ols.xlsx')
    ols['const'] = 1
    model = sm.OLS(ols['Close1'], ols[['Close2', 'const']])
    results = model.fit()
    print(results.summary())
    return results.params

def adf_test(params):
    ols = pd.read_excel('ols.xlsx')
    ols['const'] = 1
    spread = ols['Close1'] - params[0]*ols['Close2'] + params[1]
    spread = spread.iloc[::-1]
    spread.reset_index(drop = True, inplace = True)
    spread.plot()
    adf = ts.adfuller(spread, maxlag = 1, regression = "ctt")
    print("Augmented-Dickey-Fuller Test Results")
    print("====================================")
    print("ADF Test Statistic        ", round(adf[0], 6))
    print("P-Value                    ", round(adf[1], 6))
    print("# Lags Used                       ", round(adf[2], 0))
    print("# Observations Used            ", round(adf[3], 0))
    print("Critical Value (1%)       ", round(adf[4]["1%"], 6))
    print("Critical Value (5%)       ", round(adf[4]["5%"], 6))
    print("Critical Value (10%)      ", round(adf[4]["10%"], 6))
    print("dtype: float64")
    return None