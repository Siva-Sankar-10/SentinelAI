def calculate_accuracy(predictions, labels):
    """
    Calculate the accuracy of predictions against the true labels.

    Args:
        predictions (list): A list of predicted labels.
        labels (list): A list of true labels.

    Returns:
        float: The accuracy as a percentage.
    """
    correct_predictions = sum(p == l for p, l in zip(predictions, labels))
    total_predictions = len(labels)
    
    if total_predictions == 0:
        return 0.0
    
    accuracy = (correct_predictions / total_predictions) * 100
    return accuracy