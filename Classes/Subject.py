class Subject:
    """
    複数コマある1つの科目をまとめて表現する。

    Attributes
    ----------
    student_name : str
        生徒名。 
    student_id : str
        生徒ID。
    subject : str
        科目名。
    num_of_lecture : int
        コマ数。
    is_one_on_one : bool
        対1か対2か。
    """

    def __init__(self, student_name, student_id, subject, num_of_lecture, is_one_on_one):
        """
        Parameters
        ----------
        student_name : str
            生徒名。
        student_id : str
            生徒ID。
        subject : str
            科目名。"English" や "Math"。
        num_of_lecture : int
            コマ数。
        is_one_on_one : bool
            対1か対2か。
        """
        self.student_name = student_name
        self.student_id = student_id
        self.subject = subject
        self.num_of_lecture = num_of_lecture
        self.is_one_on_one = is_one_on_one
