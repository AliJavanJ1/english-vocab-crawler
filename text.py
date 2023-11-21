import pandas as pd


def main():
    db = pd.read_csv('4000_short_long.csv')
    db2 = db.loc[:, ["Id"]]
    db2["Mixed Meaning"] = "<ul><li>" + db["Short Meaning"] + "</li><li>" + db["Long Meaning"] + "</li></ul>"
    db2.to_csv("4000_extra.csv", index=False)


if __name__ == '__main__':
    main()
