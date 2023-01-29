import joblib


def model_load(path):
    rfc = joblib.load(path)
    return rfc

def model_save(model,path):
    joblib.dump(model,path)