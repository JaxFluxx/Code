import pandas as pd
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, ConfusionMatrixDisplay, roc_curve, auc, recall_score
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt

# Step 1: Load data
train_path = r"/Users/jia/Desktop/学习 /科研/SVM_支持向量机/Dataset_cleaned_1/archive/healthcare_stroke_train.csv"
test_path = r"/Users/jia/Desktop/学习 /科研/SVM_支持向量机/Dataset_cleaned_1/archive/healthcare_stroke_test.csv"

train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

# Step 2: Balance training data
non_stroke_train = train_df[train_df['stroke'] == 0]
stroke_train = train_df[train_df['stroke'] == 1]

non_stroke_train_sampled = non_stroke_train.sample(n=235, random_state=42)
balanced_train_df = pd.concat([non_stroke_train_sampled, stroke_train])
balanced_train_df = balanced_train_df.sample(frac=1, random_state=42).reset_index(drop=True)

X_train = balanced_train_df.drop(columns=["stroke"])
y_train = balanced_train_df["stroke"]

print("Training set class distribution:")
print(y_train.value_counts())

# Step 3: Balance test data
non_stroke_test = test_df[test_df['stroke'] == 0]
stroke_test = test_df[test_df['stroke'] == 1]

non_stroke_test_sampled = non_stroke_test.sample(n=100, random_state=42)
balanced_test_df = pd.concat([non_stroke_test_sampled, stroke_test])
balanced_test_df = balanced_test_df.sample(frac=1, random_state=42).reset_index(drop=True)

X_test = balanced_test_df.drop(columns=["stroke"])
y_test = balanced_test_df["stroke"]

print("\nTest set class distribution:")
print(y_test.value_counts())

# Step 4: Grid search parameters
param_grid = {
    'kernel': ['rbf'],
    'C': [0.001, 0.1, 1, 10],
    'gamma': ['scale', 'auto', 0.01, 0.1, 1, 10]
}

grid_search = GridSearchCV(
    estimator=SVC(random_state=42),
    param_grid=param_grid,
    cv=5,
    scoring='f1',
    verbose=1,
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

print("\nBest Parameters:")
print(grid_search.best_params_)

# Step 5: Evaluate best model
best_model = grid_search.best_estimator_
y_pred = best_model.predict(X_test)

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Non-Stroke", "Stroke"]))

accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")

# Step 6: Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Non-Stroke", "Stroke"])
disp.plot(cmap=plt.cm.Blues)
plt.title("Confusion Matrix")
plt.show()

# Step 7: ROC Curve and AUC
if hasattr(best_model, "decision_function"):
    y_scores = best_model.decision_function(X_test)
else:
    y_scores = best_model.predict_proba(X_test)[:, 1]

fpr, tpr, _ = roc_curve(y_test, y_scores)
roc_auc = auc(fpr, tpr)

# Step 8: Total Recall (Sensitivity) / True Positive Rate
total_recall = recall_score(y_test, y_pred)
print(f"Total Recall: {total_recall:.2f}")

# Plot ROC Curve
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')

# Adding accuracy and total recall to the plot
plt.text(0.6, 0.2, f'Accuracy: {accuracy:.2f}', fontsize=12, color='black', ha='center')
plt.text(0.6, 0.15, f'Total Recall: {total_recall:.2f}', fontsize=12, color='black', ha='center')

plt.legend(loc="lower right")
plt.grid(True)
plt.show()
