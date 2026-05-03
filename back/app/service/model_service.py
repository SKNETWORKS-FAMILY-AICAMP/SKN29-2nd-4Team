from back.app.infra.repo.pred_model_repo import find_model


def predict(model_name, input):
    model_dict = find_model(model_name)
    # 모델 재구성
    # model.predict(input)
    return [0, 1, 0, 1]

def save_model_result():
    pass