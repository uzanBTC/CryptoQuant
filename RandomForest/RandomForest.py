from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import RocCurveDisplay
from sklearn.metrics import accuracy_score, classification_report

import joblib
from datetime import datetime
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt

class RandomForest():

    def __init__(self,strategy_name:str):
        self.strategy_name=strategy_name


    def model_training(self,x_train,y_train,n_estimators=100):
        random_forest_classifier = RandomForestClassifier(n_estimators=n_estimators, oob_score=True, criterion='gini',
                                                          random_state=90)
        random_forest_classifier.fit(x_train, y_train)


    def model_save(self,model):
        path=self.strategy_name+"-"+datetime.now().strftime("%Y%m%d-%H%M%S")+".joblib"
        joblib.dump(model,path)
        return path

    def model_load(self,path):
        rfc=joblib.load(path)
        return rfc

    def model_training_with_trend(self,data,target,n_estimator_start=0,n_estimator_end=200,step=10,random_state=90):
        '''
        训练时，使用交叉验证方式（十折交叉验证），画出得分曲线，用以观察 复杂度-泛化误差
        :param data: 数据特征
        :param target: 数据标签
        :param n_estimator_start: 决策树的数量下限
        :param n_estimator_end: 决策树数量的上限
        :param train_step: 决策树数量每次训练增加多少个
        :param random_state: 模型的随机程度，0表示每次训练状态都一样
        :return: (max_score:int, max_score_index:int)
        '''
        scorel=[]
        for i in range(n_estimator_start, n_estimator_end, step):
            rfc = RandomForestClassifier(n_estimators=i + 1,
                                         n_jobs=-1,
                                         random_state=random_state)
            # cv=10 意思是把数据分成10份，轮流将其中9份作为训练数据，1份作为测试数据
            score = cross_val_score(rfc, data, target, cv=10).mean()
            scorel.append(score)
        print(max(scorel), (scorel.index(max(scorel)) * step) + 1)
        plt.figure(figsize=[20, 5])
        plt.plot(range(n_estimator_start+1, n_estimator_end+1, step), scorel)
        plt.show()





 