# project: p7
# submitter: Smwells3
# partner: none
# hours: 13

import netaddr, copy
import pandas as pd
from pandas import Series
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, OneHotEncoder
from sklearn.compose import make_column_transformer

ips = pd.read_csv("data/ip2location.csv")

class UserPredictor():
    def fit(self, users, logs, ys):
        self.users = self.total_min_ips(users, logs)
        self.users = self.ip_to_country(self.users)
        self.merged = pd.merge(left=self.users, right=ys, left_on="id", right_on="id")
        self.pipeline = Pipeline([
    ("both", make_column_transformer((OneHotEncoder(), ["badge", "age", "country"]), 
                                     (PolynomialFeatures(degree=1, include_bias=False), ["past_purchase_amt", "total_min", "avg_minutes", "num_visited"]), remainder="passthrough")),
    ("lr", LogisticRegression(max_iter=1025))
])
        self.pipeline.fit(self.merged[["badge", "age", "country", "past_purchase_amt", "total_min", "avg_minutes", "num_visited"]], self.merged["y"])
    
    def predict(self, users, logs):
        self.users = self.total_min_ips(users, logs)
        self.users = self.ip_to_country(self.users)
        self.users["predicted"] = self.pipeline.predict(self.users[["badge", "age", "country", "past_purchase_amt", "total_min", "avg_minutes", "num_visited"]])
        return self.users["predicted"].values
    
    def total_min_ips(self, users, logs):
        avg = []
        num = []
        total = []
        net = []
        ids = list(users["id"].values)
        for id_ in ids: 
            test = logs[logs["id"] == id_]
            total.append(test["minutes_on_page"].sum())
            avg.append(test["minutes_on_page"].mean())
            num.append(len(test))
            try:
                net.append(int(netaddr.IPAddress(test["ip_address"].values[-1])))
            except:
                net.append(0)
        users["avg_minutes"] = avg
        users["total_min"] = total
        users["num_visited"] = num
        users["netaddr"] = net
        return users.fillna(0)
        
    def ip_to_country(self, df):
        df = df.sort_values("netaddr")
        countries = list()
        ip_idx = 0
        for ip in df["netaddr"]:
            for low in ips["low"][ip_idx:]:
                if low <= ip <= ips["high"][ip_idx]:
                    countries.append(ips["region"][ip_idx])
                    break
                else:
                    ip_idx += 1
        df["country"] = countries
        return df.sort_values("id")