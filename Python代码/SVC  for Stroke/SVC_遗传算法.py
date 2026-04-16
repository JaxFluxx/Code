import pandas as pd
import numpy as np
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, recall_score
from sklearn.model_selection import cross_val_score
from deap import base, creator, tools, algorithms
import random
import warnings
warnings.filterwarnings("ignore")

# Step 1: Load data
train_path = r"/Users/jia/Desktop/学习/科研/上课部分/SVM_支持向量机/Dataset_cleaned_1/archive/healthcare_stroke_train.csv"
test_path = r"/Users/jia/Desktop/学习/科研/上课部分/SVM_支持向量机/Dataset_cleaned_1/archive/healthcare_stroke_test.csv"

train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

# Step 2: Balance training data
non_stroke_train = train_df[train_df['stroke'] == 0]
stroke_train = train_df[train_df['stroke'] == 1]
non_stroke_train_sampled = non_stroke_train.sample(n=235, random_state=42)
balanced_train_df = pd.concat([non_stroke_train_sampled, stroke_train]).sample(frac=1, random_state=42).reset_index(drop=True)

X_train = balanced_train_df.drop(columns=["stroke"])
y_train = balanced_train_df["stroke"]

print("Training set class distribution:")
print(y_train.value_counts())

# Step 3: Balance test data
non_stroke_test = test_df[test_df['stroke'] == 0]
stroke_test = test_df[test_df['stroke'] == 1]
non_stroke_test_sampled = non_stroke_test.sample(n=100, random_state=42)
balanced_test_df = pd.concat([non_stroke_test_sampled, stroke_test]).sample(frac=1, random_state=42).reset_index(drop=True)

X_test = balanced_test_df.drop(columns=["stroke"])
y_test = balanced_test_df["stroke"]

print("\nTest set class distribution:")
print(y_test.value_counts())

# Step 4: Define Genetic Algorithm for parameter tuning
# Define fitness function (maximize F1 score)
def evaluate(individual):
    C = individual[0]
    gamma = individual[1]
    model = SVC(C=C, gamma=gamma, kernel='rbf', random_state=42)
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1')
    return (scores.mean(),)

# GA configuration
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_C", random.uniform, 0.001, 10)
toolbox.register("attr_gamma", random.uniform, 0.0001, 10)
toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.attr_C, toolbox.attr_gamma), n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.5, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

population = toolbox.population(n=20)
result_population, _ = algorithms.eaSimple(population, toolbox, cxpb=0.5, mutpb=0.2, ngen=10, verbose=False)

# Find best individual
top_individual = tools.selBest(result_population, k=1)[0]
best_C, best_gamma = top_individual
print(f"\nBest Parameters found by GA: C={best_C:.4f}, gamma={best_gamma:.4f}")

# Step 5: Evaluate best model
best_model = SVC(C=best_C, gamma=best_gamma, kernel='rbf', random_state=42)
best_model.fit(X_train, y_train)
y_pred = best_model.predict(X_test)

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Non-Stroke", "Stroke"]))

accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")

# Step 6: Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print("\nConfusion Matrix:")
print(cm)

# Step 7: Recall
total_recall = recall_score(y_test, y_pred)
print(f"Total Recall: {total_recall:.2f}")
