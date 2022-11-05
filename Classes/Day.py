import datetime


class Day:
    """
    ある日のスケジュールを表現するクラス。

    Attributes
    ----------
    date : datetime
        日付。
    koma : List
        date の日の来塾可否スケジュール (1-8限)。
    """

    def __init__(self, koma, year=None, month=None, day=None, ymd=None):
        """
        Parameters
        ----------
        year : int, default None
            年。
        month : int, default None
            月。
        day : int, default None
            日。
        ymd : datetime, default None
            日付。datetime 型での初期化に対応。
        koma : List of bool, default [0,0,0,0,0,0,0,0]
            date の日の来塾可否スケジュール (1-8限)。
            True (1)  -> 来れる。
            False (0) -> 来られない。
            e.g. [[0,0,0,0,1,1,1,1], [1,1,1,0,0,0,0,0], ...]
        """
        if ymd is None:
            self.date = datetime.date(year, month, day)
        else:
            self.date = ymd
        self.koma = koma
