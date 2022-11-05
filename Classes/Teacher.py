from Classes.Person import Person
from Classes.Lecture import Lecture
from Classes.Koma import Koma
from Classes.Day import Day


class Teacher(Person):
    """
    講師クラス。
    Person クラスを継承する。

    Attributes
    ----------
    name : str
        講師名。
    id : str
        講師ID。
    schedule : List of Day
        授業可能日時スケジュール。
    subjects : List of Subjects
        担当する講習コマ。
    students : List of Student
        担当する生徒。
    """

    def __init__(self, name, id, schedule=None):
        """
        Parameters
        ----------
        name : str
            講師名。
        id : str
            講師ID。
        schedule : List of Day, default = None
            講師本人の授業可能日時スケジュール。
            後から登録も可。-> register_schedule() を使用。
        """
        super().__init__(name, id, schedule)
        self.table = {}


    def make_table(self):
        """
        探索の際、コマを登録するために使われる
        table を作成する。

        table: dict
        -----------
        Key: str
            講師が出勤可能なコマ。
            YYYY-MM-DD-J 形式

        Value: Koma
            登録用のKomaオブジェクト。
            state = 0 (講師出勤可能かつ授業が入っていない) を指定して初期作成。
        """
        for teacher_d in self.schedule_ava: # strが回る
            # teacher_d はstr(YYYY-MM-DD-J) なので、Dayの登録ができる形に変換する
            d_info = teacher_d.split('-')
            d_info = [int(i) for i in d_info]
            day = Day(year=d_info[0], month=d_info[1], day=d_info[2], koma=None) # koma は入れた方がいい？
            jigen = d_info[3]
            self.table[teacher_d] = Koma(day=day, jigen=jigen, state=0)
            

        
                    
                        
        


