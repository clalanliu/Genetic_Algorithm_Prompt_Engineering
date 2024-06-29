import random
import re
import os
from pb.types import Population, EvolutionUnit
from typing import List
# from sentence_transformers import SentenceTransformer, util
from pb.mutation_prompts import mutation_prompts
from pb.thinking_styles import thinking_styles
from pb import gsm
from cohere import Client

from dotenv import load_dotenv
from rich import print

load_dotenv()

# need below for estimation_distribution_mutation, not currently using.
# model = SentenceTransformer('multi-qa-distilbert-cos-v1')
# print(model)

# Direct Mutation mutators


def zero_order_prompt_gen(unit: EvolutionUnit, problem_description: str, model: Client, **kwargs) -> EvolutionUnit:
    """Generates a new task-prompt P by concatenating the problem description D with the prompt 
    'a list of 10 hints:'. New task-prompt P is the first generated hint.
    
    Returns: 
        EvolutionUnit: the evolution unit to replace the loser unit.
    """
    prompt = f"""\
Task:
{problem_description}

Give me one tip to complete the task and write the instruction for this task."""
    result = model.generate(prompt)[0].text

    if result is not None:
        # return the first match
        unit.P = result
    else:
        unit.P = ""

    return unit


def first_order_prompt_gen(unit: EvolutionUnit, model: Client, **kwargs) -> EvolutionUnit:
    """Concatenate the mutation prompt M to the parent task-prompt P and pass it to the LLM to produce P'
    
    Returns: 
        EvolutionUnit: the evolution unit to replace the loser unit.
    """
    unit.P = model.generate(unit.M + " " + unit.P)[0].text
    return unit

# Estimation of Distribution Mutation - there is a variation of this called EDA rank
# and index mutation. I didn't implement it.


def estimation_distribution_mutation(unit: EvolutionUnit, population_units: List[EvolutionUnit], **kwargs) -> EvolutionUnit:
    """ Provide a filtered and numbered list of the current population of task-prompts to the LLM and ask it to continue this list with new task-prompts.
    The List is filtered via ensuring that no two task-prompts have a score of >0.95 via BERT embedding cosine similarities.
    The List is randomly ordered.  

    NOTE: I am confused by this one. Does this mutate the entire population? What values of the continued list from the LLM do I use as prompts? randomly sampled?
    Not going to implement this one yet. Maybe should email someone. 
    
    Returns: 
        EvolutionUnit: the evolution unit to replace the loser unit.
    """
    pass


def lineage_based_mutation(unit: EvolutionUnit, elites: List[EvolutionUnit], model: Client, **kwargs) -> EvolutionUnit:
    """Using the stored history of best units, provide the LLM this list in chronological order to produce a novel prompt as continuation.
    
    Returns: 
        EvolutionUnit: the evolution unit to replace the loser unit.
    """
    HEADING = "Below are instructions in ascending order of fitness score.\n"
    # made a choice not to format it with newlines, could change later.
    ITEMS = "\n".join(["{}. {}".format(i+1, x.P)
                      for i, x in enumerate(elites)])
    INSTRUCTION = "\n\nGenerate improved instructions that are more effective than the existing ones."
    unit.P = model.generate(HEADING + ITEMS + INSTRUCTION)[0].text

    return unit

# Hypermutation


def zero_order_hypermutation(unit: EvolutionUnit, problem_description: str, model: Client, **kwargs) -> EvolutionUnit:
    """ Concatenate the original problem_description to a randomly sampled thinking-style and feed it to the LLM to generate a new mutation-prompt.
    
    Returns: 
        EvolutionUnit: the evolution unit to replace the loser unit.
    """
    RANDOM_THINKING_STYLE = random.sample(thinking_styles, 1)[0]
    unit.M = model.generate(problem_description + " " +
                            RANDOM_THINKING_STYLE)[0].text
    return unit


def first_order_hypermutation(unit: EvolutionUnit, model: Client, **kwargs) -> EvolutionUnit:
    """ Concatenate the hyper-mutation prompt "Please summarize and improve the following instruction:"
    to a mutation-prompt to that the LLM generates a new mutation-prompt. This new mutation-prompt is then 
    instantly applied to the task-prompt of that unit.

    Returns: 
        EvolutionUnit: the evolution unit to replace the loser unit.
    """
    HYPER_MUTATION_PROMPT = "Please summarize and improve the following instruction: "
    unit.M = model.generate(HYPER_MUTATION_PROMPT + unit.M)[0].text
    unit.P = model.generate(unit.M + " " + unit.P)[0].text
    return unit


# Lamarckian Mutation
def working_out_task_prompt(unit: EvolutionUnit, model: Client, **kwargs) -> EvolutionUnit:
    """ A 'lamarckian' mutation operator similar to instruction induction in APE.

    As far as I can understand, give it both the Q and A from the gsm8k dataset, 
    concatenated between 'I gave a friend an instruction and some advice. Here
    are the correct examples of his workings out ' and 'The instruction was: '
    The idea is to let the LLM reverse-engineer the task-prompt.

    Returns: 
        EvolutionUnit: the evolution unit to replace the loser unit.
    """
    sample_answers = [
        "In the quaint village of Arbor, nestled between lush, verdant hills, Elara spent a decade unraveling the intricacies of love. Her journey began unexpectedly when a sudden downpour disrupted her solitary walk through the dense, fragrant orchards. Sheltering in a rustic, ivy-draped cabin, she encountered Kai, a painter whose vibrant canvases mirrored the chaotic beauty of the storm. Their initial conversations were hesitant, their dialogues a tentative dance around topics like the erratic weather, the resilience of the orchard's blooms, and the peculiar habits of the local wildlife. Yet, as seasons shifted, so did their rapport, evolving from casual chats to profound exchanges about aspirations, fears, and passions. Throughout the years, Elara and Kai shared countless sunsets and sunrises, each moment deepening their connection. They learned that love was not a constant, sunny day but a series of storms and clear skies, each phase teaching them resilience, patience, and the joy of shared silences. On the eve of their tenth anniversary, under the canopy of a starlit sky, they celebrated their enduring bond, a testament to their journey through life's unpredictable weather, the perennial blooms of their affection, and the tranquil harmony of understanding each other’s hearts.",
        "For ten years, Jane traversed the tumultuous terrain of love, her heart navigating through volcanic eruptions of emotion and serene sunsets of tranquility. She ventured into relationships as a daring explorer, grappling with the gravitational pull of attachment and the occasional suffocating fog of misunderstanding. Each connection was a mosaic of varied hues, from the fiery passion of the initial encounter to the mellow, enduring warmth that only time could bestow. Her journey was fraught with treacherous pitfalls, like navigating a foggy coastline, where the danger of collision with emotional debris was ever-present. Yet, Jane's unwavering determination to decode love's complex algorithm kept her afloat, even when the seas turned choppy and the path seemed overgrown with obstacles. She learned that love wasn't just a sentimental melody played on the heart's strings but a rigorous composition requiring both partners to harmonize. It was a blend of practical navigation and the ethereal beauty of a breathtaking panorama. Through this decade-long expedition, Jane discovered that love's true essence lay in its resilience, adaptability, and the delicate balance of mutual understanding and affection.",
        "Over a decade, exploring the multifaceted concept of love felt like a labyrinthine journey. Initially, my perception was primitive, naïve even, but as the years progressed, I realized the profound significance of this emotion. Conversations with both acquaintances and strangers revealed the versatile nature of love—romantic, platonic, familial. Like a complex ecosystem, it involved a balance of give and take, often clouded by misunderstandings and unforeseen hardships. The journey wasn't devoid of obstacles; rather, it was punctuated by moments of profound enlightenment and agonizing sorrow. I navigated through phases of heartbreak and euphoria, each instance sharpening my understanding. Sometimes, love felt like a torrential downpour, other times, a gentle breeze, yet its impact was always significant, leaving indelible marks on my soul. Through candid conversations and reflective solitude, I recognized love's resilience, its ability to withstand trials and evolve. By integrating these experiences into a cohesive narrative, I finally comprehended love's essence—a delicate balance of emotion, sacrifice, and unwavering commitment. This odyssey culminated in a profound appreciation for love's intricate, enduring nature.",
        "For a decade, John navigated a labyrinth of emotions, determined to comprehend love. His journey began with a frigid, indifferent heart, but gradually, he evolved, experiencing both soaring highs and abysmal lows. His efforts were fraught with disillusion, disappointment, and fleeting joy, each relationship a microcosm of complexity. In his pursuit, John encountered a myriad of characters: an ardent poet, a detached scientist, and a fervent activist. Each liaison was a reflection of his own state, from fervent to apathetic. The intricacies of each connection were meticulously documented in his diary, a blend of poetic verses and methodical observations. Love's dynamics were akin to gravitational forces, pulling him in with irresistible allure, only to sometimes repel him with equal intensity. He likened relationships to tectonic movements—constantly shifting, sometimes causing seismic upheavals, yet capable of forming unbreakable bonds. In the end, John's decade-long expedition into love revealed it as a delicate equilibrium of passion and patience, a radiant phenomenon as complex and multifaceted as the cosmos itself. His heart, once a barren landscape, now brimmed with profound understanding and unwavering resilience.",
        "In a decade-long odyssey to comprehend love, Emily, a biologist, sought to integrate scientific rigor with profound emotion. Her quest was not merely to dissect, but to coalesce affection with intellectual curiosity. In the laboratory, she meticulously documented hormonal fluctuations, elucidated neurotransmitter pathways, and observed the subtleties of body language. Her diary brimmed with anecdotes of passion, detailing every nuanced gesture and tender glance. Despite the rigor of her study, love remained elusive and enigmatic. Its unpredictable nature often seemed to defy the confines of scientific method. Emily's approach oscillated between empirical analysis and heartfelt introspection. She analyzed the impact of pheromones, traced the evolutionary roots of mating rituals, and pondered the psychological intricacies of attachment. Through this interplay of emotion and intellect, she encountered moments of unparalleled insight and disheartening ambiguity. Her findings, though often incongruous and perplexing, illuminated the multifaceted nature of love. Ultimately, Emily's journey underscored that love, much like the universe, is a confluence of phenomena—both celestial and terrestrial, empirical and ephemeral, rational and profoundly mystifying.",
    ]
    sampled = random.choice(sample_answers)
    prompt = "I gave a friend an instruction and some advice. Here is the correct example of his workings out:\n" + \
        f"### Story:\n{sampled}\n### End of Story\n\n" + \
        "What was the instruction?"
    unit.P = model.generate(prompt)[0].text
    return unit

# Prompt crossover and context shuffling. These happen AFTER mutation operators.


def prompt_crossover(**kwargs):
    """
    After a mutation operator is applied, 

    Returns: 
        EvolutionUnit: the evolution unit to replace the loser unit.
    """


def context_shuffling(**kwargs):
    """
    
    Returns: 
        EvolutionUnit: the evolution unit to replace the loser unit.
    """


# omitting the estimation_distribution_mutation
MUTATORS = [
    zero_order_prompt_gen,
    first_order_prompt_gen,
    # estimation_distribution_mutation,
    lineage_based_mutation,
    # zero_order_hypermutation, # Not stable
    # first_order_hypermutation, # Not stable
    working_out_task_prompt
]

POST_MUTATORS = [
    prompt_crossover,
    context_shuffling
]


def mutate(population: Population, model: Client) -> Population:
    """Select and apply a random mutator"""
    # steps
    # 1. parse through the population, grouping each evo unit by 2
    # 2. for each pair of evo units, using a uniform distribution, select a random mutator (of the 9)
    # 3. mutate and populate population.units

    # make index pairs
    indices = [i for i in range(len(population.units))]
    random.shuffle(indices)
    pairs = [indices[2*x:2*x+2] for x in range(len(indices) // 2)]

    # binary tourmanent genetic algorithm
    for i in range(len(pairs)):
        first_unit = population.units[pairs[i][0]]
        second_unit = population.units[pairs[i][1]]

        '''
        print("%"*77)
        print("First unit: \n")
        print(first_unit)
        print("%"*77)
        print("Second unit: \n")
        print(second_unit)
        '''

        # determine which unit has the higher fitness. Since I am currently testing and want to preserve the # of calls I am making to the LLM, there
        # is a decent chance that I will hit equal fitness levels. in that case, first unit wins and second unit loses.

        if first_unit.fitness >= second_unit.fitness:
            mutation_input = second_unit
        else:
            mutation_input = first_unit

        data = {
            'unit': mutation_input,
            'model': model,
            'elites': population.elites,
            'problem_description': population.problem_description,
        }

        # uniformly pick and call a random mutation operator on the losing unit
        random_mutator = random.sample(MUTATORS, 1)[0]
        # print(f"MUTATING: {mutation_input} with {random_mutator.__name__}")

        random_mutator(**data)
        mutation_input.mutant_method = str(random_mutator.__name__)

    return population
