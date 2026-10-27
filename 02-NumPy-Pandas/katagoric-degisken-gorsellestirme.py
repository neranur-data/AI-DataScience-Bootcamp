import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
pd.set_option("display.width", 500)
pd.set_option("display.max_columns", None)
df = sns.load_dataset("titanic")
df.head()

#df["sex"].value_counts().plot(kind="bar")
#plt.show()

#plt.hist(df["age"])
#plt.show()

plt.boxplot(df["fare"])
plt.show()