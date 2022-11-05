from datetime import date, timedelta
import random
from pprint import pprint
from tqdm import tqdm


from Classes.Day import Day
from Classes.Teacher import Teacher
from Classes.Student import Student
from Classes.Subject import Subject
from Classes.Koma import Koma
from utils import *


# 講習期間の登録。
start_day = date(2021, 7, 1)
end_day = date(2021, 8, 31)


# 講師登録。
teacher = Teacher(name="廣瀬")
# 講師のスケジュールの登録。csvファイル読み込み。
teacher.set_schedule_from_csv(r"schedules/teacher_hirose.csv")


# 生徒の登録。
students = []

student_mao = Student(name="増田")
student_mao.set_schedule_from_csv(csv_path=r"schedules/student_mao.csv")
student_mao.set_subjects(subjects=[
        Subject(subject="英", num_of_lecture=8, is_one_on_one=False),
        Subject(subject="数", num_of_lecture=12, is_one_on_one=False)])
student_mao.set_lectures()
students.append(student_mao)

student_yuuna = Student(name="小川")
student_yuuna.set_schedule_from_csv(csv_path=r"schedules/student_yuuna.csv")
student_yuuna.set_subjects(subjects=[
        Subject(subject="英", num_of_lecture=10, is_one_on_one=False),
        Subject(subject="数", num_of_lecture=16, is_one_on_one=False)])
student_yuuna.set_lectures()
students.append(student_yuuna)


# 座席表の作成。
seat_table = []
for d in range((end_day-start_day).days + 1):
    seat_day = []
    for jigen in range(1, 9):
        koma = Koma(day=start_day+timedelta(d), jigen=jigen, state=-1)
        seat_day.append(koma)
    seat_table.append(Day(ymd=start_day+timedelta(d), koma=seat_day))


teacher_available_koma_list = {}

# 講師のシフトを座席表に反映させる。
for teacher_d in teacher.schedule:
    for seat_d in seat_table:
        if is_same_day(teacher_d, seat_d):
            available_in_day = []
            available_flag = 0
            for jigen in range(8):
                if teacher_d.koma[jigen] == 1:
                    seat_d.koma[jigen].state = 0
                    available_flag = 1
                    available_in_day.append(jigen + 1)
            if available_flag:
                teacher_available_koma_list[teacher_d] = available_in_day

#print(teacher_available_koma_list, len(teacher_available_koma_list))


available_komas = {}
def register(date, jigen: int, student_name: str):
    koma = str(date) + '-' + str(jigen)
    if koma in available_komas:
        available_komas[koma].append(student_name)
    else:
        available_komas[koma] = [student_name]


# 生徒のシフトを講師アベイラブルリストに反映させる。
for teacher_day in teacher_available_koma_list:
    for student in students:
        listofday = student.schedule
        for student_day in listofday:
            if is_same_day(teacher_day, student_day):
                for jigen in teacher_available_koma_list[teacher_day]:
                    if student_day.koma[jigen - 1] == 1:
                        register(teacher_day.date, jigen, student.name)

#pprint(available_komas)

"""
print("座席表")
display_seat_table(seat_table)
"""



n = 1
for i in range(n):
    keys = list(available_komas.keys())
    lecture_list = {}
    for student in students:
        lecture_list[student.name] = student.lectures
    #pprint(lecture_list)
    random.shuffle(keys)
    for item in keys:
        available_students = available_komas[item]
        student = random.choice(available_students)
        lecture = random.choice(lecture_list[student])
        # seat_tableの中からそのdayを持ってくる
        # その後、dayが持っているkomaオブジェクトのlecture_1に追加, 状態もなんか変える(たぶん)
        # seat_table はDay インスタンスのリスト
        d = convert_datestr_to_date(item)
        print(d)









