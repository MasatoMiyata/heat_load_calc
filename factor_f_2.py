"""
日射取得率補正係数

ガラスの仕様の区分は、区分1（単板ガラス）を想定する。
方位が北・北東・東・南東・南・南西・西・北西の窓については、日除け下端から窓上端までの垂直方向の距離：窓の開口高さ寸法：壁面からの日除けの張り出し寸法＝3:0:1とする。
8地域の暖房期は、8地域の冷房期で代用。

平成28年省エネルギー基準に準拠したエネルギー消費性能の評価に関する技術情報（住宅）
2.エネルギー消費性能の算定方法
2.2 算定方法
第三章 暖冷房負荷と外皮性能
第四節 日射熱取得
付録 B 大部分がガラスで構成されている窓等の開口部における取得日射熱補正係数

データ「取得日射熱補正係数」
表 1(a) 屋根又は屋根の直下の天井に設置されている開口部の暖房期の取得日射熱補正係数
表 1(b) 屋根又は屋根の直下の天井に設置されている開口部の冷房期の取得日射熱補正係数

"""


def get_f(season, region, direction):

    return {
        'heating' :{
            'top'    : {1: 1.000, 2: 1.000, 3: 1.000, 4: 1.000, 5: 1.000, 6: 1.000, 7: 1.000, 8: 1.000 },
            'n'      : {1: 0.683, 2: 0.682, 3: 0.680, 4: 0.683, 5: 0.691, 6: 0.689, 7: 0.698, 8: 0.660 },
            'ne'     : {1: 0.665, 2: 0.666, 3: 0.662, 4: 0.658, 5: 0.658, 6: 0.655, 7: 0.657, 8: 0.653 },
            'e'      : {1: 0.684, 2: 0.684, 3: 0.676, 4: 0.679, 5: 0.689, 6: 0.686, 7: 0.684, 8: 0.671 },
            'se'     : {1: 0.697, 2: 0.689, 3: 0.684, 4: 0.675, 5: 0.699, 6: 0.703, 7: 0.693, 8: 0.632 },
            's'      : {1: 0.691, 2: 0.666, 3: 0.675, 4: 0.655, 5: 0.693, 6: 0.683, 7: 0.691, 8: 0.586 },
            'sw'     : {1: 0.692, 2: 0.682, 3: 0.684, 4: 0.675, 5: 0.696, 6: 0.685, 7: 0.696, 8: 0.629 },
            'w'      : {1: 0.682, 2: 0.685, 3: 0.680, 4: 0.677, 5: 0.687, 6: 0.686, 7: 0.686, 8: 0.671 },
            'nw'     : {1: 0.667, 2: 0.666, 3: 0.663, 4: 0.657, 5: 0.662, 6: 0.660, 7: 0.661, 8: 0.658 },
            'bottom' : {1: 0.000, 2: 0.000, 3: 0.000, 4: 0.000, 5: 0.000, 6: 0.000, 7: 0.000, 8: 0.000 }
        },
        'cooling' :{
            'top'    : {1: 1.000, 2: 1.000, 3: 1.000, 4: 1.000, 5: 1.000, 6: 1.000, 7: 1.000, 8: 1.000 },
            'n'      : {1: 0.667, 2: 0.670, 3: 0.667, 4: 0.665, 5: 0.669, 6: 0.659, 7: 0.655, 8: 0.660 },
            'ne'     : {1: 0.671, 2: 0.666, 3: 0.663, 4: 0.657, 5: 0.662, 6: 0.659, 7: 0.658, 8: 0.653 },
            'e'      : {1: 0.680, 2: 0.671, 3: 0.659, 4: 0.670, 5: 0.665, 6: 0.669, 7: 0.670, 8: 0.671 },
            'se'     : {1: 0.626, 2: 0.621, 3: 0.610, 4: 0.608, 5: 0.619, 6: 0.613, 7: 0.607, 8: 0.632 },
            's'      : {1: 0.515, 2: 0.524, 3: 0.510, 4: 0.501, 5: 0.541, 6: 0.541, 7: 0.536, 8: 0.586 },
            'sw'     : {1: 0.622, 2: 0.622, 3: 0.621, 4: 0.607, 5: 0.625, 6: 0.614, 7: 0.605, 8: 0.629 },
            'w'      : {1: 0.678, 2: 0.671, 3: 0.679, 4: 0.663, 5: 0.665, 6: 0.671, 7: 0.670, 8: 0.671 },
            'nw'     : {1: 0.671, 2: 0.667, 3: 0.668, 4: 0.658, 5: 0.660, 6: 0.664, 7: 0.660, 8: 0.658 },
            'bottom' : {1: 0.000, 2: 0.000, 3: 0.000, 4: 0.000, 5: 0.000, 6: 0.000, 7: 0.000, 8: 0.000 }
        }
    }[season][direction][region]