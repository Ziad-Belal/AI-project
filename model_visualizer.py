from sklearn.cluster import KMeans
import pandas as pd

df = pd.read_csv("All_Players.csv")

# Pick columns for clustering
features = ['MP','Gls','Ast','xG','xA']  # Example
X = df[features]

kmeans = KMeans(n_clusters=4)
kmeans.fit(X)
labels = kmeans.labels_  # Which cluster each player belongs to
