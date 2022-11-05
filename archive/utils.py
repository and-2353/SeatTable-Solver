from datetime import date

def is_same_day(day1, day2):
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


def convert_datestr_to_date(datestr :str):
    # YYYY-MM-DD-[1~8] を , dateにする
    s_ = [int(i) for i in datestr.split('-')]
    #print(s_)
    return date(s_[0], s_[1], s_[2])
