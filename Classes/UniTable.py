import random
import pickle
from datetime import date
from utils import *
from Classes.Error import *

class UniTable():
    """
    Unitable は期間中全部のコマ、全講師の出勤情報を含む教室全体のテーブル。
    塾マネの座席表をイメージしてる。
    同じコマに生徒がいたら片方削除する関数が必要。
    初期作成は空で行う。最初にあった関数が使える?
    そこに各講師に紐づいたSeatTableを登録できるようにする。
    その後、UniTable の中で片コマ率やscoreを計算できるようにする。

    Attributes
    ----------
    unitable : dict
        登録期間中すべてのコマと、そのコマの授業・出勤情報を含む。
        Key : str
            期間中すべてのコマ。
            YYYY-MM-DD-J 形式
        Value : dict
            Key: str
                講師ID
            Value : Koma
                講師IDに紐づくKoma オブジェクト。
    ava_stu_dic : dict
        生徒の授業可能情報。
        登録期間中すべてのコマと、そのコマに授業可能な生徒リスト。
    ava_komas : List of str
        講師が出勤可能な時限リスト。
        要素は YYYY-MM-DD-J 形式。
        順番をシャッフルしたあと return される。
        探索では、どのコマから登録するか、という順番を決めるために使う。
    left_lecs : dict
        登録されている全生徒と、その生徒の講習コマを格納したdict。
        Key : str
            登録されている全生徒の名前。
            Student.id 形式
        Value : Student.lectures (List of Lecture)
    score : int
    """

    def __init__(self, teachers, students):
        """
        のちのちは start_day, end_day を 引数にとって__init__ の中でkeyだけ登録する(?)
        登録期間中すべてのコマを登録した方がいいかもしれない 講師がいるコマだけでいい? ---> ここは微妙
        """ 
        self.unitable = {}
        self.ava_stu_dic = {}
        self.ava_komas = []
        self.left_lecs = {}
        self.score = 0.

        self.make_table(teachers)
        self.make_ava_stu_dic(teachers, students)
        self.make_left_lecs(students)
        self.shuffle_ava_komas()

    def make_table(self, teachers):
        """
        table をつくる
        """
        for teacher in teachers.values():
            for jigen in teacher.schedule_ava:
                koma = init_koma_from_jigen(jigen)
                if jigen in self.unitable:
                    self.unitable[jigen][teacher.id] = koma
                else:
                    self.unitable[jigen] = {teacher.id : koma}


    def make_ava_stu_dic(self, teachers, students):
        """
        講師が出勤可能なコマと、そのコマに授業可能な生徒を格納した
        """
        for teacher in teachers.values():
            for teacher_d in teacher.schedule_ava:
                self.ava_stu_dic[teacher_d] = [] # 生徒がいなくても一旦空でKeyを登録
                for student in students.values():
                    if teacher_d in student.schedule_ava:
                        self.ava_stu_dic[teacher_d].append(student.id) # 生徒がいれば空のリストにappend


    def make_left_lecs(self, students):
        """
        left_lecs を作成する。
        """
        for student in students.values():
            id = student.id
            for lecture in student.lectures: 
                if id in self.left_lecs:
                    self.left_lecs[id].append(lecture)
                else:
                    self.left_lecs[id] = [lecture]
    

    def re_register_students_to_ava_stu_dic(self, students, canceled_stus):
        """
        self.ava_stu_dic に生徒を戻す。
        exclude_overlapping() の中でも呼ばれる。
        cancelされた対象の生徒に対して行う。
        self.ava_stu_dic は、授業が全登録された生徒は削除される仕様になっているので、再登録の際に戻す必要がある。
        ---
        入力
            students {'001': Student, '002': Student}
            canceled_stus ['001', '004', '002']

        """
        for jigen, stus in list(self.ava_stu_dic.items()): # jigen='YYYY-MM-DD-J', stus=['001', '003']
            for stu_id in canceled_stus: 
                # schedule_ava がみたいので、students を使ってstuインスタンスに変換
                stuobject = students[stu_id]

                # その jigen に生徒が 授業可能で、 その jigen に生徒がいなければ、生徒を戻す 
                if stu_id not in stus and jigen in stuobject.schedule_ava:
                    self.ava_stu_dic[jigen].append(stu_id)

                
    def make_print_dic(self):
        """"
        self.unitable を print するための dict に変換する関数
        登録されたKoma を str の形にするだけ
        あとで外部に出すか綺麗にする
        """
        li = {}
        for jigen, teaandkoma in self.unitable.items():
            lis = {}
            for tea, koma in teaandkoma.items():
                if koma.state == -1:
                    lis[tea] = '             x'
                elif koma.state == 0:
                    lis[tea] = '[     ],[     ]'
                elif koma.state == 1:
                    lis[tea] = f"{koma.lecture_1},[     ]"
                elif koma.state == 2:
                    lis[tea] = f"{koma.lecture_1},{koma.lecture_2}"
                elif koma.state == 3:
                    lis[tea]  = f"{koma.lecture_1}       "
            li[jigen] = lis

        pprint(li)
        #return li
            
    def is_all_lec_rgstred(self, stu_id):
        """
        ある生徒の授業がすべて登録されたか、チェックする。
        授業が登録されるたびに self.left_lecs からLecture が削除されるので、
        その生徒の list が空になった時、True と判定する。
        ---
        入力
            stu_id '001'
        """
        if len(self.left_lecs[stu_id]) == 0:
            return True
        else:
            return False

    def remove_stu(self, stu_id):
        """
        ava_stu_dic, left_lecs から生徒を削除する。
        ある生徒の授業がすべて登録された時に呼ばれる。

        -----------
        self.ava_stu_dic の Value のリストから生徒を全部削除する
            choice_and_register_lec() で、その生徒が選ばれないようにするため。
            この際、Value のリストの要素が0になったら、self.ava_stu_dic からそのコマ自体を消す。

        self.left_lecs の Key から生徒を消す
            self.left_lecs の要素をなくしていき、すべてなくなったら is_able_to_finish がTrueになる。
        ---
        入力
            stu_id '001'
        """
        for ava_stus in list(self.ava_stu_dic.values()):
            if stu_id in ava_stus:
                ava_stus.remove(stu_id)
        del self.left_lecs[stu_id] # self.left_lecs のkeyから生徒を消す

    def is_able_to_finish(self):
        """
        すべての生徒の授業がすべて登録されたか、チェックする。
        self.left_lecs はある生徒の授業がすべて登録されたときにその生徒(Key)が削除される。
        dict のKey がすべてなくなった時、Trueと判定する。
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
        # s += self.search_combi_spec()           # 特定の組み合わせによる加点・減点
        # s += self.calc_min_lec_day_interval()   # 次の授業との間隔の最小値
        # s -= self.calc_max_lec_inday_interval() # 同じ日に2つ以上授業がある日の授業時限間隔の最大値
        # s -= self.calc_changelessness()
        # s += self.calc_matching()
        self.score = s

    def count_katakoma(self):
        """
        片コマになっているコマの数を計算する。
        """
        katakoma = 0
        for jigen in self.unitable.values():
            for koma in jigen.values():
                if koma.state == 1:
                    katakoma += 1
        return katakoma

    def calculate_katakoma_rate(self):
        """
        片コマ率を計算する。
        """
        katakoma = 0
        all_koma = 0
        for teaandkoma in self.unitable.values():
            for koma in teaandkoma.values():
                if koma.state == 1:
                    katakoma += 1
                if koma.state in [1, 2 ,3]:
                    all_koma += 1
        if all_koma == 0:
            return 0
        else:
            return katakoma / all_koma

    def count_rgstred_jigens(self):
        """
        self.unitableの中で、1つ以上の授業が登録されている時限数を計算する。
        """
        rgstred_days = 0
        for jigen in self.unitable.values():
            for koma in jigen.values():
                if koma.state >= 1:# 1 or 2 or 3
                    rgstred_days += 1
                    break # 1つの時限で+1より多くプラスされないように
        return rgstred_days

    def count_rgstred_lecs(self):
        """
        self.tableに登録された授業の数を計算する。
        """
        rgstred_koma = 0
        for teaandkoma in self.unitable.values():
            for koma in teaandkoma.values():
                if koma.state == 1 or koma.state == 3:
                    rgstred_koma += 1
                elif koma.state == 2:
                    rgstred_koma += 2
        return rgstred_koma

    def count_left_lecs(self):
        """
        self.unitableの中で、登録されていない授業の数を計算する。
        """
        count = 0
        for lecs in self.left_lecs.values():
            count += len(lecs)
        return count

    def decide_cancel_targets(self, cancel_rate=0.5):
        """
        キャンセルの対象を決め、対象となる時限のリストを作成する。
        登録されていない時限が選ばれ得る。
        なので、cancel_rate は1以上でも問題ない。
        'YYYY-MM-DD-J' のリストを返す。
        """
        cancel_num = int(cancel_rate * self.count_rgstred_jigens())
        cancel_days = random.sample(self.unitable.keys(), cancel_num)
        return cancel_days

    def cancel_lecs(self, students, cancel_rate=0.5):
        """
        self.unitable に登録されたコマの登録を解除し、
        self.left_lecs に戻す。
        
        選ばれたjigen は全部キャンセルされるようにしている。
        jigen のうち random で選ばれた講師がキャンセルされるみたいにした方がいいかも。
        """
        canceled_stus = []
        cancel_days = self.decide_cancel_targets(cancel_rate)
        for jigen in cancel_days:        
            teaandkoma = self.unitable[jigen] # これからキャンセルするKoma
            for koma in teaandkoma.values():
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
        self.unitable上の 特定の組み合わせを数え、それによる加点・減点を計算する。
        特定の組み合わせは data/students/combi_spec.csv に登録されたもの。
        """
        with open('objects/combi_spec.pickle', mode='rb') as p:
            combi_spec_list = pickle.load(p)
        point = 0

        # self.unitable 上の 対2のコマ だけ見る
        for teaandkoma in self.unitable.values():
            for koma in teaandkoma.values():
                if koma.state == 2:
                    stus_in_koma = [koma.lecture_1.student_id, koma.lecture_2.student_id]

                    # conbi_spec_list = [{'combi' : ['001', '003'], weight : -1},
                    #                    {'combi' : ['002', '004'], weight : 1},]
                    for combi_spec in combi_spec_list:
                        if set(stus_in_koma) == set(combi_spec['combi']): # 組み合わせが同じなら
                            point += combi_spec['weight']
        return point

    def calc_matching(self, match_matrix):
        point = 0
        for teaandkoma in self.unitable.values():
            for tea, koma in teaandkoma.items():
                stus = koma.get_student_ids()
                subs = koma.get_subjects()
                if stus == None:
                    continue
                for stu, sub in zip(stus, subs):
                    weight = match_matrix.get_weight(tea, stu, sub)
                    point += weight
        return point

    def make_sbjct_tea_dic(self):
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
                teacher.id 形式。
                e.g.) ["00001", "00002", "00001"]
        """
        dic = {}                                    # return用辞書
        for teaandkoma in self.unitable.values():   # 各時限に対して
            for tea, koma in teaandkoma.items():
                if koma.state in [1, 2, 3]:              # 授業が入っていれば
                    sbjct_key = koma.lecture_1.student_name + '-' + koma.lecture_1.subject
                    if sbjct_key not in dic.keys():     # 辞書に未登録の「生徒-科目」なら
                        dic[sbjct_key] = [tea]
                    else:                               # 辞書に登録済の「生徒-科目」なら
                        dic[sbjct_key].append(tea)
                    if koma.state==2:                      # 対2 x 2人が登録されてるなら
                        sbjct_key = koma.lecture_2.student_name + '-' + koma.lecture_2.subject
                        if sbjct_key not in dic.keys(): # 辞書に未登録の「生徒-科目」なら
                            dic[sbjct_key] = [tea]
                        else:                           # 辞書に登録済の「生徒-科目」なら
                            dic[sbjct_key].append(tea)
        return dic

    def calc_lec_per_of_main_tea(self, stu_sub_teas):
        """
        ある生徒のある教科に携わる講師のうち、最も授業数が多い講師
        (これを main_tea とする)
        の授業割合を計算する。
        """
        pers = []
        all_lec_num = len(stu_sub_teas)
        tea_list = list(set(stu_sub_teas))
        for tea in tea_list:
            per = stu_sub_teas.count(tea) / all_lec_num
            pers.append(per)
        return max(pers)


    def calc_changelessness(self):
        """
        担当講師の一貫性を判定する。
        """
        charge_tea_nums = []
        main_charge_pers = []
        sbjct_tea_dic = self.make_sbjct_tea_dic()
        for stu_sub_teas in sbjct_tea_dic.values():

            # 講師の数を数える(少ない = 良い)
            charge_tea_num = len(list(set(stu_sub_teas)))
            charge_tea_nums.append(charge_tea_num - 1) # 担当講師1人ならペナルティなし 

            # 一番担当している割合が多い講師の授業割合を数える(高い = 良い)
            per = self.calc_lec_per_of_main_tea(stu_sub_teas)
            main_charge_pers.append(per)
        return sum(charge_tea_nums), sum(main_charge_pers) # 返し方微妙 割合足すの気持ち悪い


    def calc_min_lec_day_interval(self):
        """
        授業間隔日数の最小値を計算し返す。
        複数の生徒・科目がある場合は(通常はそうだが)、各生徒・科目に対して授業間隔日数の最小値を計算し、
        それらの合計を返す。
        これが大きい = 良い。
        これが大きい = 授業間隔が空いている状態。

        Returns
        -------
        _ : int
            複数生徒・科目の授業間隔日数の最小値の合計

        改善点
        ---

        授業数が多いものは間隔最大にしても2~3日になるし、それを伸ばすことにモチベーションがあまりない。
        (授業数が少ないもの授業の位置をずらすと大幅に値が改善されるが、授業数が少ないものはあまり改善されない)
        また最大値のみの計算にすると少し更新しただけでは値が変わりにくい。 ---> かなりよく改善されたときにしか更新されない(低確率), 変動しづらい
        以上の理由からある科目ごとにどれくらい間隔がまんべんないか みたいなものを算出して、それを均等に重みづけされるようにしてほしい。理論上最大の間隔を計算しておいてそれとの差をとるようにしてほしい。 <--- 均等になる
        あと、最大だけじゃなくて平均もとった方がいい(?) <--- ロスが連続的になる
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
        これが大きい = 悪い。
        これが大きい = 同じ日の中で間が空いているスケジュールが多く存在している状態。

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
        for jigen, teaandkoma in self.unitable.items():  # 各時限に対して
            for koma in teaandkoma.values():
                if koma.state in [1, 2, 3]:              # 授業が入っていれば
                    sbjct_key = koma.lecture_1.student_name + '-' + koma.lecture_1.subject
                    if sbjct_key not in dic.keys():     # 辞書に未登録の「生徒-科目」なら
                        dic[sbjct_key] = [jigen]
                    else:                               # 辞書に登録済の「生徒-科目」なら
                        dic[sbjct_key].append(jigen)
                    if koma.state == 2:                      # 対2 x 2人が登録されてるなら
                        sbjct_key = koma.lecture_2.student_name + '-' + koma.lecture_2.subject
                        if sbjct_key not in dic.keys(): # 辞書に未登録の「生徒-科目」なら
                            dic[sbjct_key] = [jigen]
                        else:                           # 辞書に登録済の「生徒-科目」なら
                            dic[sbjct_key].append(jigen)
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
        for jigen, teaandkoma in self.unitable.items():             # 各時限に対して
            for koma in teaandkoma.values():
                if koma.state in [1, 2, 3]:              # 授業が入っていれば
                    sbjct_key = koma.lecture_1.student_name
                    if sbjct_key not in dic.keys():     # 辞書に未登録の生徒なら
                        dic[sbjct_key] = [jigen]
                    else:                               # 辞書に登録済の生徒なら
                        dic[sbjct_key].append(jigen)
                    if koma.state==2:                      # 対2 x 2人が登録されてるなら
                        sbjct_key = koma.lecture_2.student_name
                        if sbjct_key not in dic.keys(): # 辞書に未登録の生徒なら
                            dic[sbjct_key] = [jigen]
                        else:                           # 辞書に登録済の生徒なら
                            dic[sbjct_key].append(jigen)
        for v in dic.values():
            v.sort()                                # 日時のリストを昇順にソート
        return dic

    def get_ava_tea(self, jigen):
        ava_tea = []
        teaandkoma = self.unitable[jigen]
        for tea_id, koma in teaandkoma.items():
            if koma.state in [0,1]: # 授業を入れられる
                ava_tea.append(tea_id)
        return ava_tea

    def is_katakoma(self, tea_id, jigen):
        state = self.unitable[jigen][tea_id].state
        if state == 1:
            return True
        elif state in [2, 3]:
            return False
        else:
            raise NotExpectedError
        

