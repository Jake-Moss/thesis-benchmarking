import time
import tracemalloc
import memray

def foo(i):
    a = list(range(10 * 2 * i))
    return a

snapshots = []
for i in range(10):
    foo(i)
    snapshots.append(memory_usage((foo, (i,)), backend="tracemalloc"))


# lens = [len(snap) for snap in snapshots]
# print(lens)
# print(*snapshots[0], sep="\n")
# print("-" * 50)
# print(*snapshots[-1], sep="\n")
