from Classes.Day import Day


class Person:
    """
    人クラス。
    Student クラスと Teacher クラスはこれを継承する。

    Attributes
    ----------
    name : str
        生徒/講師名。
    id : str
        生徒/講師ID。
    schedule : List of Day
        授業可能日時スケジュール。
    """

    def __init__(self, name, id, schedule=None):
        """
        Parameters
        ----------
        name : str
            生徒/講師名。
        id : str
            生徒/講師ID。
        schedule : List of Day, default = []
            授業可能日時スケジュール。
            後から登録も可。
            -> set_schedule(), register_schedule() を使用。
        schedule_ava : List of str
            スケジュールのうち、授業可能な日時を登録したもの。
            要素は YYYY-MM-DD-J 形式。
        """
        self.name = name
        self.id = id
        if schedule == None:
            self.schedule = []
        else:
            self.schedule = schedule
        self.schedule_ava = []

    def set_schedule(self, schedule):
        """
        授業可能日時スケジュールを設定する。

        Parameters
        ----------
        schedule : List of Day
            授業可能日時スケジュール。
        """
        self.schedule = schedule

    def register_schedule(self, day):
        """
        授業可能日時スケジュールを設定する。

        Parameters
        ----------
        day : Day
            ある日の授業可能日時スケジュール。
        """
        self.schedule.append(day)

    def set_schedule_from_csv(self, csv_path):
        with open(csv_path, encoding="utf-8") as f:
            f.readline() # 最初の行は読み飛ばす。
            for line in f:
                rows = line.rstrip('\n').split(',')
                date = rows[0].split('/')
                date = [int(i) for i in date]
                koma = rows[2:]
                for i in range(len(koma)):
                    if len(koma[i]) == 0:
                        koma[i] = '0'
                koma = [int(i) for i in koma]
                day = Day(year=date[0], month=date[1], day=date[2], koma=koma)
                self.register_schedule(day)

    def set_schedule_ava(self):
        for student_d in self.schedule:
            for i, jigen in enumerate(student_d.koma):
                if jigen == 1:
                    ava_koma = str(student_d.date) + '-' + str(i+1)
                    self.schedule_ava.append(ava_koma) 