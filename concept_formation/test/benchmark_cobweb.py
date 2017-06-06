from random import randint
from timeit import timeit

from matplotlib import pyplot as plt
import matplotlib.patches as mpatches


def generate_dt_dataset(n_inst, n_attr, n_val):
    y = []
    x = []
    for i in range(n_inst):
        i = []
        for j in range(n_attr):
            if j == 0:
                y.append(randint(1, n_val))
            else:
                i.append(randint(1, n_val))
        x.append(i)
    return x, y


def generate_dataset(n_inst, n_attr, n_val):
    instances = []
    for i in range(n_inst):
        i = {}
        for j in range(n_attr):
            i[str(j)] = randint(1, n_val)
        instances.append(i)
    return instances


def time_dt(n_inst, n_attr, n_val):
    return timeit('[tree.fit(x[0:i+1], y[0:i+1]) for i in range(len(x))]',
                  setup=('from __main__ import generate_dt_dataset; '
                         'from sklearn.tree import DecisionTreeClassifier; '
                         'tree = DecisionTreeClassifier(); '
                         'x, y = generate_dt_dataset(%i, %i, %i)' % (n_inst,
                                                                     n_attr,
                                                                     n_val)),
                  number=1)


def time(n_inst, n_attr, n_val):
    return timeit('tree.fit(x)',
                  setup=('from __main__ import generate_dataset; '
                         'from concept_formation.cobweb import CobwebTree; '
                         'tree = CobwebTree(); '
                         'x = generate_dataset(%i, %i, %i)' % (n_inst, n_attr,
                                                               n_val)),
                  number=1)


if __name__ == "__main__":
    # 5 attributes
    sizes = [10, 30, 60, 120, 180, 220]
    times = [time(i, 5, 5) for i in sizes]
    plt.plot(sizes, times, 'ro')
    plt.plot(sizes, times, 'r-')

    # 10 attributes
    times = [time(i, 10, 5) for i in sizes]
    plt.plot(sizes, times, 'bo')
    plt.plot(sizes, times, 'b-')

    # 20 attributes
    times = [time(i, 10, 5) for i in sizes]
    plt.plot(sizes, times, 'go')
    plt.plot(sizes, times, 'g-')

    red_patch = mpatches.Patch(color='red', label='# attr=5')
    blue_patch = mpatches.Patch(color='blue', label='# attr=10')
    green_patch = mpatches.Patch(color='green', label='# attr=20')
    plt.legend(handles=[red_patch, blue_patch, green_patch], loc=2)

    plt.xlabel('Number of training instances (5 possible values / attr)')
    plt.ylabel('Runtime in Seconds')
    plt.show()