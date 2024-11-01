import matplotlib.pyplot as plt
from matplotlib import colormaps
import seaborn as sns
import itertools


sns.set_theme("notebook", font_scale=1, rc={
    'figure.figsize': (8, 6),
    "text.usetex": True,
    "text.latex.preamble": r"\usepackage{libertine}",
})


with open("small_int_benchmark.txt") as f:
    flint_timings = []
    gmp_timings = []
    flint_timings_vec = []
    gmp_timings_vec = []

    for (a, b, c, d) in itertools.batched((eval(x) for x in f.read().split("\n") if x), 4):
        flint_timings.append(a)
        gmp_timings.append(b)
        flint_timings_vec.append(c)
        gmp_timings_vec.append(d)

    n = len(flint_timings)
    flint_timings = [sum(x) / n for x in zip(*flint_timings)]
    gmp_timings = [sum(x) / n for x in zip(*gmp_timings)]
    flint_timings_vec = [sum(x) / n for x in zip(*flint_timings_vec)]
    gmp_timings_vec = [sum(x) / n for x in zip(*gmp_timings_vec)]

with open("small_int_benchmark_cython.txt") as f:
    cython_timings = []
    cython_timings_vec = []

    for (a, b) in itertools.batched((eval(x) for x in f.read().split("\n") if x), 2):
        cython_timings.append(a)
        cython_timings_vec.append(b)

    n = len(cython_timings)
    cython_timings = [sum(x) / n for x in zip(*cython_timings)]
    cython_timings_vec = [sum(x) / n for x in zip(*cython_timings_vec)]

x = list(range(1, len(flint_timings) + 1))

f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
sns.lineplot(x=x, y=gmp_timings, ax=ax2, label="GMP")
sns.lineplot(x=x, y=flint_timings, ax=ax2, label="FLINT")
sns.lineplot(x=x, y=cython_timings, ax=ax2, label="Python")
sns.lineplot(x=x, y=gmp_timings_vec, ax=ax1, label="GMP vector[1000]")
sns.lineplot(x=x, y=flint_timings_vec, ax=ax1, label="FLINT vector[1000]")
sns.lineplot(x=x, y=cython_timings_vec, ax=ax1, label="Python vector[1000]")
ax1.set_yscale('log')
ax2.set_yscale('log')
f.supxlabel('Number of multiplications by 2')
f.supylabel('Reference cycles')
f.suptitle('Reference cycles to execute repeated multiplications by 2')
plt.tight_layout()
plt.savefig('images/small_int_benchmark.pdf', dpi=300, bbox_inches='tight')
plt.show()

n = 62 * 2
f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
sns.lineplot(x=x[:n], y=gmp_timings[:n], ax=ax2, label="GMP")
sns.lineplot(x=x[:n], y=flint_timings[:n], ax=ax2, label="FLINT")
sns.lineplot(x=x[:n], y=cython_timings[:n], ax=ax2, label="Python")
sns.lineplot(x=x[:n], y=gmp_timings_vec[:n], ax=ax1, label="GMP vector[1000]")
sns.lineplot(x=x[:n], y=flint_timings_vec[:n], ax=ax1, label="FLINT vector[1000]")
sns.lineplot(x=x[:n], y=cython_timings_vec[:n], ax=ax1, label="Python vector[1000]")
ax1.set_yscale('log')
ax2.set_yscale('log')
f.supxlabel('Number of multiplications by 2')
f.supylabel('Reference cycles')
f.suptitle('Reference cycles to execute repeated multiplications by 2')
sns.move_legend(ax1, "upper right")
sns.move_legend(ax2, "upper right")
plt.tight_layout()
plt.savefig('images/small_int_benchmark_focused.pdf', dpi=300, bbox_inches='tight')
plt.show()


# f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
# sns.lineplot(x=x, y=[x / y for x, y in zip(flint_timings, gmp_timings)], ax=ax2, label="FLINT / GMP")
# sns.lineplot(x=x, y=[x / y for x, y in zip(flint_timings_vec, gmp_timings_vec)], ax=ax1, label="FLINT / GMP vector[1000]")
# f.supxlabel('Number of multiplications by 2')
# f.supylabel('Ratio of reference cycles')
# f.suptitle('Ratio of reference cycles to execute repeated multiplications by 2')
# plt.tight_layout()
# plt.savefig('images/small_int_benchmark_ratio.pdf', dpi=300, bbox_inches='tight')
# plt.show()

# f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
# sns.lineplot(x=x[:n], y=[x / y for x, y in zip(flint_timings[:n], gmp_timings[:n])], ax=ax2, label="FLINT / GMP")
# sns.lineplot(x=x[:n], y=[x / y for x, y in zip(flint_timings_vec[:n], gmp_timings_vec[:])], ax=ax1, label="FLINT / GMP vector[1000]")
# f.supxlabel('Number of multiplications by 2')
# f.supylabel('Ratio of reference cycles')
# f.suptitle('Ratio of reference cycles to execute repeated multiplications by 2')
# plt.tight_layout()
# plt.savefig('images/small_int_benchmark_ratio_focused.pdf', dpi=300, bbox_inches='tight')
# plt.show()

f, (ax1, ax2) = plt.subplots(2, 1, sharex=False)
sns.lineplot(x=x, y=[x / y for x, y in zip(gmp_timings_vec, flint_timings_vec)], ax=ax1, label="GMP / FLINT vector[1000]")
sns.lineplot(x=x, y=[x / y for x, y in zip(cython_timings_vec, flint_timings_vec)], ax=ax1, label="Python / FLIN vector[1000]")
sns.lineplot(x=x[:n], y=[x / y for x, y in zip(gmp_timings_vec[:n], flint_timings_vec[:])], ax=ax2, label="GMP / FLINT vector[1000]")
sns.lineplot(x=x[:n], y=[x / y for x, y in zip(cython_timings_vec[:n], flint_timings_vec[:])], ax=ax2, label="Python / FLINT vector[1000]")
f.supxlabel('Number of multiplications by 2')
f.supylabel('Ratio of reference cycles')
f.suptitle('Ratio of reference cycles to execute repeated multiplications by 2')
plt.tight_layout()
plt.savefig('images/small_int_benchmark_ratio.pdf', dpi=300, bbox_inches='tight')
plt.show()


f, (ax1, ax2) = plt.subplots(2, 1, sharex=False)
sns.lineplot(x=x, y=gmp_timings_vec, ax=ax1, label="GMP vector[1000]")
sns.lineplot(x=x, y=flint_timings_vec, ax=ax1, label="FLINT vector[1000]")
sns.lineplot(x=x, y=cython_timings_vec, ax=ax1, label="Python vector[1000]")
sns.lineplot(x=x[:n], y=gmp_timings_vec[:n], ax=ax2, label="GMP vector[1000]")
sns.lineplot(x=x[:n], y=flint_timings_vec[:n], ax=ax2, label="FLINT vector[1000]")
sns.lineplot(x=x[:n], y=cython_timings_vec[:n], ax=ax2, label="Python vector[1000]")
ax1.set_yscale('log')
ax2.set_yscale('log')
f.supxlabel('Number of multiplications by 2')
f.supylabel('Reference cycles')
f.suptitle('Reference cycles to execute repeated multiplications by 2')

ax2.get_legend().remove()
plt.tight_layout()
plt.savefig('images/small_int_benchmark_combined.pdf', dpi=300, bbox_inches='tight')
plt.show()
