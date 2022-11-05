import random, copy
import pickle
from datetime import date, datetime, timedelta
from Classes.Error import NotExpectedError
from Classes.Teacher import Teacher
from utils import *

class SeatTable():
    """
    探索における1つの解(座席表)クラス。

    Attributes
    ----------
    teacher_name : str
        紐づく講師の名前。
    teacher_id : str
        紐づく講師ID。
    table : dict
        Key : str
            講師が出勤可能なコマ。
            YYYY-MM-DD-J 形式
        Value : Koma
            登録済のKomaオブジェクト。
    left_lecs : dict
        登録されている全生徒と、その生徒の講習コマを格納したdict。
        Key : str
            登録されている全生徒の名前。
            Student.id 形式
        Value : Student.lectures (List of Lecture)
    ava_stu_dic : dict
        講師が出勤可能で、かつ受講可能な生徒が一人以上いるコマを格納したdict。
        Key : str
            講師が出勤可能なコマ。
            YYYY-MM-DD-J 形式
        Value : List of str
            そのコマに授業可能な生徒の名前。
            Student.id 形式
    ava_komas : List of str
        講師が出勤可能で、かつ受講可能な生徒が一人以上いるコマ のリスト。
        要素は YYYY-MM-DD-J 形式。
        順番をシャッフルしたあと return される。
        探索では、どのコマから登録するか、という順番を決めるために使う。
    score : float, default = 0.0
        この座席表の評価値。
        片コマ率や授業間隔などから算出。
        この計算自体は、別の関数で行う。
    """

    def __init__(self, teacher_name ,teacher_id, table, left_lecs, ava_stu_dic):

        self.teacher_name = teacher_name
        self.teacher_id = teacher_id

        # 探索用リスト3つはコピーする
        self.table = copy.deepcopy(table)
        self.left_lecs = copy.deepcopy(left_lecs)
        self.ava_stu_dic = copy.deepcopy(ava_stu_dic)

        # どのコマから登録するか、という順番をランダムで決める
        self.ava_komas = list(self.ava_stu_dic.keys())
        random.shuffle(self.ava_komas)

        # スコアは0で新規作成される
        self.score = 0.

    def is_all_lec_rgstred(self, stu_id):
        """
        ある生徒の授業がすべて登録されたか、チェックする。
        授業が登録されるたびに self.left_lecs からLecture が削除されるので、
        その生徒の list が空になった時、True と判定する。

        Parameters
        ----------
        stu_id : str (Student.id 形式)
        """
        if len(self.left_lecs[stu_id]) == 0:
            return True
        else:
            return False
    
    def remove_stu(self, stu_id):
        """
        探索に使う dict から生徒を削除する。
        ある生徒の授業がすべて登録された時に呼ばれる。

        -----------
        self.ava_stu_dic の Value のリストから生徒を全部削除する
            choice_and_register_lec() で、その生徒が選ばれないようにするため。
            この際、Value のリストの要素が0になったら、self.ava_stu_dic からそのコマ自体を消す。

        self.left_lecs の Key から生徒を消す
            self.left_lecs の要素をなくしていき、すべてなくなったら is_able_to_finish がTrueになる。
        """
        for each_ava_stu in list(self.ava_stu_dic.values()):
            if stu_id in each_ava_stu:
                each_ava_stu.remove(stu_id)
        del self.left_lecs[stu_id] # self.left_lecs のkeyから生徒を消す

    def is_able_to_finish(self):
        """
        すべての生徒の授業がすべて登録されたか、チェックする。
        self.left_lecs はある生徒の授業がすべて登録されたときにその生徒が削除されるので、
        dict が空になった時、Trueと判定する。
        """
        if len(self.left_lecs) == 0:
            return True
        else:
            return False
    
    def calculate_score(self):
        """
        スコアを計算する。高い = 良い。
        """
        s = 100.
        s -= self.count_katakoma()              # 片コマ数
        s -= self.count_left_lecs()             # 未登録授業数
        s += self.search_combi_spec()           # 特定の組み合わせによる加点・減点
        s += self.calc_min_lec_day_interval()   # 次の授業との間隔の最小値
        s -= self.calc_max_lec_inday_interval() # 同じ日に2つ以上授業がある日の授業時限間隔の最大値

        self.score = s
    
    def calculate_katakoma_rate(self):
        """
        片コマ率を計算する。
        """
        katakoma = 0
        all_koma = 0
        for item in self.table.values():
            if item.state == 1:
                katakoma += 1
            if item.state == 1 or item.state == 2 or item.state == 3:
                all_koma += 1
        if all_koma == 0:
            return 0
        else:
            return katakoma / all_koma
    
    def count_katakoma(self):
        """
        片コマになっているコマの数を計算する。
        """
        katakoma = 0
        for item in self.table.values():
            if item.state == 1:
                katakoma += 1
        return katakoma

    def count_rgstred_lecs(self):
        """
        self.tableに登録された授業の数を計算する。
        """
        rgstred_koma = 0
        for item in self.table.values():
            if item.state == 1 or item.state == 3:
                rgstred_koma += 1
            elif item.state == 2:
                rgstred_koma += 2
        return rgstred_koma


    def count_rgstred_days(self):
        """
        self.tableの中で、1つ以上の授業が登録されている時限数を計算する。
        """
        rgstred_days = 0
        for item in self.table.values():
            if item.state >= 1:# 1 or 2 or 3
                rgstred_days += 1
        return rgstred_days

    
    def count_left_lecs(self):
        """
        self.table の中で、登録されていない授業の数を計算する。
        """
        count = 0
        for lecs in self.left_lecs.values():
            count += len(lecs)
        return count

    def decide_cancel_targets(self, cancel_rate):
        """
        キャンセルの対象を決め、対象となる時限のリストを作成する。
        登録されていない時限が選ばれ得る。
        なので、cancel_rate は1以上でも問題ない。
        'YYYY-MM-DD-J' のリストを返す。
        """
        cancel_num = int(cancel_rate * self.count_rgstred_days())
        cancel_days = random.sample(self.table.keys(), cancel_num)
        return cancel_days


    def cancel_lecs(self, students, cancel_rate=0.5):
        """
        self.table に登録されたコマの登録を解除し、
        self.left_lecs に戻す。
        """
        canceled_stus = []
        cancel_days = self.decide_cancel_targets(cancel_rate)
        for jigen in cancel_days:        
            koma = self.table[jigen] # これからキャンセルするKoma
            if koma.state == 0: # koma.state が0ならキャンセルしないで続ける
                continue 
            elif koma.state in [1, 2, 3]:
                stu_ids = koma.get_student_ids() 
                lectures = koma.get_lectures()

                # self.left_lecs に戻す
                for id, lec in zip(stu_ids, lectures): # state==1か3 なら1回, state==2 なら2回ループ 
                    if id in self.left_lecs:
                        self.left_lecs[id].append(lec)
                    else:
                        self.left_lecs[id] = [lec]
                    canceled_stus.append(id)                
                koma.delete_lecture() # コマの削除

        canceled_stus = list(set(canceled_stus)) # 重複排除
        self.re_register_students_to_ava_stu_dic(students, canceled_stus)
        

    def re_register_students_to_ava_stu_dic(self, students, canceled_stus):
        """
        self.ava_stu_dic に生徒を戻す。
        cancelされた対象の生徒に対して行う。
        self.ava_stu_dic は、授業が全登録された生徒は削除される仕様になっているので、再登録の際に戻す必要がある。
        """
        for jigen, stus in list(self.ava_stu_dic.items()): # jigen='YYYY-MM-DD-J', stus = ['001', '003', ...]
            
            for stu in canceled_stus:
                # schedule_ava がみたいので、students を使ってstuインスタンスに変換
                stuobject = students[stu]

                # その jigen に生徒が 授業可能で、 その jigen に生徒がいなければ、生徒を戻す 
                if stu not in stus and jigen in stuobject.schedule_ava:
                    self.ava_stu_dic[jigen].append(stu)


    def reset_score(self):
        """ 
        self.score のリセットをする。
        """
        self.score = 0


    def shuffle_ava_komas(self):
        """
        ava_komas をシャッフルする。
        """
        self.ava_komas = list(self.ava_stu_dic.keys())
        random.shuffle(self.ava_komas)


    def search_combi_spec(self):
        """
        self.table上の 特定の組み合わせを数え、それによる加点・減点を計算する。
        特定の組み合わせは data/students/combi_spec.csv に登録されたもの。
        """
        with open('objects/combi_spec.pickle', mode='rb') as p:
            combi_spec_list = pickle.load(p)
        point = 0

        # self.table 上の 対2のコマ だけ見る
        for koma in self.table.values():
            if koma.state == 2:
                stus_in_koma = [koma.lecture_1.student_id, koma.lecture_2.student_id]

                # conbi_spec_list = [{'combi' : ['001', '003'], weight : -1},
                #                    {'combi' : ['002', '004'], weight : 1},]
                for combi_spec in combi_spec_list:
                    if set(stus_in_koma) == set(combi_spec['combi']): # 組み合わせが同じなら
                        point += combi_spec['weight']
        return point

    
    def calc_min_lec_day_interval(self):

        """
        授業間隔日数の最小値を計算し返す。
        複数の生徒・科目がある場合は(通常はそうだが)、各生徒・科目に対して授業間隔日数の最小値を計算し、
        それらの合計を返す。

        Returns
        -------
        _ : int
            複数生徒・科目の授業間隔日数の最小値の合計
        """
        min_intervals = []                             # return 用リスト
        rgstred_lec_dic = self.make_sbjct_date_dic()   # 生徒・科目の日時をまとめた辞書の作成
        for stu_sub_dates in rgstred_lec_dic.values(): # 各生徒・科目の日時リストに対して
            if len(stu_sub_dates) in [0, 1]:           # 登録授業数が0 or 1なら skip (間隔計算不可能だから)
                continue
            days = []                                  # 授業日時を保持するリスト
            for day_str in stu_sub_dates:              # 各日時に対して
                day = day_str.split('-')
                days.append(date(int(day[0]), int(day[1]), int(day[2])))       # 授業日時を days リストに追加
            intervals = [(days[k+1]-days[k]).days for k in range(len(days)-1)] # 隣り合う授業日の間隔を計算
            min_intervals.append(min(intervals))                               # 授業間隔の最小値だけを保存
        return sum(min_intervals)                      # 最小値の合計を返す
    

    def calc_max_lec_inday_interval(self):
        """
        同じ日に2つ以上授業がある生徒の、その日の授業間隔時限の最大値を返す。
        同じ日に2つ以上授業がある生徒が複数人いる場合、上記の最大値の合計を返す。
        """
        max_intervals = []                         # return 用リスト
        rgstred_lec_dic = self.make_stu_date_dic() # 生徒の全科目の日時をまとめた辞書の作成
        for stu_dates in rgstred_lec_dic.values(): # 各生徒の日時リストに対して
            if len(stu_dates) in [0, 1]:           # 登録授業数が0 or 1ならskip (間隔計算不可能だから)
                continue
            intervals = [0]                        # 同じ日の時限間隔を保持するリスト
            for i in range(len(stu_dates)-1):      # 各日時に対して
                if stu_dates[i].split('-')[:3] == stu_dates[i+1].split('-')[:3]: # もし次の授業の日が同じ日なら
                    intervals.append(int(stu_dates[i+1].split('-')[-1]) - int(stu_dates[i].split('-')[-1])) # 時限間隔を保存
            max_intervals.append(max(intervals))   # 時限間隔の最大値だけを保存
        return sum(max_intervals)                  # 最大値の合計を返す
    

    def make_sbjct_date_dic(self):
        """
        ある生徒のある科目が登録されている日時をまとめた辞書を返す。
        なお、日時はソートしてから返す。

        Returns
        -------
        dic : dict
            Key : str
                生徒の科目。「{生徒名}-{科目}」の形式。
                e.g.) "中3A-数"
            Value : List of str
                Key の科目が登録されている日時のリスト。
                YYYY-MM-DD-J 形式。
                e.g.) ["2021-10-13-7", "2021-10-13-8", "2021-10-16-7"]
        """
        dic = {}                                    # return用辞書
        for d, k in self.table.items():             # 各時限に対して
            if not k.state in [-1, 0]:              # 授業が入っていれば
                sbjct_key = k.lecture_1.student_name + '-' + k.lecture_1.subject
                if sbjct_key not in dic.keys():     # 辞書に未登録の「生徒-科目」なら
                    dic[sbjct_key] = [d]
                else:                               # 辞書に登録済の「生徒-科目」なら
                    dic[sbjct_key].append(d)
                if k.state==2:                      # 対2 x 2人が登録されてるなら
                    sbjct_key = k.lecture_2.student_name + '-' + k.lecture_2.subject
                    if sbjct_key not in dic.keys(): # 辞書に未登録の「生徒-科目」なら
                        dic[sbjct_key] = [d]
                    else:                           # 辞書に登録済の「生徒-科目」なら
                        dic[sbjct_key].append(d)
        for v in dic.values():
            v.sort()                                # 日時のリストを昇順にソート
        return dic
    

    def make_stu_date_dic(self):
        """
        ある生徒の全科目の授業が登録されている日時をまとめた辞書を返す。
        なお、日時はソートしてから返す。

        Returns
        -------
        dic : dict
            Key : str
                生徒名。e.g.) "中3A"
            Value : List of str
                Key の科目が登録されている日時のリスト。
                YYYY-MM-DD-J 形式。
                e.g.) ["2021-10-13-7", "2021-10-13-8", "2021-10-16-7"]
        """
        dic = {}                                    # return用辞書
        for d, k in self.table.items():             # 各時限に対して
            if not k.state in [-1, 0]:              # 授業が入っていれば
                sbjct_key = k.lecture_1.student_name
                if sbjct_key not in dic.keys():     # 辞書に未登録の生徒なら
                    dic[sbjct_key] = [d]
                else:                               # 辞書に登録済の生徒なら
                    dic[sbjct_key].append(d)
                if k.state==2:                      # 対2 x 2人が登録されてるなら
                    sbjct_key = k.lecture_2.student_name
                    if sbjct_key not in dic.keys(): # 辞書に未登録の生徒なら
                        dic[sbjct_key] = [d]
                    else:                           # 辞書に登録済の生徒なら
                        dic[sbjct_key].append(d)
        for v in dic.values():
            v.sort()                                # 日時のリストを昇順にソート
        return dic