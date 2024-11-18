#I want to aggregate the results of solutions1 and solutions2 and only keep
#the pareto optimal solutions. I will then write the results to a csv file.
#I will use the is_pareto_optimal function from flowshop.py to determine if a solution is pareto optimal.
#I will use the calculate_make_span and calculate_total_weighted_tardiness functions from flowshop.py to calculate the make span and total weighted tardiness of a solution.
#I will use the following code to aggregate the results:
from matplotlib import pyplot as plt
# Read the results from solutions1
results1 = []
with open("solutions1.csv", "r") as f:
    for line in f:
        job_ids = [int(job_id) for job_id in line.strip().split(",")]
        results1.append(job_ids)

# Read the results from solutions2
results2 = []
with open("solutions2.csv", "r") as f:
    for line in f:
        job_ids = [int(job_id) for job_id in line.strip().split(",")]
        results2.append(job_ids)

# Combine the results
all_results = results1 + results2

# I need to add the data from instance.csv containing the processing times of the jobs
processing_times = {}
with open("instance.csv", "r") as f:
    for i, line in enumerate(f.readlines()):
        job_id = i
        processing_time = line.strip().split(",")
        for j, char in enumerate(processing_time):
            processing_time[j] = int(char)
        processing_times[int(job_id)] = processing_time


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


# add the processing times to the results
for result in all_results:
    for i, job_id in enumerate(result):
        result[i] = [job_id]
        result[i].extend(processing_times[job_id])

make_span_values = [s[0] for s in all_results]
twt_values = [s[1] for s in all_results]

plt.scatter(twt_values, make_span_values)
plt.title("Pareto Optimal Solutions")
plt.xlabel("Total Weighted Tardiness")
plt.ylabel("Make Span")

plt.show()

# Keep only pareto optimal solutions
pareto_optimal_solutions = []


for s1 in all_results:
    is_pareto = True
    j = 0
    for s2 in all_results:
        if i != j and is_pareto_optimal(s1, s2):
            is_pareto = False
            break
        j += 1
    if is_pareto:
        end_times_s1 = calculate_make_span(s1)
        make_span_s1 = end_times_s1[-1][-1]
        total_weighted_tardiness_s1 = calculate_total_weighted_tardiness(s1, end_times_s1)
        pareto_optimal_solutions.append((make_span_s1, total_weighted_tardiness_s1, s1))
    i += 1


make_span_values = [s[0] for s in pareto_optimal_solutions]
twt_values = [s[1] for s in pareto_optimal_solutions]

plt.scatter(twt_values, make_span_values)
plt.title("Pareto Optimal Solutions")
plt.xlabel("Total Weighted Tardiness")
plt.ylabel("Make Span")

plt.show()


with open("solutions.csv", "w") as f:
    for s in pareto_optimal_solutions:
        f.write(",".join([str(job[0]) for job in s[2]]) + "\n")
