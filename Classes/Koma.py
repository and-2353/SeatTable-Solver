from datetime import date, timedelta
from Classes.Error import *


class Koma():
    """
    座席表の各時限を表す。
    いわば、Lecture インスタンスをいれる箱。

    Attributes
    ----------
    day : datetime
        日付。
    jigen : int
        時限。1限-8限まで。
    state : int
        コマの状態。
        -1: 講師出勤不可能。
         0: 講師出勤可能かつ授業が入っていない。
         1: 講師出勤可能かつ 対2 x 1人 が入っている。(いわゆる片コマ)
         2: 講師出勤可能かつ 対2 x 2人 が入っている。
         3: 講師出勤可能かつ 対1 が入っている。
    lecture_1 : Lecture
        対1 or 対2の1人目の授業。
        state == -1, 0 の時は None。
    lecture_2 : Lecture
        対2の2人目の授業。
        state == -1, 0, 1, 3 の時は None。
    """

    def __init__(self, day, jigen, state, lecture_1=None, lecture_2=None):
        """
        Parameters
        ----------
        day : datetime
            日付。
        jigen : int
            時限。1限-8限まで。
        state : int
            コマの状態。
            -1: 講師出勤不可能。
             0: 講師出勤可能かつ授業が入っていない。
             1: 講師出勤可能かつ 対2 x 1人 が入っている。(いわゆる片コマ)
             2: 講師出勤可能かつ 対2 x 2人 が入っている。
             3: 講師出勤可能かつ 対1 が入っている。
        lecture_1 : Lecture
            対1 or 対2の1人目の授業。
            state == -1, 0 の時は None。
        lecture_2 : Lecture
            対2の2人目の授業。
            state == -1, 0, 1, 3 の時は None。
        """
        self.day = day
        self.jigen = jigen
        self.state = state
        self.lecture_1 = lecture_1
        self.lecture_2 = lecture_2

    def __str__(self):
        if self.state == -1:
            return '           x'
        elif self.state == 0:
            return '[   ], [   ]'
        elif self.state == 1:
            return f"{self.lecture_1},[   ]"
        elif self.state == 2:
            return f"{self.lecture_1},{self.lecture_2}"
        elif self.state == 3:
            return f"{self.lecture_1}      "

    def register(self, lecture):
        if self.state == -1:
            raise NotExpectedError # 講師が出勤不可能
        elif self.state == 2 or self.state == 3:
            raise NotExpectedError # 既に対2 x 2人の授業、もしくは対1の授業が入っている
        elif self.state == 0:
            self.lecture_1 = lecture
            if lecture.is_one_on_one: # 登録されたlecture が対1なら
                self.state = 3
            else:
                self.state = 1
        elif self.state == 1:
            if lecture.is_one_on_one:
                raise CannotRegisterError # 対2 x 1人 が入っているコマに対1の授業を登録することはできない
            else:
                if self.lecture_1.student_name == lecture.student_name:      
                    raise CannotRegisterError # 対2 x 1人 が入っているコマに、それと同じ生徒の対2の授業を登録することはできない
                else:
                    self.lecture_2 = lecture
                    self.state = 2

    def get_student_ids(self):
        """
        Komaに登録されている 生徒ID のリスト を返す。
        None か List(要素数1もしくは2) を返す。 
        """
        if self.state in [-1, 0]:
            return None
        elif self.state == 1 or self.state == 3:
            return [self.lecture_1.student_id] # 生徒ID 1つ 返す
        elif self.state == 2:
            return [self.lecture_1.student_id, self.lecture_2.student_id] # 生徒ID 2つ 返す
        else:
            raise NotExpectedError

    def get_lectures(self):
        """
        Komaに登録されている Lecture のリスト を返す。
        None か List(要素数1もしくは2) を返す。 
        """
        if self.state in [-1, 0]:
            return None
        elif self.state == 1 or self.state == 3:
            return [self.lecture_1] # Lecture 1つ 返す
        elif self.state == 2:
            return [self.lecture_1, self.lecture_2] # Lecture 2つ 返す
        else:
            raise NotExpectedError

    def get_subjects(self):
        """
        Komaに登録されている 教科(str) のリスト を返す。
        None か List(要素数1もしくは2) を返す。 
        """
        if self.state in [-1, 0]:
            return None
        elif self.state == 1 or self.state == 3:
            return [self.lecture_1.subject] # str 1つ 返す
        elif self.state == 2:
            return [self.lecture_1.subject, self.lecture_2.subject] # str 2つ 返す
        else:
            raise NotExpectedError


    def delete_lecture(self):
        """
        登録をリセットする。
        """
        self.lecture_1 = None
        self.lecture_2 = None
        self.state = 0

