import pydantic
from typing import List


class EvolutionUnit(pydantic.BaseModel):
    """ A individual unit of the overall population.

    Attributes:
        'T': the thinking_style.

        'M': the mutation_prompt.

        'P': the task_prompt.
        
        'fitness': the estimated performance of the unit.
        
        'history': historical prompts for analysis.

        'R': Result 
    """
    T: str
    M: str
    P: str
    ID: str | None
    fitness: float
    history: List[str]
    task_result: str | None
    parent: str | None | list[str]
    mutant_method: str | None

    def __str__(self):
        strs = [
            f"{str(id(self))}"
            f"T: {self.T}",
            f"M: {self.M}",
            f"P: {self.P}",
            f"fitness: {self.fitness}",
            f"parent: {self.parent}",
            f"mutant method: {self.mutant_method}",
            f"Result: {self.task_result}"
        ]
        return '\n'.join(strs)


class Population(pydantic.BaseModel):
    """ Population model that holds the age of the population, its size, and a list of individuals.
    
    Attributes:
        'size' (int): the size of the population.

        'age' (int): the age of the population.
        
        'units' (List[EvolutionUnit]): the individuals of a population.
    """
    size: int
    age: int
    problem_description: str
    elites: List[EvolutionUnit]
    units: List[EvolutionUnit]
