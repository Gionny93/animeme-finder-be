import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import pdist, squareform
from scipy.sparse import csr_matrix
from flask_jwt_extended import get_jwt_identity
import numpy as np

class CollFiltering:

    def __init__(self, user_anime_list, general_anime_list):
        self.user_anime_list = user_anime_list
        self.anime_data = general_anime_list
        self.anime_data['genre'] = self.anime_data['genres'].apply(lambda x: ','.join([genre['name'] for genre in x]))

    def recommend_anime(self, user_list, anime_list, top_n=10):
        user_list['score'] = user_list['score'].astype(float)
        anime_list['score'] = anime_list['score'].astype(float)

        merged_data = pd.merge(user_list, anime_list, on='title', suffixes=('_user', '_all'), how='right')

        merged_data['genre'] = merged_data['genre_all']

        merged_data['score_diff'] = merged_data['score_user'] - merged_data['score_all']
        user_mean_score = np.mean(merged_data['score_diff'])

        anime_list['normalized_score'] = anime_list['score'] + user_mean_score

        anime_list['normalized_score'].fillna(anime_list['normalized_score'].mean(), inplace=True)

        anime_list['genre_similarity'] = anime_list['genre'].apply(
            lambda x: len(set(x.split(',')).intersection(set(merged_data['genre'].iloc[0].split(',')))) /
                    len(set(x.split(',')).union(set(merged_data['genre'].iloc[0].split(',')))))

        anime_list['genre_similarity'].fillna(anime_list['genre_similarity'].mean(), inplace=True)

        anime_list['overall_similarity'] = anime_list['normalized_score'] * anime_list['genre_similarity']

        user_scores = np.array(merged_data['score_user']).reshape(1, -1)
        all_normalized_scores = np.repeat(anime_list['overall_similarity'].values.reshape(1, -1), len(user_scores[0]), axis=0).T

        user_scores = np.nan_to_num(user_scores)

        all_normalized_scores = np.nan_to_num(all_normalized_scores)

        similarities = cosine_similarity(user_scores, all_normalized_scores)

        top_indices = np.argsort(similarities[0])[-top_n:][::-1]
        recommendations = anime_list.iloc[top_indices]

        return recommendations


    def execute(self, top_n=5):
            return self.recommend_anime(self.user_anime_list, self.anime_data, top_n=top_n)

