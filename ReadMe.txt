Implementation of the consensus algorithm used by Facebook’s diem blockchain system. Also implemented a testing framework for DiemBFT using the Twins approach. 
 
LINKS:
 
DiemBFT: https://developers.diem.com/docs/technical-papers/state-machine-replication-paper/
Twins: https://arxiv.org/abs/2004.10617#:~:text=This%20paper%20presents%20Twins%2C%20an,'locks'%20guarding%20voted%20values.

PLATFORM:
The software platforms that are used in testing the algorithm are:


OS: 
macOS 11.6 (Big Sur) 

Python Implementation:
Python 3.7.0


DistAlgo Version used for implementation:
1.1.0b15


Type of host:
Laptop



BUGS AND LIMITATIONS:
-- In test generator, test cases with configuration having 7 nodes, 2 partitions, 2 twins, 4 round with faulty leader selection, is not getting generated.
-- Race condition in sync-up mechanism causes safety and liveness issues in quite a few test cases
-- Test executor faces several issues and crashes when executing more than 100 testcases

MAIN FILES:
-- Config for test generator: <path_of_project_folder>/config/generator_config.py
-- Test generator: <path_of_project_folder>/src/{test_generator, generate_partitions}.py
-- Test executor: <path_of_project_folder>/src/test_executor.da
-- Simulating network partitions: <path_of_project_folder>/src/validator_twins.da
-- Overwritten mem_pool and leader_election: <path_of_project_folder>/src/{mem_pool, leader_election}.da
-- Classes used by Test Generator and Test Executor: <path_of_project_folder>/src/{generator_models, executor_models}.py
-- Fixing correctness issues in LBG implementation: cryptographic hash verification <path_of_project_folder>/src/validator.da
-- Fixing correctness issues in LBG implementation: sync up of replicas <path_of_project_folder>/src/validator.da
-- Fixing correctness issues in LBG implementation: mem_pool issue <path_of_project_folder>/src/mem_pool.da
-- Fixing correctness issues in LBG implementation: issue where duplicate votes form QC <path_of_project_folder>/src/block_tree.da


CODE SIZE:
1. Non-blank non-comment lines of code in Test generator:	155(Total)
							126(test generator implementation)
                                       			14(generator config)
							15(generator models)

2. Non-blank non-comment lines of code in Test executor :  243(Total)
							125(test executor implementation)
							48(other - executor models)
							70(network playground)

2. Count for both test generator and test executor was obtained using cloc command : cloc "filename"



LANGUAGE FEATURE USAGE:
Our algorithm uses approximately 1 dictionary comprehensions, no set comprehensions, 10 list comprehensions, 2 await statements and no receive handlers(in Twins implementation).


CONTRIBUTIONS:

Balaji Jayasankar:
-- Test executor and test generator
-- Test report and user manual documentation


Reetu Singh:
-- Test generator, pseudocode documentation

Prashant Shrivastava:
-- Network playground, readme documentation
