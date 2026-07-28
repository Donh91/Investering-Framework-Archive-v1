# Global Liquidity Causal Chain, source and literature baseline v1

**Frozen:** 2026-07-28  
**Status:** SOURCE_QA_BASELINE / NO_ECONOMIC_RESULTS

## Verified public-source anchors

### Fiscal pressure

The Congressional Budget Office's 2026 to 2036 outlook projects a material increase in US federal net interest costs. The current official outlook describes net interest rising from approximately USD 1.0 trillion in 2026 to USD 2.1 trillion in 2036 and from approximately 3.3 percent of GDP to 4.6 percent.

Official sources:

- https://www.cbo.gov/publication/62105
- https://www.cbo.gov/publication/62050

Interpretation boundary:

This establishes a forecastable fiscal-pressure path. It does not establish automatic monetary accommodation or a three-year liquidity lead.

### Actual interest payments

The BEA/FRED series `A091RC1Q027SBEA` provides quarterly federal government current-expenditure interest payments and currently spans 1947 through 2026.

Official sources:

- https://fred.stlouisfed.org/series/A091RC1Q027SBEA
- https://fred.stlouisfed.org/data/A091RC1Q027SBEA

Required contract:

- preserve release date and vintage;
- do not treat a later revised observation as historically known;
- distinguish gross/current-expenditure interest from CBO net-interest projections.

### Treasury issuance and maturity structure

Treasury FiscalData exposes official debt, auction, issue-date and maturity-date information. Relevant official datasets include Treasury Securities Auctions Data, Monthly Statement of the Public Debt and Debt to the Penny.

Official sources:

- https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/
- https://fiscaldata.treasury.gov/datasets/monthly-statement-public-debt/
- https://fiscaldata.treasury.gov/datasets/debt-to-the-penny/

Interpretation boundary:

Outstanding debt and future interest costs do not determine the market's absorption capacity, issuance composition, TGA timing or policy response by themselves.

### BIS global liquidity

The Bank for International Settlements defines global liquidity as the ease of financing in global financial markets. Its Global Liquidity Indicators track credit to non-bank borrowers through bank loans and international debt securities, with emphasis on foreign-currency credit in US dollars, euros and Japanese yen to non-residents.

Official sources:

- https://data.bis.org/topics/GLI
- https://www.bis.org/statistics/dataportal/gli.htm
- https://data.bis.org/topics/GLI/tables-and-dashboards

Interpretation boundary:

BIS global liquidity is a credit and financing concept. It is not interchangeable with a central-bank-balance or global-M2 chart.

## Local byte-visible inputs

```yaml
fred_recent_backfill:
  file: FRED_MACRO_CORE_RECENT_BACKFILL_20260716T070839Z.zip
  sha256: e1184a8c5b34dd7aef8a3db747de9094cc4660e9f5f4a7f8bdf0f2b1a475339d
  role: ENGINEERING_FIXTURE_ONLY
  reason: recent backfill and reproduction assets are useful for contract tests but do not provide a complete multi-cycle owner history

btc_investing_pdf:
  file: Bitcoin Historical Data - Investing.com 2.pdf
  sha256: eba4f29d2c61b3e4cafcf01229b116abe76b15c2f576cf24c28f0b65a800b108
  role: SHADOW_PRICE_CHALLENGER_ONLY
  reason: long historical table, but not selected as point-in-time owner and carries vendor/export lineage limitations
```

## Current hard gaps

```text
Exact GMI liquidity formula and series
Exact method behind the 87 percent and 97 percent claims
Nasdaq machine-readable owner history
Archived CBO projection vintages
Complete Treasury maturity and issuance owner table
BIS GLI export with publication timestamps
Official global broad-money series with point-in-time FX
Official PBoC monthly history and publication calendar
ALFRED or official historical release vintages
Final Backtest Build master binary byte audit
```

## Initial source conclusion

The fiscal-pressure premise is source-backed. The claimed mapping from interest payments to realised liquidity and from realised liquidity to BTC or Nasdaq timing remains unverified and must pass the frozen causal-chain tests.
