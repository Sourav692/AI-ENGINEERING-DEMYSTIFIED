"""
CampusX DSMP 2.0 — ML Roadmap Notion Database Creator
=======================================================
Prerequisites:
  pip install requests

Setup:
  1. Go to https://www.notion.so/my-integrations → create a new integration → copy the secret key
  2. Open the Notion page where you want the database → click ••• → Connections → add your integration
  3. Copy the page ID from the URL: notion.so/<workspace>/<PAGE_ID>?v=...
  4. Paste both values below and run: python notion_roadmap.py
"""

import requests
import json

# ── CONFIG ──────────────────────────────────────────────────────────────────
NOTION_API_KEY = "ntn_i74658943132aYIH9C3QL3B6G9H4vj2lJlA5cnWn0ky1yG"   # ntn_xxxxxxxxxxxxxxx
PARENT_PAGE_ID = "33f1bd0081a9807891e1f8afecc8c8db"              # 32-char hex from URL
# ────────────────────────────────────────────────────────────────────────────

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

# ── ROADMAP DATA ─────────────────────────────────────────────────────────────
# Each entry: (phase, topic, subtopics, week_section, status)
ROADMAP = [
    # Phase 1 — Python & programming foundations
    ("Phase 1 — Python & programming foundations", "Python basics",
     "About Python · print/output · data types · variables · comments · keywords & identifiers · user input · type conversion · literals",
     "Week 1 · Session 1", "Not started"),
    ("Phase 1 — Python & programming foundations", "Operators, if-else & loops",
     "Python operators · if-else · modules · while loop · for loop",
     "Week 1 · Session 2", "Not started"),
    ("Phase 1 — Python & programming foundations", "Strings & time complexity",
     "Loop problems · break/continue/pass · string indexing & slicing · edit/delete strings · string operations & functions · time complexity: orders of growth",
     "Week 1 · Session 3", "Not started"),
    ("Phase 1 — Python & programming foundations", "Lists, tuples, sets & dictionaries",
     "Array vs list · memory storage · append/extend/insert · list comprehension · zip() · set operations · frozen set · dictionary comprehension · tuple unpacking · nested comprehension",
     "Week 2 · Sessions 4–5", "Not started"),
    ("Phase 1 — Python & programming foundations", "Functions",
     "Arguments/parameters · args & kwargs · memory execution · variable scope · nested functions · first-class functions · lambda · higher-order functions · map/filter/reduce",
     "Week 2 · Session 6", "Not started"),
    ("Phase 1 — Python & programming foundations", "OOP (Parts 1–3) + Abstraction",
     "Classes & objects · dunder/magic methods · constructor · self · Fraction class · encapsulation · reference variables · mutability · static variables/methods · aggregation · inheritance (single, multilevel, hierarchical, multiple, hybrid) · diamond problem · polymorphism · method overriding/overloading · operator overloading · abstract classes",
     "Week 3 · Sessions 7–9", "Not started"),
    ("Phase 1 — Python & programming foundations", "File handling & serialization",
     "File I/O · open() · append · read/readline · context manager with() · reading big files · seek/tell · binary files · JSON dump/load · pickling · pickle vs JSON",
     "Week 4 · Session 10", "Not started"),
    ("Phase 1 — Python & programming foundations", "Exception handling",
     "Syntax error · exceptions · try-except-else-finally · handling specific errors · raise · custom exceptions",
     "Week 4 · Session 11", "Not started"),
    ("Phase 1 — Python & programming foundations", "Decorators & namespaces",
     "Namespaces · scope & LEGB rule · local/enclosing/global/built-in scope · decorators with examples",
     "Week 4 · Session 12", "Not started"),
    ("Phase 1 — Python & programming foundations", "Iterators & generators",
     "Iterators vs iterables · how for loop works · custom for loop · custom range function · generators · yield vs return · generator expressions · benefits of generators",
     "Week 4 · Bonus", "Not started"),

    # Phase 2 — Numpy & Pandas
    ("Phase 2 — Data libraries: Numpy & Pandas", "Numpy fundamentals",
     "Numpy array · matrix · array attributes · scalar & vector operations · dot product · log/exp/mean/median/std/prod/min/max/trig/variance/ceil/floor · slicing · reshaping · stacking & splitting",
     "Week 5 · Session 13", "Not started"),
    ("Phase 2 — Data libraries: Numpy & Pandas", "Advanced Numpy & tricks",
     "Numpy array vs Python list · advanced/fancy/boolean indexing · broadcasting · sigmoid & MSE in numpy · missing values · sort, append, concatenate, percentile, flip, set functions",
     "Week 5 · Sessions 14–15", "Not started"),
    ("Phase 2 — Data libraries: Numpy & Pandas", "Pandas Series",
     "Introduction to Series · Series methods & math methods · Python functionalities on Series · boolean indexing · plotting on Series",
     "Week 6 · Session 16", "Not started"),
    ("Phase 2 — Data libraries: Numpy & Pandas", "Pandas DataFrame",
     "Creating DataFrame · read_csv() · attributes & methods · math methods · selecting cols/rows · filtering · adding columns · astype() · sort, reset_index, isnull, dropna, fillna, drop_duplicates, value_counts, apply",
     "Week 6–7 · Sessions 17–18", "Not started"),
    ("Phase 2 — Data libraries: Numpy & Pandas", "Advanced Pandas",
     "GroupBy: builtin aggregation, attributes & methods, IPL dataset · concat, merge, join methods",
     "Week 7 · Sessions 19–20", "Not started"),
    ("Phase 2 — Data libraries: Numpy & Pandas", "Pandas continued",
     "MultiIndex Series & DataFrames · stacking/unstacking · transpose · swaplevel · long vs wide data · melt · pivot table · agg functions · vectorized string operations · Pandas datetime · time series case study · textual data case study",
     "Week 8 · Sessions 21–22", "Not started"),

    # Phase 3 — Data visualization
    ("Phase 3 — Data visualization", "Matplotlib",
     "Simple functions, labels, legends, multiple plots · scatter, bar, histogram, pie · styles · colored scatterplot · plot size, annotations · subplots · 3D plots · contour plots · heatmaps · Pandas plot()",
     "Week 9 · Sessions 23–24", "Not started"),
    ("Phase 3 — Data visualization", "Seaborn",
     "Relational plots · distribution plots · KDE plot · matrix plot · categorical plots: stripplot, swarmplot, boxplot, violinplot · barplot, pointplot, countplot · catplot · faceting · regression plots: regplot, lmplot, residual · FacetGrid · pairplot/pairgrid · jointgrid/jointplot",
     "Week 10 · Sessions 25–26", "Not started"),
    ("Phase 3 — Data visualization", "Plotly & Dash",
     "Plotly Express · Plotly Graph Objects · Dash basics · COVID-19 dashboard · deploying on Heroku · Indian Census geospatial project",
     "Week 9–10 · Bonus", "Not started"),

    # Phase 4 — Data analysis process
    ("Phase 4 — Data analysis process", "Data gathering",
     "Data analysis process overview · import from CSV/Excel/JSON/text/SQL · export formats · gather via API or web scraping · advanced web scraping with Selenium & Chromedriver",
     "Week 11 · Session 27", "Not started"),
    ("Phase 4 — Data analysis process", "Data assessing & cleaning",
     "Types of unclean data · write data summary · manual & automatic assessment · data quality dimensions · cleaning pipeline · quality & tidiness issues · smartphone dataset case study",
     "Weeks 11–12 · Session 28", "Not started"),
    ("Phase 4 — Data analysis process", "EDA",
     "Introduction to EDA · why EDA · steps for EDA · univariate analysis · bivariate analysis · feature engineering insights · EDA case study on smartphone dataset",
     "Week 12 · Session 29", "Not started"),

    # Phase 5 — SQL
    ("Phase 5 — SQL", "Database fundamentals",
     "Data & database intro · CRUD operations · database properties · types of databases · DBMS · keys · cardinality · drawbacks",
     "Week 13 · Session 30", "Not started"),
    ("Phase 5 — SQL", "DDL & DML commands",
     "DDL commands · INSERT, SELECT, UPDATE, DELETE · SQL functions · ORDER BY, GROUP BY (single & multiple columns) · HAVING clause · practice on IPL dataset",
     "Weeks 13–14 · Sessions 31–32", "Not started"),
    ("Phase 5 — SQL", "Joins & subqueries",
     "Cross, inner, left, right, full outer joins · SET operations · SELF join · query execution order · subqueries: independent & correlated · Zomato dataset case study · flight dashboard",
     "Week 15 · Sessions 34–35", "Not started"),
    ("Phase 5 — SQL", "Window functions",
     "OVER() · RANK, DENSE_RANK, ROW_NUMBER · FIRST_VALUE, LAST_VALUE · frames · LAG, LEAD · cumulative sum/average · running average · percent of total · percent change · quantiles/percentiles · segmentation · cumulative distribution · partition by multiple columns",
     "Week 16 · Sessions 36–37", "Not started"),
    ("Phase 5 — SQL", "SQL data cleaning, EDA & advanced SQL",
     "String functions · wildcards · data cleaning on laptop dataset · EDA: numerical & categorical · datetime functions · TIMESTAMP vs DATETIME · stored procedures · transactions: commit/rollback/savepoint · ACID properties · views · user-defined functions · database normalization · ER diagrams",
     "Week 16 · Bonus", "Not started"),

    # Phase 6 — Statistics & mathematics
    ("Phase 6 — Statistics & mathematics", "Descriptive statistics",
     "Types of statistics · population vs sample · types of data · central tendency · dispersion · coefficient of variation · univariate/bivariate graphs · frequency distribution · quantiles, percentiles, five-number summary · boxplots · scatterplots · covariance · correlation vs causation",
     "Weeks 17–18 · Sessions 38–39", "Not started"),
    ("Phase 6 — Statistics & mathematics", "Probability distributions",
     "Random variables · PMF · PDF · CDF · density estimation · parametric & non-parametric · KDE · normal distribution: equation/parameters/intuition · standard normal variate, z-table, empirical rule · skewness · kurtosis · QQ plot · uniform, log-normal, Pareto distributions",
     "Weeks 18–19 · Sessions 40–42", "Not started"),
    ("Phase 6 — Statistics & mathematics", "Feature transformations (stats context)",
     "Mathematical transformation · function transformer · log transform · reciprocal/square/sqrt transform · power transformer · Box-Cox transform · Yeo-Johnson transformation",
     "Week 19 · Session 42", "Not started"),
    ("Phase 6 — Statistics & mathematics", "Inferential statistics",
     "Bernoulli & Binomial distributions · sampling distribution · CLT: intuition, code, case study · confidence intervals: z-procedure, t-procedure, t-distribution · hypothesis testing: null/alternate hypothesis, z-test, rejection region, Type I/II errors, one/two-tailed · p-value · t-tests: single sample, independent 2-sample, paired · chi-square: GoF & independence tests · ANOVA: F-distribution, one-way, post-hoc",
     "Weeks 20–21 · Sessions 43–46", "Not started"),
    ("Phase 6 — Statistics & mathematics", "Linear algebra",
     "Tensors: 0D–5D, rank/axes/shape · vectors: Euclidean distance, scalar ops, dot product, angle, hyperplane equation · matrices: types, operations, transpose, determinant, minor, cofactor, adjoint, inverse · basis vectors · linear transformations · matrix multiplication as composition · eigenvectors & eigenvalues · eigen decomposition · SVD",
     "Week 22", "Not started"),

    # Phase 7 — Core ML: regression & optimization
    ("Phase 7 — Core ML: regression & optimization", "Intro to machine learning",
     "History & definition · supervised, unsupervised, semi-supervised, RL · batch/offline vs online learning · instance-based vs model-based · challenges: data collection, labelling, overfitting/underfitting · ML development lifecycle · job roles · framing a ML problem",
     "Week 23 · Session 48", "Not started"),
    ("Phase 7 — Core ML: regression & optimization", "Simple & multiple linear regression",
     "Intuition · finding m and b · code from scratch · MAE, MSE, RMSE, R², Adjusted R² · MLR: mathematical formulation, error function, minimizing error · differential calculus: power/sum/product/quotient/chain rules, partial differentiation, matrix differentiation",
     "Week 23 · Sessions 49–50", "Not started"),
    ("Phase 7 — Core ML: regression & optimization", "Gradient descent",
     "Intuition, math formulation · effect of learning rate, loss function, data · batch GD: math, code from scratch · stochastic GD: problems with batch, code, learning schedules · mini-batch GD · optimization big picture: convex/non-convex loss, parametric vs non-parametric",
     "Week 24 · Sessions 51–52", "Not started"),
    ("Phase 7 — Core ML: regression & optimization", "Regression analysis",
     "Inference vs prediction · statsmodel LR · TSS/RSS/ESS · degree of freedom · F-statistic · R² & Adjusted R² · t-statistic · CI for coefficients · polynomial regression · assumptions: linearity, normality of residuals, homoscedasticity, no autocorrelation, no multicollinearity · VIF, condition number",
     "Week 25 · Session 53", "Not started"),
    ("Phase 7 — Core ML: regression & optimization", "Feature selection",
     "Filter methods: duplicate features, variance threshold, correlation, ANOVA, chi-square · wrapper methods: exhaustive/best subset, sequential backward/forward selection · embedded methods: linear regression, tree-based, regularized models · RFE",
     "Week 26 · Sessions 54–55", "Not started"),
    ("Phase 7 — Core ML: regression & optimization", "Regularization",
     "Bias-variance tradeoff: expected value, variance, decomposition · Ridge (L2): geometric intuition, sklearn, 2D/nD data, gradient descent, 5 key understandings · Lasso (L1): intuition, why creates sparsity · ElasticNet",
     "Week 27", "Not started"),

    # Phase 8 — Classification algorithms
    ("Phase 8 — Classification algorithms", "KNN + classification metrics",
     "KNN intuition · how to select K · decision surface · overfitting/underfitting · KNN regressor · weighted KNN · Euclidean vs Manhattan distance · KD-tree · space/time complexity · accuracy, confusion matrix, Type I/II errors · precision, recall, F1 · multi-class metrics",
     "Week 28", "Not started"),
    ("Phase 8 — Classification algorithms", "Naive Bayes",
     "Probability crash course: Bayes theorem, conditional/joint/marginal probability · Gaussian NB · underflow & log probabilities · Laplace additive smoothing · Bernoulli, Categorical, Multinomial NB · out-of-core NB · email spam classifier project",
     "Week 31", "Not started"),
    ("Phase 8 — Classification algorithms", "Logistic regression",
     "Sigmoid function · maximum likelihood · log loss · gradient descent · multiclass: OVR, SoftMax · MLE in depth · probability vs likelihood · assumptions · odds & log(odds) · polynomial features · regularization in LR · hyperparameters",
     "Week 32", "Not started"),
    ("Phase 8 — Classification algorithms", "SVM",
     "Hard margin SVM: max margin classifier, support vectors, math formulation · soft margin: slack variable, C parameter, bias-variance tradeoff · kernel trick: polynomial, RBF, custom kernels · constrained optimization, KKT conditions · dual problem derivation · gamma effect",
     "Week 33", "Not started"),

    # Phase 9 — Dimensionality reduction & model evaluation
    ("Phase 9 — Dimensionality reduction & model evaluation", "PCA",
     "Curse of dimensionality · geometric intuition · covariance matrix · eigenvectors & eigenvalues · step-by-step PCA · MNIST practical example · explained variance · optimal components · when PCA fails · eigen decomposition · spectral decomposition · kernel PCA · SVD applications",
     "Week 29", "Not started"),
    ("Phase 9 — Dimensionality reduction & model evaluation", "ROC curve & cross-validation",
     "ROC AUC requirements · TPR & FPR · hold-out approach & its problems · LOOCV · K-fold CV · stratified K-fold · data leakage: detection & removal · validation set",
     "Week 30", "Not started"),
    ("Phase 9 — Dimensionality reduction & model evaluation", "Hyperparameter tuning",
     "Parameter vs hyperparameter · GridSearchCV · RandomizedSearchCV",
     "Week 30", "Not started"),
    ("Phase 9 — Dimensionality reduction & model evaluation", "Sklearn deep dive",
     "Estimators · custom estimators · mixins · transformers · custom transformer · composite transformers · ColumnTransformer · FeatureUnion · Pipeline",
     "Extra session", "Not started"),

    # Phase 10 — Tree-based models & ensembles
    ("Phase 10 — Tree-based models & ensembles", "Decision trees",
     "CART for classification & regression · Gini impurity · splitting categorical/numerical features · geometric intuition · feature importance · overfitting · pruning: pre-pruning, post-pruning, cost complexity pruning · dtreeviz demo",
     "Week 34", "Not started"),
    ("Phase 10 — Tree-based models & ensembles", "Bagging & random forest",
     "Ensemble learning intuition · types & benefits · bagging: classifier & regressor · random forest: intuition, why it works, bagging vs RF · feature importance · OOB score · extremely randomized trees · hyperparameters",
     "Week 35", "Not started"),
    ("Phase 10 — Tree-based models & ensembles", "Gradient boosting",
     "Boosting intuition · function space vs parameter space · direction of loss minimization · how to update function · vs gradient descent · classification: geometric intuition · math: F0(x), pseudo residuals, regression tree training, lambda for leaf nodes, update model, log(odds) vs probability",
     "Week 36", "Not started"),

    # Phase 11 — XGBoost (introductory)
    ("Phase 11 — XGBoost (introductory)", "XGBoost for regression & classification",
     "Introduction: features, performance, speed, flexibility · regression problem statement: step-by-step mathematical calculation · classification problem statement: step-by-step mathematical calculation",
     "Post Week 36", "Not started"),
    ("Phase 11 — XGBoost (introductory)", "Complete maths of XGBoost",
     "Boosting as additive model · XGBoost loss function · deriving objective function · Taylor series · applying Taylor series · simplification · output value for regression & classification · derivation of similarity score · final calculation of similarity score",
     "Post Week 36", "Not started"),
    ("Phase 11 — XGBoost (introductory)", "Capstone project",
     "Data gathering (real estate dataset) · merging house & flats data · feature engineering: additionalRoom, areaWithType, agePossession, furnishDetails, luxuryScore · univariate & multivariate EDA · outlier detection & removal · missing value imputation · feature selection: correlation, RF/GBM importance, permutation, LASSO, RFE, SHAP · encoding: OHE, ordinal, OHE+PCA, target · pipelines: LR, SVR · price prediction Streamlit UI · analytics module · recommender system · deploy on AWS",
     "Capstone Sessions 1–13", "Not started"),

    # Phase 12 — Advanced XGBoost
    ("Phase 12 — Advanced XGBoost", "Revisiting XGBoost",
     "Supervised ML recap · stagewise additive modelling · XGBoost objective function",
     "Adv. XGBoost · Session 1", "Not started"),
    ("Phase 12 — Advanced XGBoost", "XGBoost regularization",
     "Ways to reduce overfitting · gamma · max depth · num estimators · early stopping · shrinkage · min child weight · lambda (L2) & alpha (L1) · subsample · col subsample (colsample_bytree)",
     "Adv. XGBoost · Sessions 2–3", "Not started"),
    ("Phase 12 — Advanced XGBoost", "XGBoost optimizations",
     "Reason for slowness in boosting · exact greedy split finding · approximate method for split finding · reduces no. of splits · calculation of G and H · parallel processing · cache storage · quantile sketch · weighted quantile sketch",
     "Adv. XGBoost · Session 4", "Not started"),
    ("Phase 12 — Advanced XGBoost", "Handling missing values in XGBoost",
     "XGBoost's native missing value handling mechanism",
     "Adv. XGBoost · Session 5", "Not started"),

    # Phase 13 — Unsupervised learning
    ("Phase 13 — Unsupervised learning", "K-means clustering",
     "Geometric intuition · elbow method · assumptions & limitations · silhouette score · K-means++ initialization · hyperparameters: k, init method, n_init, max_iter, tol · Lloyd's algorithm · time & space complexity · mini-batch K-means",
     "Unsupervised block", "Not started"),
    ("Phase 13 — Unsupervised learning", "DBSCAN",
     "Density-based clustering · MinPts & epsilon · core/border/noise points · density connected points · DBSCAN algorithm · limitations · visualization",
     "Unsupervised block", "Not started"),
    ("Phase 13 — Unsupervised learning", "Hierarchical clustering",
     "Agglomerative algorithm · types: min (single-link), max (complete-link), average, Ward · finding ideal number of clusters · hyperparameters · benefits/limitations",
     "Unsupervised block", "Not started"),
    ("Phase 13 — Unsupervised learning", "Gaussian Mixture Models",
     "Geometric intuition · multivariate normal distribution · EM algorithm · covariance types: spherical, diagonal, full, tied · AIC & BIC for n_components · likelihood formula · K-means vs GMM · DBSCAN vs GMM · applications",
     "Unsupervised block", "Not started"),
    ("Phase 13 — Unsupervised learning", "T-SNE",
     "Geometric intuition · mathematical formulation · why probabilities over distances · why Gaussian in high dims · variance calculation · why t-distribution in lower dims · hyperparameters: perplexity, learning rate, iterations",
     "Unsupervised block", "Not started"),
    ("Phase 13 — Unsupervised learning", "LDA & Apriori",
     "LDA: supervised dimensionality reduction, maximizing between-class variance, comparison with PCA · Apriori: association rule mining, support/confidence/lift, candidate generation, pruning, market basket analysis",
     "Unsupervised block", "Not started"),

    # Phase 14 — Feature engineering (extra sessions)
    ("Phase 14 — Feature engineering (extra sessions)", "Handling missing values",
     "MCAR, MAR, MNAR · impact on ML models · removing missing data · mean/median/mode/constant/arbitrary/end-distribution imputation · missing indicator · KNN imputer · iterative imputer (MICE) · comparison framework",
     "Extra sessions", "Not started"),
    ("Phase 14 — Feature engineering (extra sessions)", "Encoding categorical features",
     "Ordinal encoding · label encoding · OHE · handling unknown/rare categories · LabelBinarizer · count/frequency encoder · binary encoder · target encoder · weight of evidence · ColumnTransformer · sklearn Pipeline",
     "Extra sessions", "Not started"),
    ("Phase 14 — Feature engineering (extra sessions)", "Discretization",
     "Why discretization · reducing overfitting · handling non-linear relationships · uniform binning · quantile binning · K-means binning · decision tree-based binning · custom binning · threshold binning (binarization)",
     "Extra sessions", "Not started"),
    ("Phase 14 — Feature engineering (extra sessions)", "Feature scaling",
     "Why scaling · algorithms affected vs not · standardization · MinMax scaling · Robust scaler · MaxAbsolute scaler · L1/L2 normalization · comparison",
     "Extra sessions", "Not started"),
    ("Phase 14 — Feature engineering (extra sessions)", "Outlier detection",
     "Types of outliers · impact · z-score, IQR/boxplot · Isolation Forest (anomaly score) · KNN-based outlier detection · local vs global outliers · LOF · DBSCAN for outliers · when to use which algorithm",
     "Extra sessions", "Not started"),
    ("Phase 14 — Feature engineering (extra sessions)", "Feature transformation",
     "Why transformations · log transformation: when to/not to use · square root · reciprocal · square · Box-Cox · Yeo-Johnson · Boston Housing case study",
     "Extra sessions", "Not started"),

    # Phase 15 — Competitive data science
    ("Phase 15 — Competitive data science", "AdaBoost",
     "Intuition · weak learners · weight updating · final weighted model · hyperparameters: learning rate, n_estimators · applications in classification & regression",
     "Competitive DS", "Not started"),
    ("Phase 15 — Competitive data science", "Stacking",
     "Model ensembling concept · base models → meta-model → final prediction · variations & modifications · best practices for effective stacking",
     "Competitive DS", "Not started"),
    ("Phase 15 — Competitive data science", "LightGBM",
     "Introduction & core features · histogram-based split finding · leaf-wise growth strategy · GOSS (gradient-based one-side sampling) · EFB (exclusive feature bundling)",
     "Competitive DS", "Not started"),
    ("Phase 15 — Competitive data science", "CatBoost",
     "Introduction · advantages & technical aspects · practical implementation on Medical Cost dataset",
     "Competitive DS", "Not started"),
    ("Phase 15 — Competitive data science", "Advanced hyperparameter tuning",
     "Bayesian optimization · Optuna · Hyperopt · practical tips: efficient tuning, avoiding overfitting · robust model evaluation",
     "Competitive DS", "Not started"),
    ("Phase 15 — Competitive data science", "Kaggle competition",
     "Understanding the problem · exploring datasets · model selection & preprocessing · validation strategy · teamwork & collaboration · effective submissions · learning from feedback",
     "Competitive DS", "Not started"),

    # Phase 16 — Miscellaneous & tooling
    ("Phase 16 — Miscellaneous & tooling", "NoSQL",
     "Overview · types: document, key-value, column-family, graph · when NoSQL over SQL · MongoDB, Cassandra, Redis, Neo4j",
     "Miscellaneous", "Not started"),
    ("Phase 16 — Miscellaneous & tooling", "Model explainability",
     "Importance of interpretable models · LIME · SHAP · feature importance · applying to various models",
     "Miscellaneous", "Not started"),
    ("Phase 16 — Miscellaneous & tooling", "FastAPI",
     "Modern fast web framework · type checking, automatic validation, documentation · building APIs · deployment: hosting & scaling",
     "Miscellaneous", "Not started"),
    ("Phase 16 — Miscellaneous & tooling", "AWS Sagemaker",
     "Fully managed ML service · model building, training, deployment · workflow: data preprocessing to deployment · optimizing costs & performance",
     "Miscellaneous", "Not started"),
    ("Phase 16 — Miscellaneous & tooling", "Handling imbalanced data",
     "Problem with imbalanced data · undersampling: random, Tomek links, ENN, NCR, cluster centroids · oversampling: random, SMOTE, Borderline SMOTE, ADASYN, SVM SMOTE, SMOTENC · class weighting · cost-sensitive learning · threshold tuning",
     "Miscellaneous", "Not started"),
]


def create_database(parent_page_id: str) -> str:
    """Create the Notion database with the required schema and return its ID."""
    url = "https://api.notion.com/v1/databases"
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "icon": {"type": "emoji", "emoji": "📚"},
        "title": [{"type": "text", "text": {"content": "CampusX DSMP 2.0 — ML Roadmap"}}],
        "properties": {
            "Topic": {"title": {}},
            "Phase": {
                "select": {
                    "options": [
                        {"name": "Phase 1 — Python & programming foundations",  "color": "purple"},
                        {"name": "Phase 2 — Data libraries: Numpy & Pandas",    "color": "green"},
                        {"name": "Phase 3 — Data visualization",                "color": "green"},
                        {"name": "Phase 4 — Data analysis process",             "color": "blue"},
                        {"name": "Phase 5 — SQL",                               "color": "blue"},
                        {"name": "Phase 6 — Statistics & mathematics",          "color": "blue"},
                        {"name": "Phase 7 — Core ML: regression & optimization","color": "orange"},
                        {"name": "Phase 8 — Classification algorithms",         "color": "orange"},
                        {"name": "Phase 9 — Dimensionality reduction & model evaluation", "color": "blue"},
                        {"name": "Phase 10 — Tree-based models & ensembles",    "color": "pink"},
                        {"name": "Phase 11 — XGBoost (introductory)",           "color": "pink"},
                        {"name": "Phase 12 — Advanced XGBoost",                 "color": "yellow"},
                        {"name": "Phase 13 — Unsupervised learning",            "color": "green"},
                        {"name": "Phase 14 — Feature engineering (extra sessions)", "color": "orange"},
                        {"name": "Phase 15 — Competitive data science",         "color": "gray"},
                        {"name": "Phase 16 — Miscellaneous & tooling",          "color": "gray"},
                    ]
                }
            },
            "Subtopics": {"rich_text": {}},
            "Week / Section": {"rich_text": {}},
            "Status": {
                "status": {
                    "options": [
                        {"name": "Not started", "color": "default"},
                        {"name": "In progress",  "color": "yellow"},
                        {"name": "Completed",    "color": "green"},
                        {"name": "Revisit",      "color": "orange"},
                    ],
                    "groups": [
                        {"name": "To-do",       "color": "gray",   "option_ids": []},
                        {"name": "In progress", "color": "blue",   "option_ids": []},
                        {"name": "Complete",    "color": "green",  "option_ids": []},
                    ]
                }
            },
        },
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    db_id = resp.json()["id"]
    print(f"✅ Database created: {db_id}")
    return db_id


def add_row(db_id: str, phase: str, topic: str, subtopics: str, week: str, status: str):
    """Add a single row (page) to the database."""
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": db_id},
        "properties": {
            "Topic":          {"title":     [{"text": {"content": topic}}]},
            "Phase":          {"select":    {"name": phase}},
            "Subtopics":      {"rich_text": [{"text": {"content": subtopics}}]},
            "Week / Section": {"rich_text": [{"text": {"content": week}}]},
            "Status":         {"status":    {"name": status}},
        },
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    resp.raise_for_status()


def main():
    if NOTION_API_KEY == "your_notion_integration_secret_here":
        print("❌  Please set NOTION_API_KEY and PARENT_PAGE_ID before running.")
        return

    print("Creating database...")
    db_id = create_database(PARENT_PAGE_ID)

    print(f"Adding {len(ROADMAP)} rows...")
    for i, (phase, topic, subtopics, week, status) in enumerate(ROADMAP, 1):
        add_row(db_id, phase, topic, subtopics, week, status)
        print(f"  [{i:02d}/{len(ROADMAP)}] {topic}")

    print(f"\n🎉 Done! Open Notion and look for 'CampusX DSMP 2.0 — ML Roadmap' on your page.")


if __name__ == "__main__":
    main()