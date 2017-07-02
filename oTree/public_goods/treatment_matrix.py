import itertools
import random



def get_treatment_matrix():
    treatments = ['Bel', 'Act', 'Ctrl', 'No',]
    def by_letters(a, b):
        u = zip(a, b)
        for i, j in u:
            if i == j:
                return True
        return False

        x = [i for i in a if not by_letters(i, what)]
        return x
    def filtered(what):
        x = [i for i in a if not by_letters(i, what)]
        return x
    def triple(str):
        return [str, str, str]

    initial_data = list(itertools.permutations(treatments))
    result = None
    while result is None:
        try:
            matrices = []
            a = initial_data
            for i in range(4):
                print('cycle:: ', i)
                line1 = random.choice(a)
                line2 = random.choice(filtered(line1))
                s1 = set(filtered(line1))
                s2 = set(filtered(line2))
                sets = [s1, s2]
                line3 = random.choice(list(set.intersection(*sets)))
                s3 = set(filtered(line3))
                sets = [s1, s2, s3]
                line4 = random.choice(list(set.intersection(*sets)))
                matrix1 = [line1, line2, line3, line4]
                matrices.append(matrix1)
                a = list(itertools.filterfalse(lambda x: x in matrix1, a))
            result = matrices

        except IndexError:
            pass
    result = [[x for x in j for i in range(3)] for i in  matrices for j in i]
    return result