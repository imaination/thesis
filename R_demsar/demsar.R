#install.packages("PMCMRplus")
#install.packages("readxl")
library(PMCMRplus)
library("readxl")

# xlsx files
position_df <- read_excel("~/Downloads/results_demsar.xlsx", sheet = "position")
swing_df <- read_excel("~/Downloads/results_demsar.xlsx", sheet = "swing")
scalp_df <- read_excel("~/Downloads/results_demsar.xlsx", sheet = "scalp")

position <- array(data = unlist(position_df),
                  dim = c(6, 11),
                  dimnames = list(1:6, colnames(position_df)))

swing <- array(data = unlist(swing_df),
                  dim = c(6, 11),
                  dimnames = list(1:6, colnames(swing_df)))

scalp <- array(data = unlist(scalp_df),
                  dim = c(6, 11),
                  dimnames = list(1:6, colnames(scalp_df)))

## Demsar's many-one test
summary(frdManyOneDemsarTest(y=position, p.adjust = "bonferroni"))
summary(frdManyOneDemsarTest(y=swing, p.adjust = "bonferroni"))
summary(frdManyOneDemsarTest(y=scalp, p.adjust = "bonferroni"))
