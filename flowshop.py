import random
from matplotlib import pyplot as plt

NB_SOL = 100  #1000
NB_GEN = 100  #750
NB_BEST_SOL = 10  #100
NB_OF_OBJECTS = 200

instance = []
with open("instance.csv", "r") as f:
    for j, line in enumerate(f.readlines()):
        line_list = line.split(",")
        for i in range(len(line_list)):
            line_list[i] = int(line_list[i].strip())
        line_list.insert(0, j)
        instance.append(line_list)


instance = instance[:NB_OF_OBJECTS]

def generate_random_permutation(instance):
    #return random.sample(instance, len(instance))
    instance.sort(key=lambda x: (-x[1], x[2]))
    chunk_size = 10

    # Divide the instance into chunks and shuffle each chunk
    chunks = [instance[i:i + chunk_size] for i in range(0, len(instance), chunk_size)]
    for chunk in chunks:
        random.shuffle(chunk)

    # Flatten the list of chunks to get the new instance
    instance = [job for chunk in chunks for job in chunk]
    return instance


def calculate_make_span(instance):
    end_times = [[0 for _ in range(10)] for _ in range(len(instance))]
    for i, job in enumerate(instance):
        job = job[3:]
        for machine_nb, machine in enumerate(job):
            if machine_nb == 0:
                if i == 0:
                    end_times[i][machine_nb] = job[machine_nb]
                else:
                    end_times[i][machine_nb] = job[machine_nb] + end_times[i - 1][machine_nb]
            else:
                if i == 0:
                    end_times[i][machine_nb] = job[machine_nb] + end_times[i][machine_nb - 1]
                else:
                    end_times[i][machine_nb] = job[machine_nb] + max(end_times[i][machine_nb - 1],
                                                                     end_times[i - 1][machine_nb])
    return end_times


def calculate_total_weighted_tardiness(instance, end_times):
    total = 0
    for i, job in enumerate(instance):
        total += max(0, (end_times[i][-1] - job[2]) * job[1])
    return total


def fitness(instance, w):
    end_times = calculate_make_span(instance)
    make_span = end_times[-1][-1]
    total_weighted_tardiness = calculate_total_weighted_tardiness(instance, end_times)
    fit = w * make_span + (1 - w) * total_weighted_tardiness
    return fit


def is_pareto_optimal(s1, s2):
    end_times_s1 = calculate_make_span(s1)
    make_span_s1 = end_times_s1[-1][-1]
    total_weighted_tardiness_s1 = calculate_total_weighted_tardiness(s1, end_times_s1)
    end_times_s2 = calculate_make_span(s2)
    make_span_s2 = end_times_s2[-1][-1]
    total_weighted_tardiness_s2 = calculate_total_weighted_tardiness(s2, end_times_s2)

    if make_span_s2 < make_span_s1 and total_weighted_tardiness_s2 < total_weighted_tardiness_s1:
        return True                     # s2 is better than s1 in both criteria
    return False


weights = [i/7 for i in range(7)]
weights.pop(0)
weights = [0.5]
saved_paretos = []

for w in weights:
    solutions = [generate_random_permutation(instance) for _ in range(NB_SOL)]
    pareto_optimal_solutions = []
    graph = []
    print("=== Weight: ", w, " ===")
    for i in range(NB_GEN):
        ranked_solutions = sorted([(fitness(s, w), s) for s in solutions], reverse=False)
        if i % 50 == 0:
            print(f"=== Generation {i} ===")
        print(f"=== Generation {i} meilleure solution ===")
        print(ranked_solutions[0])
        best_solutions = ranked_solutions[:NB_BEST_SOL]
        # Make crossover
        new_generation = []
        for _ in range(NB_SOL):
            parent1 = random.choice(best_solutions)[1]
            parent2 = random.choice(best_solutions)[1]
            child = []
            for j in range(len(parent1)//2):
                child.append(parent1[j])
            for element in parent2:
                if element not in child:
                    child.append(element)
            for i in range(5):
                random_index = random.randint(0, NB_OF_OBJECTS - 2)
                child[random_index], child[random_index + 1] = child[random_index + 1], child[random_index]
            new_generation.append(child)
        solutions = new_generation
    # Keep only pareto optimal solutions
    for i, s1 in enumerate(solutions):
        is_pareto = True
        for j, s2 in enumerate(solutions):
            if i != j and is_pareto_optimal(s1, s2):
                is_pareto = False
                break
        if is_pareto:
            end_times_s1 = calculate_make_span(s1)
            make_span_s1 = end_times_s1[-1][-1]
            total_weighted_tardiness_s1 = calculate_total_weighted_tardiness(s1, end_times_s1)
            pareto_optimal_solutions.append(s1)
            #graph.append((make_span_s1, total_weighted_tardiness_s1))

    #make_span_values = [s[0] for s in graph]
    #twt_values = [s[1] for s in graph]
#
    #plt.scatter(twt_values, make_span_values)
    #plt.title(f"Pareto Optimal Solutions with weight {w}")
    #plt.xlabel("Total Weighted Tardiness")
    #plt.ylabel("Make Span")
#
    #plt.show()
    saved_paretos.extend(pareto_optimal_solutions)

updated_paretos = []
i = 0
for s1 in saved_paretos:
    is_pareto = True
    j = 0
    for s2 in saved_paretos:
        if i != j and is_pareto_optimal(s1, s2):
            is_pareto = False
            break
        j += 1
    if is_pareto:
        end_times_s1 = calculate_make_span(s1)
        make_span_s1 = end_times_s1[-1][-1]
        total_weighted_tardiness_s1 = calculate_total_weighted_tardiness(s1, end_times_s1)
        updated_paretos.append((make_span_s1, total_weighted_tardiness_s1, s1))
    i += 1
saved_paretos = updated_paretos



make_span_values = [s[0] for s in saved_paretos]
twt_values = [s[1] for s in saved_paretos]

plt.scatter(twt_values, make_span_values)
plt.title("Pareto Optimal Solutions")
plt.xlabel("Total Weighted Tardiness")
plt.ylabel("Make Span")

plt.show()

# Write the pareto optimal solutions to a csv file, only keeping the job ids, separated by commas, one solution per line
with open("DesoilTheo_JauffretOscar.csv", "w") as f:
    for s in saved_paretos:
        f.write(",".join([str(job[0]) for job in s[2]]) + "\n")
