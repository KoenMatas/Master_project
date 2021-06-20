#loading necessary library
library(tidyverse)
library(readxl)
library(car)

#loading data 
finalexcel <- read_excel("C:/Users/koenm/OneDrive/Bureaublad/Thesis/Metacritic_thesis/5. files_to_merge/output/finalexcel.xlsx")
View(finalexcel)

#check datatype columns
str(finalexcel)

#change user_score and total_previous_nominations to numeric
finalexcel$User_Score <- as.numeric(finalexcel$User_Score)

#change NA's to 0
finalexcel$User_Score[is.na(finalexcel$User_Score)] <- 0 

cleandata <- finalexcel

#run regression on weeks_on_chart
mlml <- lm(cleandata$weeks_on_chart 
           ~ cleandata$Meta_Score 
           + cleandata$User_Score 
           + cleandata$critic_volume 
           + cleandata$critic_sentiment_score 
           + cleandata$Sum_critic_topic1_album
           + cleandata$Sum_critic_topic2_music
           + cleandata$Sum_critic_topic3_individualtracks
           + cleandata$user_volume
           + cleandata$user_sentiment_score
           + cleandata$user_spoiler
           + cleandata$user_album
           + cleandata$user_individualtracks
           + cleandata$wins
           + cleandata$total_previous_wins
           + cleandata$nominated, data = cleandata)

summary(mlml)

#run vif to multicollinearity 
vif(mlml)

#Start to transform the high VIF variables
#loading needed packages
library(ggpubr)
library(moments)

#plotting density distribution to check for skewness
ggdensity(cleandata, x = "Sum_critic_topic1_album", fill = "lightgray", title = "critic_topic1") +
  stat_overlay_normal_density(color = "red", linetype = "dashed")

ggdensity(cleandata, x = "Sum_critic_topic2_music", fill = "lightgray", title = "critic_topic2") +
  stat_overlay_normal_density(color = "red", linetype = "dashed")

ggdensity(cleandata, x = "Sum_critic_topic3_individualtracks", fill = "lightgray", title = "critic_topic3") +
  stat_overlay_normal_density(color = "red", linetype = "dashed")

ggdensity(cleandata, x = "user_spoiler", fill = "lightgray", title = "topic1") +
  scale_x_continuous(limits = c(-1, 1)) +
  stat_overlay_normal_density(color = "red", linetype = "dashed")

ggdensity(cleandata, x = "user_album", fill = "lightgray", title = "topic2") +
  scale_x_continuous(limits = c(-1, 1)) +
  stat_overlay_normal_density(color = "red", linetype = "dashed")

ggdensity(cleandata, x = "user_individualtracks", fill = "lightgray", title = "topic3") +
  scale_x_continuous(limits = c(-1, 1)) +
  stat_overlay_normal_density(color = "red", linetype = "dashed")

#Compute skewness critic topic 1 (result is 1.4391):
skewness(cleandata$Sum_critic_topic1_album, na.rm = TRUE)

#Compute skewness critic topic 2 (result is 1.423412):
skewness(cleandata$Sum_critic_topic2_music, na.rm = TRUE)

#Compute skewness critic topic 3 (result is 1.418963):
skewness(cleandata$Sum_critic_topic3_individualtracks, na.rm = TRUE)

#Compute skewness user topic 1 (result is 33.58409:
skewness(cleandata$user_spoiler, na.rm = TRUE)

#Compute skewness user topic 2 (result is 30.70093):
skewness(cleandata$user_album, na.rm = TRUE)

#Compute skewness user topic 3 (result is 30.0027):
skewness(cleandata$user_individualtracks, na.rm = TRUE)

#Log transformation of the skewed data  (all are positively skewed):
cleandata$Sum_critic_topic1_album <- log10(cleandata$Sum_critic_topic1_album)
cleandata$Sum_critic_topic2_music <- log10(cleandata$Sum_critic_topic2_music)
cleandata$Sum_critic_topic3_individualtracks <- log10(cleandata$Sum_critic_topic3_individualtracks)

cleandata$user_spoiler <- log10(cleandata$user_spoiler)
cleandata$user_album <- log10(cleandata$user_album)
cleandata$user_individualtracks <- log10(cleandata$user_individualtracks)

#check data
view(cleandata)

#check distribution again for skewness for each variable
ggdensity(cleandata, x = "Sum_critic_topic1_album", fill = "lightgray", title = "critic_topic1") +
  stat_overlay_normal_density(color = "red", linetype = "dashed")

ggdensity(cleandata, x = "Sum_critic_topic2_music", fill = "lightgray", title = "critic_topic2") +
  stat_overlay_normal_density(color = "red", linetype = "dashed")

ggdensity(cleandata, x = "Sum_critic_topic3_individualtracks", fill = "lightgray", title = "critic_topic3") +
  stat_overlay_normal_density(color = "red", linetype = "dashed")

ggdensity(cleandata, x = "user_spoiler", fill = "lightgray", title = "topic1") +
  stat_overlay_normal_density(color = "red", linetype = "dashed")

ggdensity(cleandata, x = "user_album", fill = "lightgray", title = "topic2") +
  stat_overlay_normal_density(color = "red", linetype = "dashed")

ggdensity(cleandata, x = "user_individualtracks", fill = "lightgray", title = "topic3") +
  stat_overlay_normal_density(color = "red", linetype = "dashed")

view(cleandata)

#combine critic topics into 1 variable by adding together
cleandata$critic_topic_combined <- cleandata$Sum_critic_topic1_album + cleandata$Sum_critic_topic2_music + cleandata$Sum_critic_topic3_individualtracks
view(cleandata$critic_topic_combined)

#combine user topics into 1 variable
cleandata$user_topic_combined <- cleandata$user_spoiler + cleandata$user_album + cleandata$user_individualtracks

#change infinte values to NA

is.na(cleandata$critic_topic_combined) <- sapply(cleandata$critic_topic_combined, is.infinite)
is.na(cleandata$user_topic_combined) <- sapply(cleandata$user_topic_combined, is.infinite)

str(cleandata)

#run new regression   
mlml <- lm(cleandata$weeks_on_chart 
           ~ cleandata$Meta_Score 
           + cleandata$User_Score 
           + cleandata$critic_volume 
           + cleandata$critic_sentiment_score 
           + cleandata$critic_topic_combined
           + cleandata$user_volume
           + cleandata$user_sentiment_score
           + cleandata$user_topic_combined
           + cleandata$wins
           + cleandata$total_previous_wins
           + cleandata$nominated, data = cleandata)

summary(mlml)

#run vif weeks on chart
vif(mlml)

#run regression on peak
peak <- lm(cleandata$peak 
           ~ cleandata$Meta_Score 
           + cleandata$User_Score 
           + cleandata$critic_volume 
           + cleandata$critic_sentiment_score 
           + cleandata$critic_topic_combined
           + cleandata$user_volume
           + cleandata$user_sentiment_score
           + cleandata$user_topic_combined
           + cleandata$wins
           + cleandata$total_previous_wins
           + cleandata$nominated, data = cleandata)

summary(peak)

#vif on peak
vif(peak)

#run regression on median position
position <- lm(cleandata$position
           ~ cleandata$Meta_Score 
           + cleandata$User_Score 
           + cleandata$critic_volume 
           + cleandata$critic_sentiment_score 
           + cleandata$critic_topic_combined
           + cleandata$user_volume
           + cleandata$user_sentiment_score
           + cleandata$user_topic_combined
           + cleandata$wins
           + cleandata$total_previous_wins
           + cleandata$nominated, data = cleandata)

summary(position)

#vif
vif(position)