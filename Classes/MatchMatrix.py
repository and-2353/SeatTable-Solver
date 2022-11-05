import pandas as pd
import pickle


class MatchMatrix():
    """
    講師と生徒の相性をマトリックスにしたもの

    subjects_detailed = [
    '英(小学生)', '数(小学生)', '国(小学生)', '理(小学生)', '社(小学生)',
    '英(中受生)', '数(中受生)', '国(中受生)', '理(中受生)', '社(中受生)',
    '英(中学生)', '数(中学生)', '国(中学生)', '理(中学生)', '社(中学生)',
    '英(高1)', '英(高2)', '英(高3)',
    '数Ⅰ', '数Ⅱ', '数Ⅲ', '数A', '数B', 
    '現文', '古典', '漢文', '小論文',
    '化学', '物理', '生物', '地学', '理総',
    '日史', '地理', '世史', '政経', '倫理', '現社'
    ]

    subjects も ID にした方がいい感
    あと、検索が遅い(?)からデータ構造 考え直した方がいいかも
    """

    def __init__(self, teachers, students):
        subjects = ['英', '数', '国', '理', '社']
        
        self.matrix = pd.DataFrame(index=[], columns=['teacher', 'student', 'subject', 'weight'])
        for tea_id in teachers.keys():
            for stu_id in students.keys():
                for subject in subjects:
                    record = pd.Series([tea_id, stu_id, subject, -100], self.matrix.columns)
                    self.matrix = self.matrix.append(record, ignore_index=True)

    def register_weight(self, tea_id, stu_id, subj, weight):
        df = self.matrix
        row = df.query("teacher == @tea_id and student == @stu_id and subject == @subj")
        #print(ind)
        df.loc[row.index, "weight"] = 100

    def register_existing_charge(self):
        """
        match_matrix に 既存の担当講師を登録する。
        """
        with open('objects/existing_charge.pickle', mode='rb') as p:
            existing_charge_list = pickle.load(p)
        for charge in existing_charge_list:
            print(charge['teacher'], charge['student'], charge['subject'], charge['weight'])
            self.register_weight(charge['teacher'], charge['student'], charge['subject'], charge['weight'])
        
    def get_weight(self, teacher_id, student_id, subject):
        # 挙動未検証
        df = self.matrix
        row = df.query("teacher == @tea_id and student == @stu_id and subject == @subj")
        return df.loc[row.index, "weight"] # エラー処理追加する(算, 英2)