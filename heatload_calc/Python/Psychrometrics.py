import math
from common import P

# 湿り空気の状態値計算モジュール

# 飽和水蒸気圧の計算（Wexler-Hylandの式）
# T : 温度[℃]
# Pws : 飽和水蒸気圧[kPa]
def Pws(T):
    tab = T + 273.15        # 絶対温度の計算
    if T >= 0.:
        Pws = math.exp(-5800.2206 / tab + 1.3914993 \
                - 0.048640239 * tab + 0.41764768 * 10.**-4. * tab**2. \
                - 0.14452093 * 10.**-7. * tab**3. + 6.5459673 * math.log(tab)) / 1000.
    else:
        Pws = math.exp(-5674.5359 / tab + 6.3925247 \
                - 0.9677843 * 10.**-2. * tab + 0.6215701 * 10.**-6. * tab**2. \
                + 0.20747825 * 10.**-8. * tab**3. - 0.9484024 * 10.**-12. * tab**4. \
                + 4.1635019 * math.log(tab)) / 1000.
    
    return Pws

# 水蒸気圧から絶対湿度を計算する（ダルトンの法則）
# Pw : 水蒸気圧[kPa]
# x : 絶対湿度[kg/kg(DA)]
def x(Pw):
    return 0.62198 * Pw / (P - Pw)

# 例題
# for T in range(-20, 20, 5):
#     print(T, Pws(T), x(Pws(T)))
