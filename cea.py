from mtsoo import *

config = load_config()

def cea(functions):
  # unpacking hyper-parameters
  K = len(functions)
  N = config['pop_size'] * K
  D = config['dimension']
  T = config['num_iter']
  sbxdi = config['sbxdi']
  pmdi  = config['pmdi']
  pswap = config['pswap']

  # initialize
  population = np.random.rand(2 * N, D)
  skill_factor = np.array([i % K for i in range(2 * N)])
  factorial_cost = np.full([2 * N, K], np.inf)
  scalar_fitness = np.empty([2 * N])

  # evaluate
  for i in range(2 * N):
    sf = skill_factor[i]
    factorial_cost[i, sf] = functions[sf](population[i])
  scalar_fitness = calculate_scalar_fitness(factorial_cost)

  # sort 
  sort_index = np.argsort(scalar_fitness)[::-1]
  population = population[sort_index]
  skill_factor = skill_factor[sort_index]
  factorial_cost = factorial_cost[sort_index]

  # evolve
  iterator = trange(T)
  for t in iterator:
    # permute current population
    permutation_index = np.random.permutation(N)
    population[:N] = population[:N][permutation_index]
    skill_factor[:N] = skill_factor[:N][permutation_index]
    factorial_cost[:N] = factorial_cost[:N][permutation_index]
    factorial_cost[N:] = np.inf

    # select pair to crossover
    for i in range(0, N, 2):
      # extract parent
      p1  = population[i]
      sf1 = skill_factor[i]
      p2  = find_relative(population, skill_factor, sf1, N)
      # recombine parent
      c1, c2 = sbx_crossover(p1, p2, sbxdi)
      c1 = mutate(c1, pmdi)
      c2 = mutate(c2, pmdi)
      c1, c2 = variable_swap(c1, c2, pswap)
      # save child
      population[N + i, :], population[N + i + 1, :] = c1[:], c2[:]
      skill_factor[N + i] = sf1
      skill_factor[N + i + 1] = sf1

    # evaluate
    for i in range(N, 2 * N):
      sf = skill_factor[i]
      factorial_cost[i, sf] = functions[sf](population[i])
    scalar_fitness = calculate_scalar_fitness(factorial_cost)

    # sort
    sort_index = np.argsort(scalar_fitness)[::-1]
    population = population[sort_index]
    skill_factor = skill_factor[sort_index]
    factorial_cost = factorial_cost[sort_index]

    best_fitness = np.min(factorial_cost, axis=0)
    c1 = population[np.where(skill_factor == 0)][0]
    c2 = population[np.where(skill_factor == 1)][0]

    desc = 'gen:{} fitness:{}'.format(t, ' '.join('{:0.2f}'.format(_) for _ in best_fitness))
    iterator.set_description(desc)

def main():
  functions = CI_HS().functions
  for exp_id in range(config['repeat']):
    print('[+] CEA - CI_HS - %d/%d' % (exp_id, config['repeat']))
    cea(functions)

if __name__ == '__main__':
  main()