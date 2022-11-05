from Classes.Person import Person
from Classes.Lecture import Lecture


class Student(Person):
    """
    生徒クラス。名前や講習コマ情報を保持する。
    Person クラスを継承する。

    Attributes
    ----------
    name : str
        生徒名。
    id : str
        生徒ID。
    schedule : List of Day
        生徒本人の授業可能日時スケジュール。
    subjects : List of Subject
        Subject インスタンスのリスト。
    lectures : List of Lecture
        Lecture インスタンスのリスト。
        1つ1つの授業を、このリストに格納する。
    """

    def __init__(self, name, id, schedule=None, subjects=None):
        """
        Parameters
        ----------
        name : str
            生徒名。
        id : str
            生徒ID。
        schedule : List of Day, default = []
            生徒本人の授業可能日時スケジュール。
            後から登録も可。-> register_schedule() を使用。
        subjects : List of Subject, default = []
            Subject インスタンスのリスト。
            後から登録も可。-> register_subject() を使用。
            e.g. [Subject("English", 12, False), Subject("Math", 8, True), ...]
        """
        super().__init__(name, id, schedule)
        if subjects == None:
            self.subjects = []
        else:
            self.subjects = subjects
        self.lectures = []
        

    def register_subject(self, subject):
        """
        生徒が振り込んだ講習コマを1科目ずつ登録。

        Parameters
        ----------
        subject : Subject
            Subject インスタンス。
        """
        self.subjects.append(subject)
    
    
    def set_subjects(self, subjects):
        """
        生徒が振り込んだ講習コマを全科目登録。

        Parameters
        ----------
        subjects : List of subject
            subject インスタンスのリスト。
        """
        self.subjects = subjects

    def set_lectures(self):
        """
        登録された科目を1授業ずつに分解し、self.lectures リストに追加。
        """
        for subject in self.subjects:
            for _ in range(subject.num_of_lecture):
                lecture = Lecture(
                        student_name=self.name,
                        student_id=self.id,
                        subject=subject.subject,
                        is_one_on_one=subject.is_one_on_one)
                self.lectures.append(lecture)


