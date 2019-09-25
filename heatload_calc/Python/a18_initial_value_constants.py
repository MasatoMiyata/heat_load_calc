from Psychrometrics import xtrh

"""
付録18．初期値と定数
"""


# ********** 表8 各種変数の初期値 **********


def get_Tr_initial() -> float:
    return 15.0


def get_TsdA_initial() -> float:
    return 0.0


def get_TsdT_initial() -> float:
    # TODO: 仕様書は15.0になっているが、実装は0.0相当だった
    return 0.0


def get_Teo_initial() -> float:
    return 15.0


def get_q_initial() -> float:
    return 0.0


def get_Tfun_initial() -> float:
    return 15.0


def get_xr_initial() -> float:
    # return 0.00579618
    return xtrh(20.0, 40.0)


def get_xf_initial() -> float:
    # return 0.00579618
    return xtrh(20.0, 40.0)


# ********** 表9 各種定数値 **********

# 空気の比熱[J/kg K]
def get_ca() -> float:
    return 1005.0


# 空気の密度[kg/m3]
def get_rhoa() -> float:
    return 1.2


# 蒸発潜熱[J/kg]
def get_conra() -> float:
    return 2501000.0


# 大気圧[kPa]
def get_P() -> float:
    return 101.325


# ステファンボルツマン定数
def get_Sgm() -> float:
    return 5.67e-8


def get_l_wtr() -> float:
    """
    Returns:
         水の蒸発潜熱, J/kg
    """
    return 2501000.0


def get_delta_t():
    return 900


# TODO: 仕様書では固定値で記述されているが、
# 実際には JSONファイル内の`outside_solar_absorption`を使用している
# def get_as():
#    return 0.8


def get_RhoG():
    return 0.1


def get_eps():
    return 0.9