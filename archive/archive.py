def make_seat_table(start_day, end_day):
    # from seat_solver.py
    """
    座席表を初期作成する。
    """
    seat_table = []
    for d in range((end_day-start_day).days + 1):
        seat_day = []
        for jigen in range(1, 9):
            koma = Koma(day=start_day+timedelta(d), jigen=jigen, state=-1)
            seat_day.append(koma)
        seat_table.append(Day(ymd=start_day+timedelta(d), koma=seat_day))
    return seat_table



def make_subjects(path, student_name):
    # from seat_solver.py
    """
    生徒の登録時に使うSubjectインスタンスのリストを作成する。
    """
    subjects = []
    with open(path, encoding='utf-8')as f:
        f.readline()
        for subject_info in f:
            subject_info = subject_info.rstrip('\n').split(',')
            subject, num_of_lecture, is_one_on_one, charge = subject_info
            subject_ = Subject(student_name, subject, int(num_of_lecture), int(is_one_on_one))
            subjects.append(subject_)
    return subjects


def update_ava_stu_dic(date, jigen, student_name, ava_stu_dic):
    # from utils.py
    """
    ava_stu_dic に、「そのコマに受講可能な生徒」を登録する。
    make_ava_stu_dic の中で呼び出され、ava_stu_dic の初期作成時にのみ使われる。

    Parameters
    ----------
    date : Day
    jigen : int
    student_name : str
    ava_stu_dic : dict
    """
    koma = str(date) + '-' + str(jigen)
    if koma in ava_stu_dic:
        ava_stu_dic[koma].append(student_name)
    else:
        ava_stu_dic[koma] = [student_name]
    return ava_stu_dic


def strstu_to_stuobject(strstuid, students):
    # from utils.py
    """
    str型のstudentを、対応するStudentクラスのオブジェクトに変換して返す。

    Parameters
    ----------
    strstuid : str
        変換元の生徒ID。
    students: List of Student
    """ 
    for student in students:
        if strstuid == student.id:
            return student

def check_all_lecture_registered(i_dic_to_trial):
    # from utils.py
    """
    すべての授業が登録されたか判定する。

    Parameters
    ----------
    i_dic_to_trial : dict

    ---------------------------------------
    作成途中。やろうとしていることは以下
    
    rgstred_lecs : dict
        Value : Lecture または 生徒名+教科名
        Key : i_dic_to_trial の中にあるその授業の数
    を作る。
    どこかで「入れるべきすべてのコマ」を格納した別のdicを作っておいて、それと比べる
    ---------------------------------------  
    """
    rgstred_lecs = {}
    for koma in i_dic_to_trial.values():
        for lec in [koma.lecture_1, koma.lecture_2]:
            if lec not in rgstred_lecs:
                rgstred_lecs[lec] = 1
            else:
                rgstred_lecs[lec] += 1
    return rgstred_lecs


def is_same_day(day1, day2):
    # from utils.py
    """
    同じ日かを判定する。

    Parameters
    ----------
    day1 : Day
    day2 : Day
    """
    if day1.date == day2.date:
        return True
    else:
        return False


def display_seat_table(seat_table):
    # from utils.py
    count = 0
    string_list = ["" for _ in range(9)]
    for day in seat_table:
        count += 1
        string_list[0] += f"  {day.date} "
        for jigen in range(8):
            string_list[jigen+1] += f"{day.koma[jigen]} "
        if count == 7:
            count = 0
            for i in range(len(string_list)):
                print(string_list[i])
                string_list[i] = ""
            print()
    for i in range(len(string_list)):
        print(string_list[i])
        string_list[i] = ""

def create_existing_charge_csv():
    # from seat_solver.py
    """
    existing_charge_list : list of dict
        {'teacher': tea_id, 'student': stu_id, 'subject': str, 'weight': int} <--- これを要素として持つリスト
    
    """
    with open('data/existing_charge.csv', encoding='utf-8', mode='w', newline='') as e:
        writer = csv.writer(e)
        writer.writerow(['teacher', 'student', 'subject', 'weight'])
        with open('data/students/info.csv', encoding='utf-8') as f:
            f.readline() # 最初の行は読み飛ばす。
            for student_info in f:
                student_info = student_info.rstrip('\n').split(',')
                id, _ = student_info
                subjects_path = f'data/students/subjects/{id}.csv'
                with open(subjects_path, encoding='utf-8')as s:
                    s.readline()
                    for subject_info in s:
                        subject_info = subject_info.rstrip('\n').split(',')
                        subject, _, _, charge_teacher = subject_info
                        writer.writerow([charge_teacher, id, subject, 100])

def register(seat_table):
    # from seat_solver.py
    # re_register と大きく変わりないので統合した
    for koma in seat_table.ava_komas: 
        ava_stu = seat_table.ava_stu_dic[koma]
        if len(ava_stu) == 0:
            continue
        # ------------------------
        # 授業1の登録ここから
        seat_table, slcted_stu, ava_stu = choice_and_register_lec(koma, seat_table, ava_stu) # 登録
        if seat_table.is_all_lec_rgstred(slcted_stu): # ある生徒の授業が全登録されたか判定
            seat_table.remove_stu(slcted_stu)
        if seat_table.is_able_to_finish(): # 全生徒の授業が全登録されたか判定
            break
        # 授業1の登録ここまで
        # ------------------------

        if is_katakoma(seat_table.table, koma) and is_there_any_stu_else(ava_stu): # (片コマ) and (受講可能な生徒が他にもいる)
            # ------------------------
            # 授業2の登録ここから
            try:
                seat_table, slcted_stu, _ = choice_and_register_lec(koma, seat_table, ava_stu) # 登録
            except CannotRegisterError:
                continue
            if seat_table.is_all_lec_rgstred(slcted_stu): # ある生徒の授業が全登録されたか判定
                seat_table.remove_stu(slcted_stu)
            if seat_table.is_able_to_finish(): # 全生徒の授業が全登録されたか判定
                break
            # 授業2の登録ここまで
            # ------------------------
    seat_table.calculate_score()
    return seat_table

def register_seattable_to_unitable(teachers, students, N_SEARCH):
    # from seat_solver.py
    """
    seat_table を一旦探索して、遺伝的処理にかけずにunitable に登録する
    """
    unitable = UniTable()
    for teacher in teachers.values():
        table_g = first_search(teacher=teacher, n_search=N_SEARCH)
        best_table = squeeze_tables(table_g, 1)
        unitable.register_seattable_to_unitable(best_table)
        
    unitable.exclude_overlapping(students)
    return unitable

def eliminate_charge_from_subject_csv():
    # from seat_solver.py
    """
    'data/students/subjects/{id}.csv' から列 charge を取り除く時に使用した
    """
    for i in range(1, 13):
        num = '00' + str(i) if len(str(i)) == 1 else '0' + str(i)
        with open(f'data/students/temp/{num}.csv', encoding='utf-8', mode='w', newline='') as e:
            writer = csv.writer(e)
            writer.writerow(['subject', 'num_of_lecture' ,'is_one_on_one'])
            with open(f'data/students/subjects/{num}.csv', encoding='utf-8') as f:
                f.readline()
                for subject_info in f:
                    subject_info = subject_info.rstrip('\n').split(',')
                    subject, num_of_lecture, is_one_on_one, _ = subject_info
                    writer.writerow([subject, num_of_lecture, is_one_on_one])


def exclude_overlapping(self, students):
    # from UniTable.py
    """
    同じ時限に登録されている生徒をキャンセルする。
    ---
    入力
        students {'001': Student, '002': Student}
    """
    canceled_stus = [] # 全時限見てからキャンセルされた生徒は ava_stu_dic に戻す

    for teaandkoma in self.unitable.values(): # 全時限見る
        order = self.decide_teacher_order(list(teaandkoma.keys())) # どの講師から見るかランダムで決める

        rgstred_stus = [] # この時限に登録されている生徒を記録, 既に記録済みの生徒がいたら重複
    
        for tea in order: # この時限の講師を順にみる
            koma = teaandkoma[tea] # 講師に紐づいたKoma
            stu_ids = koma.get_student_ids()
            if stu_ids == None:
                continue
            for id in stu_ids: # 1回か2回ループ
                if id in rgstred_stus:
                    if koma.state == 0:
                        print("これはいらないのでは")
                        continue
                    # 既にこの時限に登録済み。キャンセルする、left_lecs に戻す
                    # 授業両方キャンセルします。実装が楽だし、どうせ UniTable で再登録する処理を追加するので
                    elif koma.state in [1, 2, 3]:
                        lectures = koma.get_lectures()

                        # self.left_lecs に戻す
                        for id, lec in zip(stu_ids, lectures): # state==1か3 なら1回, state==2 なら2回ループ 
                            if id in self.left_lecs:
                                self.left_lecs[id].append(lec)
                            else:
                                self.left_lecs[id] = [lec]
                            canceled_stus.append(id)         
                        koma.delete_lecture() # コマの削除
                    else:
                        NotExpectedError
                else:
                    rgstred_stus.append(id)
    canceled_stus = list(set(canceled_stus)) # 重複排除
    self.re_register_students_to_ava_stu_dic(students, canceled_stus)

def register_seattable_to_unitable(self, seat_table):
    # from UniTable.py
    """
    SeatTable を 1つ登録する。
    ---
    入力
        SeatTable
    """
    self.register_table(seat_table)
    self.register_left_lecs(seat_table)
    self.register_ava_stu_dic(seat_table)
    self.ava_komas = list(self.ava_stu_dic.keys()) # 毎回呼ぶ必要ない 最後だけでいい
    random.shuffle(self.ava_komas)

def make_ava_stu_dic(self):
    # from Teacher.py
    """
    講師が出勤可能なコマと、そのコマに授業可能な生徒を格納した
    ava_stu_dic を作成する。

    ava_stu_dic: dict
    -----------
    Key: str
        講師が出勤可能なコマ。
        YYYY-MM-DD-J 形式

    Value: List of str
        そのコマに授業可能な生徒の名前。
        Student.name 形式
    """

    for teacher_d in self.schedule_ava:
        self.ava_stu_dic[teacher_d] = [] # 生徒がいなくても一旦空でKeyを登録
        for student in self.students:
            if teacher_d in student.schedule_ava:
                self.ava_stu_dic[teacher_d].append(student.id) # 生徒がいれば空のリストにappend

def register_subjects(student, subjects_path, teachers):
    # from seat_solver.py
    """
    subjects の情報を1行ずつ見て、studentとteacherにそれぞれ登録する。
    (同じ生徒でも、教科によって違う講師が担当する場合がある。)
    """ 
    with open(subjects_path, encoding='utf-8')as s:
        s.readline()
        for subject_info in s:
            subject_info = subject_info.rstrip('\n').split(',')
            subject, num_of_lecture, is_one_on_one, charge_teacher = subject_info
            subject_ = Subject(student.name, student.id, subject, int(num_of_lecture), int(is_one_on_one))
            student.register_subject(subject_)
        teachers[charge_teacher].register_subject(subject_)
        return student, teachers

def make_all_lecs(self):
    # from Teacher.py
    """
    講師が担当する教科と、その生徒の講習コマを格納した
    all_lecs を作成する。

    all_lecs: dict
    -----------
    Key: str
        講師が担当する全生徒の名前。
        Student.name 形式
        
    Value: Student.lectures (List of Lecture)
    """
    for subject in self.subjects:
        for _ in range(subject.num_of_lecture):
            stu_name = subject.student_name
            stu_id = subject.student_id
            lecture = Lecture(
                    student_name=stu_name,
                    student_id=stu_id,
                    subject=subject.subject,
                    is_one_on_one=subject.is_one_on_one)
            if stu_id in self.all_lecs.keys():
                self.all_lecs[stu_id].append(lecture)
            else:
                 self.all_lecs[stu_id] = [lecture]

def register_left_lecs(self, seat_table):
    # from UniTable.py
    """
    UniTable.left_lecs に SeatTable.left_lecs を登録する
    ---
    入力
        SeatTable
    """
    from_dic = seat_table.left_lecs
    to_dic = self.left_lecs

    for stu, lecs in from_dic.items():
        if stu in to_dic:
            to_dic[stu].extend(lecs) # リストにリストを結合
        else:
            to_dic[stu] = lecs

def register_ava_stu_dic(self, seat_table):
    # from UniTable.py
    """
    UniTable.ava_stu_dic に SeatTable.ava_stu_dic を登録する
    ---
    入力
        SeatTable
    """
    from_dic = seat_table.ava_stu_dic
    to_dic = self.ava_stu_dic

    for jigen, stus in from_dic.items():
        if jigen in to_dic:
            to_dic[jigen].extend(stus) # リストにリストを結合
            to_dic[jigen] = list(set(to_dic[jigen])) # 重複排除
        else:
            to_dic[jigen] = stus

def register_ava_tea_dic(self, teachers):
    # from UniTable.py
    """
    UniTable.ava_tea_dic を作成する
    ---
    入力
        teachers {'00001': Teacher, '00002': Teacher}
    """
    dic = self.ava_tea_dic
    for id, tea in teachers.items():
        for jigen in tea.schedule_ava():
            if jigen in dic:
                dic[jigen].append(id)
            else:
                dic[jigen] = [id]

def register_table(self, seat_table):
    # from UniTable.py
    """
    UniTable.unitable に SeatTable.table を登録する
    ---
    入力
        SeatTable
    """
    id = seat_table.teacher_id
    table = seat_table.table
    for jigen, koma in table.items():
        if jigen in self.unitable:
            self.unitable[jigen][id] = koma
        else:
            self.unitable[jigen] = {id : koma}

def register_subject(self, subject):
    # from Teacher.py
    """
    担当する講習コマを1科目ずつ登録。

    Parameters
    ----------
    subject : Subject
        Subject インスタンス。
    """
    self.subjects.append(subject)
    
def register_student(self, students):
    # from Teacher.py
    """
    担当する生徒をすべて登録。
    これに基づいて、探索用リストのときに集める生徒のスケジュールを決定する。
    """
    self.students = []
    student_ids = []
    for subject in self.subjects:
        if subject.student_id in student_ids:
            continue
        else:
            stu = students[subject.student_id]
            self.students.append(stu)
            student_ids.append(stu.id)

def register_dics_to_teacher(teachers, students):
    # from seat_solver.py
    """
    探索用のdict3つ
    - ava_stu_dic
    - all_lecs
    - table(旧 dic_to_trial)
    はすべてteacherに紐づけ、作成はTeacherクラスのメソッドにした。
    """
    for teacher in teachers.values():
        # Subject を1授業ずつに分解し、lectures リストに追加。all_lecs作成のために使う。
        teacher.register_student(students)

        # 探索用リストの作成。
        teacher.make_ava_stu_dic()
        teacher.make_all_lecs()
        teacher.make_table()

def make_table(self):
    # from Teacher.py
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



def choice_and_register_lec(jigen, seat_table, ava_stu):
    # from seat_solver.py
    """
    授業の登録処理を行う。
    具体的には、次のような操作を行う。
    
    -----------
    1. 生徒をランダム選択
    2. 授業をランダム選択
    3. 選んだ授業を SeatTable.table 内の jigen で指定された日時 に登録
    4. 登録した授業を SeatTable.left_lecs 内の 選択された生徒と結びついた授業 から削除
    5. 登録した生徒を ava_stu から削除
    """
    slcted_stu = random.choice(ava_stu) # 生徒ID がrandom.choice される
    slcted_lec = random.choice(seat_table.left_lecs[slcted_stu]) # Lecture インスタンスがrandom.choice される
    try:
        seat_table.table[jigen].register(slcted_lec) # Komaオブジェクトのクラスメソッドregisterの呼び出し
        seat_table.left_lecs[slcted_stu].remove(slcted_lec) # 登録したLectureをseat_table.left_lecs から削除
        ava_stu.remove(slcted_stu) # 登録した生徒をava_stu_から削除(1人の生徒が対2コマの両方に登録されるのを防ぐ)
        return seat_table, slcted_stu, ava_stu
    except CannotRegisterError:
        raise # CannotRegisterError をそのまま呼び出し元に送信




def register(seat_table):
    # from seat_solver.py
    """
    授業がcancelされたSeatTableに対して、再度授業を登録する。
    登録後、SeatTableはスコアを計算して返される。
    """
    
    for koma in seat_table.ava_komas: 
        ava_stu = seat_table.ava_stu_dic[koma]
        if len(ava_stu) == 0:
            continue
        state = seat_table.table[koma].state
        if state in [-1, 2, 3]:
            continue
        elif state == 1:
            # ------------------------
            # 授業2の登録ここから
            try:
                seat_table, slcted_stu, _ = choice_and_register_lec(koma, seat_table, ava_stu) # 登録
            except CannotRegisterError:
                continue
            if seat_table.is_all_lec_rgstred(slcted_stu): # ある生徒の授業が全登録されたか判定
                seat_table.remove_stu(slcted_stu)
            if seat_table.is_able_to_finish(): # 全生徒の授業が全登録されたか判定
                break
            # 授業2の登録ここまで
            # ------------------------
        elif state == 0:
            # ------------------------
            # 授業1の登録ここから
            seat_table, slcted_stu, ava_stu = choice_and_register_lec(koma, seat_table, ava_stu) # 登録
            if seat_table.is_all_lec_rgstred(slcted_stu): # ある生徒の授業が全登録されたか判定
                seat_table.remove_stu(slcted_stu)
            if seat_table.is_able_to_finish(): # 全生徒の授業が全登録されたか判定
                break
            # 授業1の登録ここまで
            # ------------------------

            if is_katakoma(seat_table.table, koma) and is_there_anyone(ava_stu): # (片コマ) and (受講可能な生徒が他にもいる)
                # ------------------------
                # 授業2の登録ここから
                try:
                    seat_table, slcted_stu, _ = choice_and_register_lec(koma, seat_table, ava_stu) # 登録
                except CannotRegisterError:
                    continue
                if seat_table.is_all_lec_rgstred(slcted_stu): # ある生徒の授業が全登録されたか判定
                    seat_table.remove_stu(slcted_stu)
                if seat_table.is_able_to_finish(): # 全生徒の授業が全登録されたか判定
                    break
                # 授業2の登録ここまで
                # ------------------------
    seat_table.calculate_score()
    return seat_table

def first_search(teacher, n_search=1000):
    # from seat_solver.py
    """
    一回目の探索を行う。
    """
    tables = []
    for i in tqdm(range(n_search)):
        seat_table = SeatTable(teacher.name, teacher.id, teacher.table, teacher.all_lecs, teacher.ava_stu_dic)
        seat_table = register(seat_table)
        tables.append(seat_table)
    return tables

def step_generation(tables, students, n_cancel=2, n_resolve=10, n_keeptable=50):
    # from seat_solver.py
    """
    世代を1つ進める。

    <開発用環境>
    seat_k = [50] + [50 x 2]
        前世代のスコア上位50テーブルをそのまま保存(50)
        加えてスコア上位50テーブルに対して、それぞれ2通りずつcancelを行う(50 x 2)
        合計150テーブルを保持し、これを再登録・判定の対象とする
    seat_g = [1500] = [150 x 10]
        seat_k の150テーブルに対して、それぞれ10通りずつre_registerを行う(150 x 10)
        合計1500テーブルを保持し、次の世代に渡す

    <本番用環境>
    seat_k = [550] = [50]+ [50 x 10]
        前世代のスコア上位50テーブルをそのまま保存(50)
        加えてスコア上位50テーブルに対して、それぞれ10通りずつcancelを行う(50 x 10)
        合計550テーブルを保持し、これを再登録・判定の対象とする
    seat_g = [11000] = [550 x 20]
        seat_k の550テーブルに対して、それぞれ20通りずつre_registerを行う(550 x 20)
        合計11000テーブルを保持し、次の世代に渡す
    """

    # tableをスコア順に並べ替えて、上位 n_keeptable 個に厳選
    good_tables = squeeze_tables(tables, n_keeptable)

    resolved_tables = []
    for seat_table in tqdm(good_tables):
        
        # score をリセット
        seat_table.reset_score()
        
        # cancel せずに resolve
        resolved_tables.append(register(copy.deepcopy(seat_table)))

        # cancel してから resolve
        for i in range(n_cancel): # n_cancel 通りキャンセル
            seat_table_i = copy.deepcopy(seat_table)
            seat_table_i.cancel_lecs(students)
            for j in range(n_resolve): # n_resolve 通り再登録
                seat_table_j = copy.deepcopy(seat_table_i)
                seat_table_j = register(seat_table_j)
                resolved_tables.append(seat_table_j)
    return resolved_tables


def process_generation(teacher, students, N_SEARCH, N_GENERATIONS, N_CANCEL, N_RESOLVE, N_KEEPTABLE):
    # from seat_solver.py
    """
    講師1人にのみ対応している遺伝的処理。

    呼び出し方
        process_generation(teachers['00001'], students, N_SEARCH, N_GENERATIONS, N_CANCEL, N_RESOLVE, N_KEEPTABLE)
        を main() の中に置く。
    """
    # 1st search
    print(f"\n\t===1st generation===")
    
    table_g = first_search(teacher=teacher, n_search=N_SEARCH)
    best_table = squeeze_tables(table_g, 1)
    print_seat_table(best_table)

    # Search loop after 1st search    
    for search_counter in range(N_GENERATIONS-1):
        print(f"\n\t==={search_counter+2}-th generation===")
        table_g = step_generation(table_g, students, N_CANCEL, N_RESOLVE, N_KEEPTABLE)
        best_table = squeeze_tables(table_g, 1)
        print_seat_table(best_table)

def register_seattable_to_unitable(teachers, students, N_SEARCH):
    # from seat_solver.py
    """
    seat_table を一旦探索して、遺伝的処理にかけずにunitable に登録する
    """
    unitable = UniTable()
    for teacher in teachers.values():
        unitable.register_teacher_to_unitable(teacher)
        
    unitable.exclude_overlapping(students)
    return unitable

def decide_teacher_order(self, teacher_list):
    # from UniTable.py
    """
    exclude_overlapping() の中で、どの講師から見るかをランダムで決めるときのメソッド
    ---
    入力
        teacher_list ['00001', '00002']
    """
    random.shuffle(teacher_list)
    return teacher_list

def print_seat_table(seat_table, detail=True):
    # from utils.py
    """
    SeatTable のprint用関数。
    """
    for item in seat_table.table:
        print('date: ', item, 'state: ', seat_table.table[item].state, 'lecture_1: ', seat_table.table[item].lecture_1, 'lecture_2: ', seat_table.table[item].lecture_2)
    if detail:
        print(f'スコア: {seat_table.score:.3f}')
        print(f'片コマ率: {seat_table.calculate_katakoma_rate() * 100:.3f}%')
        print(f'登録済み授業数：{seat_table.count_rgstred_lecs()}')
        print(f'未登録授業数：{seat_table.count_left_lecs()}')
        print(f"授業間隔日数の最小値の合計: {seat_table.calc_min_lec_day_interval()}")
        print(f"同日授業間隔時限の最大値の合計: {seat_table.calc_max_lec_inday_interval()}")


def print_left_lecs(seat_table):
    # from utils.py
    """
    seat_table.left_lecs のprint用関数。
    """
    for item in seat_table.left_lecs:
        print('stu_name: ', item, 'list_of_lec: ', [str(i) for i in seat_table.left_lecs[item]])


def print_ava_stu_dic(seat_table):
    # from utils.py
    """
    seat_table.ava_stu_dic のprint用関数。
    """
    for item in seat_table.ava_stu_dic:
        print('date: ', item, 'list_of_stu: ', seat_table.ava_stu_dic[item])