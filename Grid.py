import pandas as pd
import matplotlib.pyplot as plt
# This is the rounding number 
ROUND_NUM = 4

# setup your own trading strategy here, all numbers here are percentage except the laverage ratio
STOP_LOSS = 0.4
STOP_PROF = 1.6
COMMISSION = 0.06
LEVER_RATIO = 1
cur = "1000SHIBUSDT"

# which row of the data do you want to start and end, since our data are min-klines, their unit is minutes
START = 0
END = 1440*30*5


if __name__ == "__main__":    
    df = pd.read_csv("data/{}.csv".format(cur))
    c = START
    holding_price = 0
    side = 1 # strat with buy, 1 for buy and 0 for sell
    record = []

    while c < END:
        record.append(-1)
        today = df.iloc[c]
        if holding_price == 0:
            holding_price = today["Open"]
        
        if side == 1:
            if today["Low"] < holding_price * (100 - STOP_LOSS) / 100:
                side = 0
                record[-1] = 0
                holding_price = holding_price * (100 - STOP_LOSS) / 100

            elif today["High"] > holding_price * (100 + STOP_PROF) / 100:
                side = 0
                record[-1] = 1
                holding_price = holding_price * (100 + STOP_PROF) / 100
        
        elif side == 0:
            if today["High"] > holding_price * (100 + STOP_LOSS) / 100:
                side = 1
                record[-1] = 0
                holding_price = holding_price * (100 + STOP_LOSS) / 100
            elif today["Low"] < holding_price * (100 - STOP_PROF) / 100:
                side = 1
                record[-1] = 1
                side = 1
                holding_price = holding_price * (100 - STOP_PROF) / 100             

        c += 1

    # win and lose count
    w = record.count(1) 
    l = record.count(0)

    exp_value = LEVER_RATIO*(w*(STOP_PROF-COMMISSION) - l* (STOP_LOSS +COMMISSION)) / (w+l)

    print("USE {}".format(cur))
    print("stop prof = {}\nstop loss = {}\nleverage ratio = {}".format(STOP_PROF, STOP_LOSS, LEVER_RATIO))
    print("\n===============result===============\n")
    win_rate = w / (w+l)
    actual_odd = (STOP_PROF-COMMISSION) / (STOP_LOSS + COMMISSION)
    kelly_rate = ((actual_odd+1) *  win_rate  - 1 ) / actual_odd
    print("exp with comission = {}".format(round(exp_value,ROUND_NUM)))
    print("win rate = {},  actual odd = {}".format(round(win_rate,ROUND_NUM),round(actual_odd,ROUND_NUM)))
    print("kelly rate = {}".format(round(kelly_rate,ROUND_NUM)))
    if kelly_rate < 0:
        print("This game rule will give negative expectation")
    else:
        t_re = []
        now_asset = 1
        for r in range(1,len(record)):
            if record[r] == 1:
                now_asset += now_asset * kelly_rate * (STOP_PROF-COMMISSION) * 0.01 * LEVER_RATIO
            elif record[r] == 0:
                now_asset -= now_asset * kelly_rate * (STOP_LOSS +COMMISSION) * 0.01 * LEVER_RATIO
            t_re.append(now_asset)

        print("Final asset {}".format(round(now_asset,ROUND_NUM)))
        min_id = t_re.index(min(t_re))
        max_id = t_re.index(max(t_re))
        plt.plot(t_re)
        plt.annotate("{}".format(round(min(t_re),2)),(min_id,min(t_re)))
        plt.annotate("{}".format(round(max(t_re),2)),(max_id,max(t_re)))
        plt.title("symbol: {}\nstop lose: {}, stop prof: {}, leverage : {}".format(cur, STOP_LOSS, STOP_PROF, LEVER_RATIO))
        plt.show()

    print("\n================End=================\n")

