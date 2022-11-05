from datetime import date
import pickle
from pprint import pprint
from Classes.Koma import Koma
from Classes.Day import Day


def is_katakoma(i_dic_to_trial, koma):
    """
    同じ日かを判定する。

    Parameters
    ----------
     i_dic_to_trial : dict
     koma : str
        YYYY-MM-DD-J 形式
    """
    if i_dic_to_trial[koma].state == 1:
        return True
    else:
        return False


def is_there_anyone(ava_stu):
    """
    他にも受講可能な生徒がいるかを判定する。
    授業が入っていないコマに対2のコマを1つ登録したときに呼び出される。
    register() の最初にも呼び出される

    Parameters
    ----------
    ava_stu : list of str
        要素は生徒名
    """
    if len(ava_stu) >= 1:
        return True
    else:
        return False


def dump_combi_spec():
    """
    data/students/combi_spec.csv に登録されている 特定の組み合わせをリストに変換し、保存しておく。

    Generated object
    ----------
    combi_spec_list : list of dict
        {'combi': [stu_1_id, stu_2_id], 'weight': int(weight)} <--- これを要素として持つリスト
    """
    with open('data/students/combi_spec.csv', encoding='utf-8') as f:
        f.readline() # 最初の行は読み飛ばす。
        combi_spec_list = []
        for line in f:
            combi_info = line.rstrip('\n').split(',')
            stu_1_id, stu_2_id, weight = combi_info
            combi_spec_list.append({'combi': [stu_1_id, stu_2_id], 'weight': int(weight)})
        with open('objects/combi_spec.pickle',mode='wb') as p:
            pickle.dump(combi_spec_list, p)

def dump_existing_charge():
    """
    data/existing_charge.csv に登録されている 既存の担当講師についての情報をリストに変換し、保存しておく。
    
    Generated object
    ----------
    existing_charge_list : list of dict
        {'teacher': tea_id, 'student': stu_id, 'subject': str, 'weight': int} <--- これを要素として持つリスト
    """
    with open('data/existing_charge.csv', encoding='utf-8') as f:
        f.readline() # 最初の行は読み飛ばす。
        existing_charge_list = []
        for line in f:
            charge_info = line.rstrip('\n').split(',')
            tea_id, stu_id, subject, weight = charge_info
            existing_charge_list.append({'teacher': tea_id, 'student': stu_id, 'subject': subject, 'weight': int(weight)})
        with open('objects/existing_charge.pickle',mode='wb') as p:
            pickle.dump(existing_charge_list, p)


def decide_constants(development_flag=1):
    """
    定数を決定する。
    """
    if development_flag:
        N_SEARCH = 1000
        N_CANCEL = 2
        N_RESOLVE = 10
        N_KEEPTABLE = 50
        N_GENERATIONS = 10
    else:
        N_SEARCH = 10000
        N_CANCEL = 10
        N_RESOLVE = 20
        N_KEEPTABLE = 50
        N_GENERATIONS = 5
    return N_SEARCH, N_CANCEL, N_RESOLVE, N_KEEPTABLE, N_GENERATIONS


def print_unitable(unitable, detail=True):
    """
    UniTable のprint用関数。
    """
    print(f"\n\t===unitable.table===")
    di = unitable.make_print_dic()
    #pprint(di)
    # print(f"\n\t===unitable.left_lecs===")
    # pprint(unitable.left_lecs)
    # print(f"\n\t===unitable.ava_stu_dic===")
    # pprint(unitable.ava_stu_dic)
    if detail:
        print(f'スコア: {unitable.score:.3f}')
        print(f'片コマ率: {unitable.calculate_katakoma_rate() * 100:.3f}%')
        print(f'登録済み授業数：{unitable.count_rgstred_lecs()}')
        print(f'未登録授業数：{unitable.count_left_lecs()}')
        print(f"授業間隔日数の最小値の合計: {unitable.calc_min_lec_day_interval()}")
        print(f"同日授業間隔時限の最大値の合計: {unitable.calc_max_lec_inday_interval()}")

def squeeze_tables(tables, n_keeptable):
    """
    tablesのリストをとり、スコア上位に絞りこむ。
    n_keeptable = 1 のとき、best_table を返す。
    """
    if n_keeptable == 1:
        best_table = sorted(tables, key=lambda i: i.score, reverse=True)[0]
        return best_table
    else:
        good_tables = sorted(tables, key=lambda i: i.score, reverse=True)[:n_keeptable]
        return good_tables


def init_koma_from_jigen(jigen):
    """"
    input: jigen(YYYY-MM-DD-J)
    output: initialized Koma
    """
    d_info = jigen.split('-')
    d_info = [int(i) for i in d_info]
    day = Day(year=d_info[0], month=d_info[1], day=d_info[2], koma=None) # koma は入れた方がいい?
    jigen = d_info[3]
    koma = Koma(day=day, jigen=jigen, state=0)
    return koma