from sklearn.metrics import precision_recall_curve
from sklearn.metrics import average_precision_score
from sklearn.metrics import roc_curve, auc
import cPickle
from scipy import interp
import numpy as np
import itertools
from itertools import cycle
from sklearn.metrics import explained_variance_score
from sklearn.metrics import r2_score
from sklearn.metrics import median_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error

def evaluate_model(label, predicted_label):
	from sklearn import metrics
	from sklearn.metrics import accuracy_score
	from sklearn.metrics import cohen_kappa_score
	from sklearn.metrics import classification_report
	from sklearn.metrics import confusion_matrix
	conf_matrix=confusion_matrix(label,predicted_label)
	report=classification_report(label,predicted_label)
	acc_score=accuracy_score(label,predicted_label)
	ck_score=cohen_kappa_score(label,predicted_label)
	precision_micro=metrics.precision_score(label, predicted_label, average='micro')
	precision_macro=metrics.precision_score(label,predicted_label,average='macro')
	recall_micro=metrics.recall_score(label,predicted_label,average='micro')
	recall_macro=metrics.recall_score(label,predicted_label,average='macro')
	f1_micro=metrics.f1_score(label,predicted_label,average='micro')
	f1_macro=metrics.f1_score(label,predicted_label,average='macro')
	print("\n\n")
	print("The confusion matrix is as follows: \n")
	print(conf_matrix)
	print("\n\n")
	print("The classification result for each class is as follows: \n")
	print(report)
	print("\n\n")
	print("Here is the evaluation of the model performance: \n")
	print("The accuracy score is %f.\n"%acc_score)
	print("The Cohen's Kappa score is %f.\n"%ck_score)
	print("The micro precision is %f, the macro precision is %f.\n"%(precision_micro,precision_macro))
	print("The micro recall is %f, the macro recall is %f.\n"%(recall_micro,recall_macro))
	print("The micro F1 score is %f, the macro F1 score is %f.\n"%(f1_micro,f1_macro))

def label_one_hot(label_array):
	from sklearn.preprocessing import OneHotEncoder
	enc=OneHotEncoder()
	label_list=[]
	for i in range(len(label_array)):
		label_list.append([label_array[i]])
	return enc.fit_transform(label_list).toarray()

def calculate_auroc(score, label):
	fpr = dict()
	tpr = dict()
	roc_auc = dict()
	if len(np.shape(label)) == 1:
	    label = np.array(label_one_hot(label))
	score = np.array(score)
	for i in range(len(label[0])):
	    fpr[i], tpr[i], _ = roc_curve(label[:, i], score[:, i])
	    roc_auc[i] = auc(fpr[i], tpr[i])
	for key, value in roc_auc.iteritems():
		print('For class {}, the auroc is {}'.format(key, value))
	return roc_auc

def calculate_auprc(score, label):
	average_precision = dict()
	if len(np.shape(label)) == 1:
	    label = np.array(label_one_hot(label))
	score = np.array(score)
	for i in range(len(label[0])):
	    average_precision[i] = average_precision_score(label[:, i], score[:, i])
	for key, value in average_precision.iteritems():
		print('For class {}, the auprc is {}'.format(key, value))
	return average_precision

def regression_result_evaluate(y_true, y_pred):
	r2_score_weighted = r2_score(y_true, y_pred, multioutput='variance_weighted')
	evs_weighted = explained_variance_score(y_true, y_pred, multioutput='variance_weighted')
	if len(np.shape(y_true))==1:
		median_ae = median_absolute_error(y_true, y_pred)
	mse = mean_squared_error(y_true, y_pred)
	mae = mean_absolute_error(y_true, y_pred)
	print('Variance weighted R2 score is {}'.format(r2_score_weighted))
	print('Variance weighted explained variance score is {}'.format(evs_weighted))
	print('Uniformly averaged mean squared error is {}'.format(mse))
	print('Uniformly averaged mean absolute error is {}'.format(mae))
	if len(np.shape(y_true))==1:
		print('Median absolute error is {}'.format(median_ae))
	


if __name__ == '__main__':
	pass