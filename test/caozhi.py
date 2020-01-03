import pandas as pd

df = pd.DataFrame({"a":[1,2,3],"b":[1,4,3]})

df1 = df[["a", "b"]]
df1 = df1.rename(columns={"a":"b","b":"a"})
print(df1)