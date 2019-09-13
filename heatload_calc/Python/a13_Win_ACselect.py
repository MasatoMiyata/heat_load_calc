from common import get_nday
import datetime
import Space
import numpy as np

"""
付録13．	窓の開閉と空調発停の切り替え
"""

# 当該時刻の窓開閉、空調発停を判定する
def mode_select(air_conditioning_demand: bool, prev_air_conditioning_mode: int, is_prev_window_open: bool, now_pmv: float) -> tuple:
    # 窓の開閉、空調の発停を決定する
    # 冷房開始PMV
    occu_cooling_pmv = 0.84
    # 暖房開始PMV
    occu_heating_pmv = -0.84
    # 窓を開放するときのPMV
    occu_window_open_pmv = 0.49
    # 窓を閉鎖するときのPMV
    occu_window_close_pmv = -0.49

    # 空調需要がない場合（窓閉鎖、空調停止）
    if air_conditioning_demand == False:
        is_now_window_open = False
        now_air_conditioning_mode = 0
    # 空調需要がある場合は、前の窓開閉状態で自然室温を計算
    else:
        # 前時刻が暖房の場合
        if prev_air_conditioning_mode > 0:
            is_now_window_open = is_prev_window_open
            now_air_conditioning_mode = prev_air_conditioning_mode
            # 冷房生起PMV以上の場合は冷房
            if now_pmv >= occu_cooling_pmv:
                is_now_window_open = False
                now_air_conditioning_mode = -1
            # 窓開放生起温度以上の場合は通風
            elif now_pmv >= occu_window_open_pmv:
                is_now_window_open = True
                now_air_conditioning_mode = 0
        # 前時刻が冷房の場合
        elif prev_air_conditioning_mode < 0:
            # 暖房生起PMV以上の場合は冷房
            if now_pmv >= occu_heating_pmv:
                is_now_window_open = False
                now_air_conditioning_mode = -1
            # 暖房生起PMV未満の場合は暖房
            else:
                is_now_window_open = False
                now_air_conditioning_mode = 1
        # 前の時刻が空調停止の場合
        else:
            # 冷房生起PMV以上の場合は冷房
            if now_pmv >= occu_cooling_pmv:
                is_now_window_open = False
                now_air_conditioning_mode = -1
            # 暖房生起PMV以下の場合は暖房
            elif now_pmv <= occu_heating_pmv:
                is_now_window_open = False
                now_air_conditioning_mode = 1
            # 空調は停止し、now_PMVが窓開放生起PMVをまたぐまでは前の状態を維持
            else:
                now_air_conditioning_mode = 0
                is_now_window_open = is_prev_window_open
                # 窓を開放する
                if is_prev_window_open == 0 and now_pmv >= occu_window_open_pmv:
                    is_now_window_open = True
                # 窓を閉鎖する
                elif is_prev_window_open == 1 and now_pmv <= occu_window_close_pmv:
                    is_now_window_open = False
    
    return (is_now_window_open, now_air_conditioning_mode)

# 最終の空調信号の計算（空調停止はこのルーチンに入らない）
def reset_SW(now_air_conditioning_mode: int, Lcs: float, Lr: float, isRadiantHeater: bool, Lrcap: float) -> int:
    temp = now_air_conditioning_mode

    # 「冷房時の暖房」、「暖房時の冷房」判定
    if float(now_air_conditioning_mode) * (Lcs + Lr) < 0.0:
        temp = 0
    # 放射暖房の過負荷状態
    elif isRadiantHeater and now_air_conditioning_mode == 1 and Lrcap > 0.0 \
            and Lr > Lrcap:
        temp = 3
    # 放射暖房の過負荷状態
    elif isRadiantHeater and now_air_conditioning_mode == 1 and Lrcap <= 0.0:
        temp = 4

    return temp

# JSONファイルから空調スケジュールを読み込む
def read_air_conditioning_schedules_from_json(d_room: dict):
    # 空調スケジュールの読み込み
    # 設定温度／PMV上限値の設定
    is_upper_temp_limit_set_schedule = np.array(d_room['schedule']['is_upper_temp_limit_set'])
    # 設定温度／PMV下限値の設定
    is_lower_temp_limit_set_schedule = np.array(d_room['schedule']['is_lower_temp_limit_set'])
    
    # PMV上限値
    pmv_upper_limit_schedule = np.array(d_room['schedule']['pmv_upper_limit'])
    # PMV下限値
    pmv_lower_limit_schedule = np.array(d_room['schedule']['pmv_lower_limit'])

    return is_upper_temp_limit_set_schedule, \
           is_lower_temp_limit_set_schedule, \
           pmv_upper_limit_schedule, \
           pmv_lower_limit_schedule

# スケジュールの読み込み
def get_hourly_air_conditioning_schedules(space: Space, dtmNow: datetime) -> None:
    # スケジュールのリスト番号の計算
    item = (get_nday(dtmNow.month, dtmNow.day) - 1) * 24 + dtmNow.hour

    # 上限PMV設定フラグ
    is_upper_temp_limit_set = space.is_upper_temp_limit_set_schedule[item]
    # 下限温度設定フラグ
    is_lower_temp_limit_set = space.is_lower_temp_limit_set_schedule[item]
    # 上限PMV
    pmv_upper_limit = space.pmv_upper_limit_schedule[item]
    # 下限PMV
    pmv_lower_limit = space.pmv_lower_limit_schedule[item]

    # 空調や通風などの需要がある場合にTrue
    air_conditioning_demand = is_upper_temp_limit_set or is_lower_temp_limit_set

    return is_upper_temp_limit_set, is_lower_temp_limit_set, pmv_upper_limit, pmv_lower_limit, air_conditioning_demand