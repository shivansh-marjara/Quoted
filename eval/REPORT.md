# Desharnais backtest

Dataset: PROMISE Desharnais software cost estimation, 81 projects.
Dropped 4 incomplete projects (38, 44, 66, 75) as in Shepperd & Schofield 1997, leaving 77 cases.
Split: rolling origin by `YearEnd`. Train on earlier years, test on the next year.
Folds with fewer than 15 train or 3 test rows are skipped.
Target: `Effort` (person-hours). Features: TeamExp, ManagerExp, Length, Transactions, Entities, PointsAjust, Language.

PRED(25) is the fraction of predictions within 25% of actual effort, the usual number in this literature.

## Results

| Model | MAE (hours) | MdAE (hours) | PRED(25) | n |
| --- | ---: | ---: | ---: | ---: |
| mean | 3114.6 | 2714.1 | 0.152 | 46 |
| linear | 2013.5 | 1304.3 | 0.348 | 46 |
| analog | 1972.4 | 1361.5 | 0.261 | 46 |
| tabpfn-3.5 | 1618.4 | 1058.3 | 0.413 | 46 |

## Folds

- Year 1986: train 31, test 27, mean MAE 2981, linear MAE 1991, analog MAE 1943, TabPFN MAE 1554
- Year 1987: train 58, test 14, mean MAE 3397, linear MAE 2422, analog MAE 2378, TabPFN MAE 1930
- Year 1988: train 72, test 5, mean MAE 3046, linear MAE 988, analog MAE 997, TabPFN MAE 1096

## How to read this

The mean baseline quotes the same hours for every project. Linear regression is what a careful freelancer with a spreadsheet would do.
Analog is 3-nearest-neighbour on standardized features, the method Shepperd used on this same table.

Lowest MAE on this split: **tabpfn-3.5** (1618.4). Highest MAE: **mean** (3114.6).
TabPFN beat the mean baseline on MAE (1618.4 vs 3114.6) and posted PRED(25)=0.413.

## Source

Original: J. M. Desharnais, Universite de Montreal, 1989. PROMISE ARFF via Martin Shepperd.
File vendored at `eval/desharnais.csv`.

