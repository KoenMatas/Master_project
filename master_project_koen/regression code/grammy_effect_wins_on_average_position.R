#loading necessary library
library(tidyverse)
library(readxl)
library(car)

#loading data 
grammybillboardmerge <- read_excel("C:/Users/koenm/OneDrive/Bureaublad/Thesis/Metacritic_thesis/grammy/output/finalmerge/grammybillboardmerge.xlsx")
View(grammybillboardmerge)

#check datatype columns
str(grammybillboardmerge)

#change columns to numeric
grammybillboardmerge$Median_position <- as.numeric(grammybillboardmerge$Median_position)
grammybillboardmerge$wins <- as.numeric(grammybillboardmerge$wins)
grammybillboardmerge$total_previous_wins <- as.numeric(grammybillboardmerge$total_previous_wins)
grammybillboardmerge$nominated <- as.numeric(grammybillboardmerge$nominated)

#check effect grammy win on median position
median <- lm(grammybillboardmerge$Median_position
           ~ grammybillboardmerge$wins 
           + grammybillboardmerge$total_previous_wins 
           + grammybillboardmerge$nominated, data = grammybillboardmerge)

summary(median)

#check model
vif(median)

#check effect grammy win on min-peak
peak <- lm(grammybillboardmerge$Min_peak
             ~ grammybillboardmerge$wins 
             + grammybillboardmerge$total_previous_wins 
             + grammybillboardmerge$nominated, data = grammybillboardmerge)
summary(peak)

#vif peak
vif(peak)

#check effect grammy win on weeks on chart
week <- lm(grammybillboardmerge$Max_weeks_on_chart
             ~ grammybillboardmerge$wins 
             + grammybillboardmerge$total_previous_wins
             + grammybillboardmerge$nominated, data = grammybillboardmerge)
summary(week)

#check vif
vif(week)
