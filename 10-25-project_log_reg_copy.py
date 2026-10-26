import pandas as pd

df = pd.read_csv('emails.csv')

print(df.head())
print(df["label"].value_counts())

#splits
X = df[["sender", "subject", "snippet"]]
y = df["label"]

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(X_train.shape)
print(X_test.shape)

#tfidf
from sklearn.feature_extraction.text import TfidfVectorizer

#fit_transform() look trough training subjects, build vocab, calculate how common each word is across them (term freq and inverse doc freq) learn and converts
#transform() for the test set ONLY converts into numbers using fit's learns
#we have the number forms of it now!!
subject_vectorizer = TfidfVectorizer()
subject_train = subject_vectorizer.fit_transform(X_train["subject"])
subject_test = subject_vectorizer.transform(X_test["subject"])

snippet_vectorizer = TfidfVectorizer()
snippet_train = snippet_vectorizer.fit_transform(X_train["snippet"])
snippet_test = snippet_vectorizer.transform(X_test["snippet"])

sender_vectorizer = TfidfVectorizer()
sender_train = sender_vectorizer.fit_transform(X_train["sender"])
sender_test = sender_vectorizer.transform(X_test["sender"])

#making into one feature matrix
from scipy.sparse import hstack

X_train_features = hstack([sender_train, subject_train, snippet_train])
X_test_features = hstack([sender_test, subject_test, snippet_test])

#logistic regression
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(max_iter=1000)
model.fit(X_train_features, y_train)

y_pred = model.predict(X_test_features)

#metrics
from sklearn.metrics import accuracy_score, confusion_matrix

print("Accuracy:", accuracy_score(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

#inspection
missed_news = X_test[(y_test == 1) & (y_pred == 0)]
print(missed_news.head())

for subject in missed_news["subject"]:
    print(subject)

y_proba = model.predict_proba(X_test_features)
print(y_proba[:5])

results = X_test.copy()
results["actual"] = y_test
results["probability_1"] = y_proba[:, 1]

missed_results = results[(results["actual"] == 1) & (results["probability_1"] < 0.5)]
print(missed_results[["subject", "probability_1"]].to_string(index=False))

correct_results = results[(results["actual"] == 0)].sort_values("probability_1", ascending=False)
print(correct_results[["subject", "probability_1"]].to_string(index=False))

#cross-validation
#col transfo
from sklearn.compose import ColumnTransformer

#each tuple contains name, transformer, and what col to apply to so its a list of what to do to each column
preprocessor = ColumnTransformer([
    ("subject_tfidf", TfidfVectorizer(), "subject"),
    ("snippet_tfidf", TfidfVectorizer(), "snippet"),
    ("sender_tfidf", TfidfVectorizer(), "sender")
])

#pipeline
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(max_iter=1000))
])

#stratified
from sklearn.model_selection import StratifiedKFold
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

from sklearn.model_selection import cross_validate

scores = cross_validate(pipeline, X_train, y_train, cv=cv, scoring=["accuracy", "precision", "recall"])
print("Precision:", scores["test_precision"])
print("Recall:", scores["test_recall"])
print("Accuracy:", scores["test_accuracy"])

from sklearn.model_selection import cross_val_predict
cv_predictions = cross_val_predict(
    pipeline, X_train, y_train, cv=cv
)

false_positives = X_train[
    (y_train == 0) & (cv_predictions == 1)
]

print(false_positives.to_string(index=False))