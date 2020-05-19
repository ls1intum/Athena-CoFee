

def measure_similarity(text_blocks):
    score = 0
    for text_block in text_blocks:
        for other in text_blocks:
            if text_block.similar(other) and text_block.ground_truth_similar(other):
                score += 1
            if not(text_block.similar(other)) and text_block.ground_truth_similar(other):
                score -= 1
    return score

