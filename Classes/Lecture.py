class Lecture:
    """
    1コマを表すクラス。

    Attributes
    ----------
    student_name : str
        このコマを受講する生徒名。
    student_id : str
        このコマを受講する生徒ID。
    subject : str
        科目名。(e.g. "English", "Math"
    is_one_on_one : bool
        対1か対2か。
    """

    def __init__(self, student_name, student_id, subject, is_one_on_one):
        """
        Parameters
        ----------
        student_name : str
            このコマを受講する生徒名。
        student_id : str
            このコマを受講する生徒ID。
        subject : str
            科目名。(e.g. "English", "Math"
        is_one_on_one : bool
            対1か対2か。
        """
        self.student_name = student_name
        self.student_id = student_id
        self.subject = subject
        self.is_one_on_one = is_one_on_one

    def __str__(self):
        return self.student_name + "-" + self.subject
