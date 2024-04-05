from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi()
api.authenticate()
api.dataset_download_file('avenn98/world-of-warcraft-demographics','WoW Demographics.csv')