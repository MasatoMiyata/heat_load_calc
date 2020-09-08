"""
時間間隔に関するモジュール
"""


def get_n_hour(interval):
    """
    1時間を分割するステップ数を求める。
    Args:
        interval: 生成するデータの時間間隔であり、以下の文字列で指定する。
            1h: 1時間間隔
            30m: 30分間隔
            15m: 15分間隔
    Returns:
        1時間を分割するステップ数
        1時間: 1
        30分: 2
        15分: 4
    """

    return {
        '1h': 1,
        '30m': 2,
        '15m': 4
    }[interval]
