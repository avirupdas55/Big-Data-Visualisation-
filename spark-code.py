# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 15:42:23 2021

@author: avirupdas
"""

# importing libraries

import pyspark
from pyspark.sql import SparkSession, Row
import pyspark.sql.types as T
import pyspark.sql.functions as F
from glob2 import glob

# Creating/Opening a Spark session- all csv files dumped in Data folder
files = glob('Data/*.csv')
spark= SparkSession.builder.appName('Big-data').getOrCreate()
print(spark)

#reading all csv files using Spark
# infer schema has been set to False, so all fields are imported as String
df=[spark.read.csv(fp,header=True,inferSchema=False,mode="DROPMALFORMED") for fp in files]

# creating blank dataframe in pyspark
params=['title', 'description', 'descriptionHTML', 'summary', 'summaryHTML',
           'installs', 'minInstalls', 'score', 'ratings', 'reviews', 'histogram',
           'price', 'free', 'currency', 'sale', 'saleTime', 'originalPrice',
           'saleText', 'offersIAP', 'inAppProductPrice', 'size', 'androidVersion',
           'androidVersionText', 'developer', 'developerId', 'developerEmail',
           'developerWebsite', 'developerAddress', 'privacyPolicy',
           'developerInternalID', 'genre', 'genreId', 'icon', 'headerImage',
           'screenshots', 'video', 'videoImage', 'contentRating',
           'contentRatingDescription', 'adSupported', 'containsAds', 'released',
           'updated', 'version', 'recentChanges', 'recentChangesHTML', 'comments',
           'editorsChoice', 'appId', 'url', 'category', 'Wi-Fi connection information', 'Other', 'Uncategorized',
           'Photos/Media/Files', 'Storage', 'Microphone', 'Device ID & call information',
           'Phone', 'Device & app history', 'Location', 'Camera', 'Contacts', 'Identity']
dat=spark.createDataFrame([tuple('' for i in params)], params).where('1=0')

# concatenating all available csv files in pyspark
for i in df:
    dat=dat.union(i)
    
# print the schema of the dataframe
print(dat.printSchema())

# Data-Processing

# dropping unnecessary columns 
drop_list=['category','summaryHTML','descriptionHTML','installs','recentChangesHTML',
           'comments','androidVersionText','icon','headerImage','screenshots','video',
          'videoImage','adSupported','updated','Uncategorized']
dat= dat.drop(*drop_list)

# dropping duplicate apps and null rows
dat= dat.drop_duplicates(['appId'])
dat= dat.na.drop(how='all')

# converting the size of all apps to KB
def size_clean(size):
    unit=size[-1]
    value=float(size[:-1])
    x=value
    if unit=='M':
        x=value*1024
    elif unit=='G':
        x=value*1024**2
    return str(x)

size_udf= F.UserDefinedFunction(size_clean,T.StringType())
dat=dat.withColumn('size_new',size_udf('size'))
dat=dat.drop('size').withColumnRenamed('size_new','size')

# setting the average for in-app product price
def avg_price(txt):
    txt=txt.replace('per item',"").replace('₹',"").replace(',',"")
    l=txt.split('-')
    if len(l)>1:
        return(str((float(l[0])+float(l[1]))/2))
    return(l[0])

dat= dat.na.fill(value='₹0 per item',subset='inAppProductPrice')
price_udf= F.UserDefinedFunction(avg_price,T.StringType())
dat=dat.withColumn('inAppProductPrice_new',price_udf('inAppProductPrice'))
dat=dat.drop('inAppProductPrice').withColumnRenamed('inAppProductPrice_new','inAppProductPrice')

# fixing the content rating column for proper usage
def rat_fix(txt):
    txt=txt.split()[2]
    return txt[:-1]

dat= dat.na.fill(value='Rated for 0+', subset='contentRating')
rat_udf=F.UserDefinedFunction(rat_fix,T.StringType())
dat= dat.withColumn('contentRating_new',rat_udf('contentRating'))
dat= dat.drop('contentRating').withColumnRenamed('contentRating_new','contentRating')

# handling missing values for different app permissions
def tf_enc(txt):
    if txt!='False':
        return 'True'
    return txt
tf_udf= F.UserDefinedFunction(tf_enc,T.StringType())

perm_list=['Wi-Fi connection information','Photos/Media/Files', 'Storage',
          'Microphone','Device ID & call information','Phone','Device & app history',
          'Location','Camera','Contacts','Identity']
for i in perm_list:
    dat= dat.na.fill(value='False',subset=i)
    dat=dat.withColumn(i+'_new',tf_udf(i))
    dat=dat.drop(i).withColumnRenamed(i+'_new',i)

# Generating output csv file

## writes multiple csv files
dat.write.csv('mycsv.csv')

## single csv file
dat.repartition(1).write.csv('output.csv',sep='|')

