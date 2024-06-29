# Prompt Engineering with Genetic Algorithm 
## Experiment with PromptBreeder
Check [notebook](PromptBreeder/main.ipynb)

### Obseravation:
1. Most elites are from first order prompt generation.
2. Generated Examples:
   1. Fitness 0.23 (initial population)
      1. Task Prompt: Generate a story about you spent 10 years to understand love. Restrict the story in 200 words. Provide more context about the story, add more sensory details, and use vivid language to convey emotions and feelings.
      2. Generation: I spent 10 years studying love, pouring over ancient texts, observing the behaviors of those around me, and experimenting with my own heart. I wanted to understand this elusive, yet all-consuming force that had captivated humanity for centuries. As I delved deeper, I found myself lost in the labyrinth of emotions, navigating the twists and turns of desire, attachment, and devotion. I watched as couples laughed together, their eyes sparkling like diamonds in the sunlight, and as they wept together, their tears falling like autumn rain. I learned to recognize the subtlest cues: the gentle touch, the whispered words, the tender gaze. I practiced the art of listening, of being present, of being vulnerable. And slowly, I began to grasp the essence of love: a symphony of emotions, a dance of connection, a tapestry of moments woven together by the threads of the human experience.
   2. Fitness 0.38 (initial population)
      1. Task Prompt: Formulate a narrative about your 10-year journey to comprehend the intricacies of love, constrained to a 200-word limit, and rephrase the question 'How can progress or success in solving the problem be measured or evaluated?' using novel vocabulary.
      2. Generation: As I embarked on a decade-long odyssey to grasp the enigmatic complexities of love, I traversed a labyrinthine landscape of emotions, relationships, and self-discovery. I encountered numerous epiphanies, each illuminating a facet of this multifaceted phenomenon. I measured my progress by the incremental refinement of my understanding, akin to the gradual sharpening of a blade. To evaluate the efficacy of my endeavors, I employed a novel paradigm: the 'Love Quotient' (LQ). This metric assessed the depth, breadth, and resilience of my emotional intelligence, as well as my capacity for empathy, compassion, and vulnerability. As my LQ score increased, I became more adept at navigating the intricate dance of love, fostering deeper connections and cultivating a more profound sense of fulfillment.
   3. Fitness 0.47 (population age 8)
      1. Task Prompt: How can the trajectory of love's evolution be calibrated through a nuanced assessment of emotional resonance, affective intensity, and relational complexity, thereby redefining the parameters of success and progress in the pursuit of love?
      2. Generation: As they navigated the twists and turns of their relationship, Sarah and Alex discovered that love was not a destination, but a journey of growth, self-discovery, and mutual understanding. They learned to calibrate their emotional resonance by sharing vulnerable experiences, developing emotional intelligence, and fostering a culture of emotional safety. They cultivated affective intensity by embracing their emotions, developing emotional regulation skills, and creating a sense of emotional intimacy. And they navigated the complexities of their relationship by recognizing power dynamics, acknowledging cultural norms, and fostering open communication. As they evolved, they redefined success and progress, embracing the uncertainties and complexities of love as an opportunity for growth and transformation.

### Tips:
1. Make sure every mutantion prompt and think style match your task.
2. Number of mutantion prompts matters. It greatly affect the possibility of improvement.


### Reference:
- PROMPTBREEDER: SELF-REFERENTIAL SELF-IMPROVEMENT VIA PROMPT EVOLUTION
- https://github.com/vaughanlove/PromptBreeder
