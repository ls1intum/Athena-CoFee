## Data format for evaluation


#### Evaluation with data labeled by ground-truth clusters :
For this evaluation, add the evaluation data under `benchmark/src/data/resources/clustered_text_blocks.csv`.

The CSV file has two rows: 
 - "text": with the text blocks
 - "manual_cluster_id": with the ground-truth cluster identifier as a number
 
Then, call the method `evaluate_with_ground_truth_clusters()` in main.py 



#### Evaluation with data labeled by ground-truth grades :

For this evaluation, add the evaluation data in two files (as exported from the Artemis database): 

The first file `benchmark/src/data/resources/ArTEMiS_text_block.csv` has the following rows:
- "id": with the id of the text blocks
- "text": with the text blocks
 
The second file `benchmark/src/data/resources/ArTEMiS_feedback.csv` has the following rows:
- "id": with the id of the text blocks
- "points": with the grade (as integer) assigned to text-block corresponding to the id

Then, call the `method evaluate_with_ground_truth_grades()` in main.py 

