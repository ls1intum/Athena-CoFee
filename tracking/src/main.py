import base64
from math import sqrt
from os import environ

import jaro
import numpy as np
import pandas as pd
from enum import Enum
from fastapi import FastAPI, Request, Response, status
from jwt import decode
from sklearn import preprocessing
from sklearn.metrics import cohen_kappa_score

from .database.Connection import Connection

app = FastAPI()

@app.post('/tracking/text-exercise-assessment', status_code=201)
async def track(request: Request, response: Response):
    feedback = await request.json()
    jwt_token = request.headers.get('x-athene-tracking-authorization')
    secret_base64 = environ['AUTHORIZATION_SECRET']
    try:
        encoded_jwt_token = decode(jwt_token, base64.b64decode(secret_base64), verify=True, algorithms=['HS256'])
        if encoded_jwt_token.get('result_id') != feedback.get('participation').get('results')[0].get('id'):
            response.status_code = status.HTTP_403_FORBIDDEN
            return {'Please do not spam manually!'}
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {'Your token is not valid!'}
    try:
        conn = Connection()
        conn.insert_document('feedback', feedback)
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'message': 'Saving in the database did not work!'}
    return {'Feedback is tracked successfully'}


@app.get('/tracking/exerciseId/{exercise_id}', status_code=200)
async def evaluate(exercise_id: int, response: Response):
    try:
        conn = Connection()
        raw_data = conn.get_data_for_evaluation(exercise_id)
        metrics = calculate_metrics(raw_data, exercise_id)
        return metrics
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'message': 'There is no data for this exercise!'}


class FeedbackType(Enum):
    Automatic = 1
    Typo = 2
    Extended = 3
    Different = 4


def cohens_kappa(l1, l2):
    # transfrom float values into distinc categories
    enc = preprocessing.LabelEncoder()
    enc.fit(np.hstack((l1, l2)))

    # calculate kappa
    kappa_val = cohen_kappa_score(enc.transform(l1), enc.transform(l2))
    return kappa_val


def jaro_winkler(s1: str, s2: str):
    dis = jaro.jaro_winkler_metric(s1, s2)
    # print(f'Jaro-Winkler: {dis}')
    return dis


def jaro_metric(s1: str, s2: str):
    dis = jaro.jaro_metric(s1, s2)
    # print(f'Jaro: {dis}')
    return dis


# Calculates the normalized Levenshtein distance of 2 strings
def levenshtein(s1, s2):
    l1 = len(s1)
    l2 = len(s2)
    matrix = [list(range(l1 + 1))] * (l2 + 1)
    for zz in list(range(l2 + 1)):
        matrix[zz] = list(range(zz, zz + l1 + 1))
    for zz in list(range(0, l2)):
        for sz in list(range(0, l1)):
            if s1[sz] == s2[zz]:
                matrix[zz + 1][sz + 1] = min(matrix[zz + 1][sz] + 1, matrix[zz][sz + 1] + 1, matrix[zz][sz])
            else:
                matrix[zz + 1][sz + 1] = min(matrix[zz + 1][sz] + 1, matrix[zz][sz + 1] + 1, matrix[zz][sz] + 1)
    distance = float(matrix[l2][l1])
    result = 1.0 - distance / max(l1, l2)
    # print(f'Levenshtein: {result}')
    return result


# Dynamic Programming implementation of LCS problem

def lcs(s1, s2):
    # find the length of the strings
    m = len(s1)
    n = len(s2)

    # declaring the array for storing the dp values
    L = [[None] * (n + 1) for i in range(m + 1)]

    """Following steps build L[m + 1][n + 1] in bottom up fashion 
	Note: L[i][j] contains length of LCS of X[0..i-1] 
	and Y[0..j-1]"""
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif s1[i - 1] == s2[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])

    # L[m][n] contains the length of LCS of X[0..n-1] & Y[0..m-1]
    # print(f'LCS: {L[m][n] / min(len(s1), len(s2))} (absolute: {L[m][n]}; length_s1: {len(s1)}, length_s2: {len(s2)})')

    # prevent division by zero if LCS is 0
    if L[m][n] > 0:
        return min(len(s1), len(s2)) / L[m][n]
    else:
        return 0


def st_mean_diff(l1, l2):
    mean_l1 = np.mean(l1)
    mean_l2 = np.mean(l2)
    std_l1 = np.std(l1)
    std_l2 = np.std(l2)

    diff = abs((mean_l1 - mean_l2) / sqrt((std_l1 + std_l2) / 2))

    return diff


def calculate_duration(start, end):
    # calculate submission time
    start_time = start.generation_time
    end_time = end.generation_time

    timedelta = end_time - start_time

    return timedelta.total_seconds()


def classify_comment(s1: str, s2: str):
    if s1 == s2:
        return FeedbackType.Automatic
    elif levenshtein(s1, s2) > 0.9:
        return FeedbackType.Typo
    elif lcs(s1, s2) > 0.95 and jaro_winkler(s1, s2) > 0.6:
        return FeedbackType.Extended
    else:
        return FeedbackType.Different


def calculate_metrics(df: pd.DataFrame, exercise_id: int):
    score_first_feedbacks = []
    score_last_feedbacks = []
    automatic_assessment_times = []
    manual_assessment_times = []
    assessed_participations = []

    type_count = {
        str(FeedbackType.Automatic): 0,
        str(FeedbackType.Typo): 0,
        str(FeedbackType.Extended): 0,
        str(FeedbackType.Different): 0
    }
    count = 0
    log_count = 0

    for reference, df_reference in df.groupby('feedbacks.reference'):
        # sort df since sorting before changed order
        df_reference = df_reference.sort_index()
        count += 1
        # make sure that automatic feedback was provided
        if len(df_reference.index) > 1:
            head = df_reference.head(1)
            tail = df_reference.tail(1)
            if df_reference.head(1)['feedbacks.type'].values[0] == 'AUTOMATIC':
                # only the first and the last entry are important
                score_first_feedbacks.append(head['feedbacks.credits'].values[0])
                score_last_feedbacks.append(tail['feedbacks.credits'].values[0])

                # classify feedback
                automatic_comment = head['feedbacks.detailText'].values[0]
                human_comment = tail['feedbacks.detailText'].values[0]

                # only calculate duration once for each participation
                participation_id = df_reference.head(1)['pID'].values[0]
                if participation_id not in assessed_participations:
                    # calculate duration
                    duration = calculate_duration(head['_id'].values[0], tail['_id'].values[0])
                    automatic_assessment_times.append(duration)
                    assessed_participations.append(participation_id)

                feedback_type = classify_comment(str(automatic_comment), str(human_comment))
                type_count[str(feedback_type)] += 1
            else:
                # only calculate duration once for each participation
                participation_id = df_reference.head(1)['pID'].values[0]
                if participation_id not in assessed_participations:
                    duration = calculate_duration(head['_id'].values[0], tail['_id'].values[0])
                    manual_assessment_times.append(duration)
                    assessed_participations.append(participation_id)
        else:
            if df_reference.head(1)['feedbacks.type'].values[0] == 'MANUAL':
                log_count += 1

    percentage_provided = round(len(score_first_feedbacks) / count * 100, 2)

    # print(log_count)

    kappa_val = cohens_kappa(score_first_feedbacks, score_last_feedbacks)

    diff = st_mean_diff(score_first_feedbacks, score_last_feedbacks)

    metrics = {
        'exerciseId': exercise_id,
        'sample_size_total': count,
        'sample_size_metrics': len(score_first_feedbacks),
        'percentage_provided': percentage_provided,
        'cohens_kappa': round(kappa_val, 4),
        'std_mean_score_diff': round(diff, 4),
        'comment_distribution': type_count,
        'percentage_automatic_feedback': round(type_count[str(FeedbackType.Automatic)] / len(score_first_feedbacks), 4),
        'automatic_assessment_duration': {
            'min_seconds': round(np.min(automatic_assessment_times), 2),
            'max_seconds': round(np.max(automatic_assessment_times), 2),
            'mean_seconds': round(np.mean(automatic_assessment_times), 2),
            'median_seconds': round(np.median(automatic_assessment_times), 2)},
        'manual_assessment_duration': {
            'min_seconds': round(np.min(manual_assessment_times), 2),
            'max_seconds': round(np.max(manual_assessment_times), 2),
            'mean_seconds': round(np.mean(manual_assessment_times), 2),
            'median_seconds': round(np.median(manual_assessment_times), 2)}
    }

    print(metrics)
    return metrics
