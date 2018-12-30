import datetime

#空気の比熱
conca = 1005.0
#空気の密度
conrowa = 1.2

# 通日を計算
def get_nday(mo, day):
    """
    :param mo: 月
    :param day: 日
    :return: 1月1日からの通日
    """
    new_year = datetime.datetime(2017, 1, 1)
    that_day = datetime.datetime(2017, mo, day)
    ndays = that_day - new_year

    return (ndays.days + 1)

# # 汎用処理を行う関数群

# ## 当該日の通日を計算する関数
# - 日付（datetime型）を引数とし、1月1日から通して数えた日数（通日）を返す
#
# ### Function

# 当該日の通日を計算する
def Nday(dtmDate):
    new_year = datetime.date(dtmDate.year, 1, 1)
    that_day = datetime.date(dtmDate.year, dtmDate.month, dtmDate.day)
    ndays = (that_day - new_year).days + 1
    return ndays