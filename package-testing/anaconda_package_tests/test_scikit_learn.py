"""
:Abstract: Test cases to validate the Sciki-Learn and scipy packages.
:Copyright:
            BSD 3-Clause License

            Copyright (c) 2007-2021 The scikit-learn developers.
            All rights reserved.

            Redistribution and use in source and binary forms, with or without
            modification, are permitted provided that the following conditions are met:

            * Redistributions of source code must retain the above copyright notice, this
              list of conditions and the following disclaimer.

            * Redistributions in binary form must reproduce the above copyright notice,
              this list of conditions and the following disclaimer in the documentation
              and/or other materials provided with the distribution.

            * Neither the name of the copyright holder nor the names of its
              contributors may be used to endorse or promote products derived from
              this software without specific prior written permission.

            THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
            AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
            IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
            DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
            FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
            DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
            SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
            CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
            OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
            OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import csv
import logging
import os
from time import time

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.sparse import csr_matrix
from sklearn import svm
from sklearn.datasets import fetch_20newsgroups
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_selection import VarianceThreshold
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split

n_samples = 2000
n_features = 1000
n_components = 10
n_top_words = 20

logger = logging.getLogger(__name__)


# Helper Methods fot the test validations.


def load_csv_data():
    """
    This method is used to load the iris data set to use for scikit learn package.
    """
    file_path = "test_data/iris.csv"
    test_report_file = os.path.abspath(os.path.join(os.path.dirname(__file__), file_path))
    with open(test_report_file) as csv_file:
        data_file = csv.reader(csv_file)
        temp = next(data_file)
        n_samples = int(temp[0])
        n_features = int(temp[1])
        target_names = np.array(temp[2:])
        data = np.empty((n_samples, n_features))
        target = np.empty((n_samples,), dtype=int)
        for i, ir in enumerate(data_file):
            data[i] = np.asarray(ir[:-1], dtype=np.float64)
            target[i] = np.asarray(ir[-1], dtype=int)

    return data, target, target_names


def vectorize_dataset():
    """
     This method is used to Load the 20 newsgroups dataset and vectorize it.
     the posts are stripped of headers, footers and quoted replies, and
     common English words, words occurring in
    only one document or in at least 95% of the documents are removed
    """
    logging.info("Loading dataset")
    # scikit learn package testing logic
    t0 = time()
    data, _ = fetch_20newsgroups(
        shuffle=True,
        random_state=1,
        remove=("headers", "footers", "quotes"),
        return_X_y=True,
    )
    data_samples = data[:n_samples]
    logging.info("done in %0.3fs." % (time() - t0))
    # Use tf-idf features for NMF.
    logging.info("Extracting tf-idf features for NMF...")
    tfidf_vectorizer = TfidfVectorizer(
        max_df=0.95, min_df=2, max_features=n_features, stop_words="english"
    )
    t0 = time()
    tfidf = tfidf_vectorizer.fit_transform(data_samples)
    logging.info("done in %0.3fs." % (time() - t0))

    # Use tf (raw term count) features for LDA.
    logging.info("Extracting tf features for LDA...")
    tf_vectorizer = CountVectorizer(
        max_df=0.95, min_df=2, max_features=n_features, stop_words="english"
    )
    t0 = time()
    tf = tf_vectorizer.fit_transform(data_samples)
    logging.info("done in %0.3fs." % (time() - t0))
    return tfidf, tfidf_vectorizer, tf_vectorizer, tf


def extract_top_words_by_feature_extraction_method(
    model, feature_names, n_top_words, title, file_name
):
    """
    This method contain the logic to plot the graph for Top words being used in the document.
    Params:
    MODEL: model used to plot the data.
    feature_names:
    n_top_words: features being used
    """
    # Plotting by using the plot data and assertions.
    fig, axes = plt.subplots(2, 5, figsize=(30, 15), sharex=True)
    axes = axes.flatten()
    for topic_idx, topic in enumerate(model.components_):
        top_features_ind = topic.argsort()[:(-21):-1]
        top_features = [feature_names[i] for i in top_features_ind]
        weights = topic[top_features_ind]

        ax = axes[topic_idx]
        ax.barh(top_features, weights, height=0.7)
        ax.set_title(f"Topic {topic_idx + 1}", fontdict={"fontsize": 30})
        ax.invert_yaxis()
        ax.tick_params(axis="both", which="major", labelsize=20)
        for i in "top right left".split():
            ax.spines[i].set_visible(False)
        fig.suptitle(title, fontsize=40)
    fig.savefig(file_name)
    plt.close(fig)

    # Assertions.
    try:
        im = Image.open(file_name)
        assert im.format.lower() == "png", "unable to assert the plotted data"
    except OSError as message:
        logging.info(f"Error being raised {message}")


# Scikit-learn package use cases.


def test_feature_selection():
    """
    To find out the lowest variance and remove features with low variance
    Expected result:
    To remove the first column which has the probability p = 5/6 > .8 of containing the zero.
    """
    # Test data
    training_data = [[0, 0, 1], [0, 1, 0], [1, 0, 0], [0, 1, 1], [0, 1, 0], [0, 1, 1]]

    # Package logic being tested.
    for data in [training_data, csr_matrix(training_data)]:
        selector = VarianceThreshold(threshold=(0.8 * (1 - 0.8)))
        actual_data = selector.fit_transform(data)
        expected_array_len = len(training_data)
        # Assertions
        assert (expected_array_len, 2) == actual_data.shape, (
            f"failed to validate the scikit learn package"
            f" feature_Selection test , actual data returned "
            f"{actual_data}"
        )


def test_confusion_matrix():
    """
    To normalize the confuse matrix
    train_test_split : Utility function to split the data into a development
        set usable for fitting a GridSearchCV instance and an evaluation set
        for its final evaluation.
    Document to refer the use case:
    https://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html#sphx-glr-auto-
    examples-model-selection-plot-confusion-matrix-py


    """
    # Test data
    iris = load_csv_data()
    data = iris[0]
    target = iris[1]
    target_names = iris[2]
    # Split the data into a training set and a test set
    data_train, data_test, target_train, target_test = train_test_split(
        data, target, random_state=0
    )

    # Run classifier, using a model that is too regularized (C too low) to see
    # the impact on the results
    # Logic being tested from the package
    classifier = svm.SVC(kernel="linear", C=0.01).fit(data_train, target_train)
    np.set_printoptions(precision=2)

    # Plot non-normalized confusion matrix
    titles_options = [
        ("Confusion matrix, without normalization", None),
        ("Normalized confusion matrix", "true"),
    ]
    for title, normalize in titles_options:
        disp = ConfusionMatrixDisplay.from_estimator(
            classifier,
            data_test,
            target_test,
            display_labels=target_names,
            cmap=plt.cm.Blues,
            normalize=normalize,
        )
        disp.ax_.set_title(title)
        array_1 = title
        array_2 = disp.confusion_matrix
        # Assertions/Validation on the normalized matrix with standardization
        # and without standardization.
        array_ = np.array(array_2)
        indices = [0, 1, 2]
        m = range(0, array_.shape[0])
        for b in zip(m, indices):
            if "without normalization" in array_1:
                if b == (0, 0):
                    assert (
                        array_[b] == 13
                    ), "Failed to validate the confuse matrix without normalization"
                elif b == (1, 1):
                    assert (
                        array_[b] == 10
                    ), "Failed to validate the confuse matrix without normalization"
            else:
                if b == (0, 0):
                    assert (
                        array_[b] == 1.0
                    ), "Failed to validate the confuse matrix with normalization"
                elif b == (2, 2):
                    assert (
                        array_[b] == 1.0
                    ), "Failed to validate the confuse matrix with normalization"


def test_nmf_model():
    """
    This test is used to validate the nmf model validation for scikit learn package.
    REF document:
    https://scikit-learn.org/stable/auto_examples/applications/plot_topics_extraction_with_nmf_lda.html#
    """

    logging.info(f'{"Fitting the NMF model (Frobenius norm) with tf-idf features"}')
    # calling vectorize_dataset method to test package functionality.
    t0 = time()
    vectorize_dataset_out_put = vectorize_dataset()
    tfidf = vectorize_dataset_out_put[0]
    tfidf_vectorizer = vectorize_dataset_out_put[1]
    nmf = NMF(n_components=n_components, random_state=1, alpha=0.1, l1_ratio=0.5).fit(tfidf)
    logging.info("done in %0.3fs." % (time() - t0))
    tfidf_feature_names = tfidf_vectorizer.get_feature_names_out()

    # Generating plot using the data generated from pkg module and doing assertions.
    extract_top_words_by_feature_extraction_method(
        nmf,
        tfidf_feature_names,
        n_top_words,
        "Topics in NMF model (Frobenius norm)",
        "Frobenius_norm_O_P.png",
    )


def test_generalized_divergent_nmf_model():
    """
    This test is to validate the genralized nmf model.
    REF document:
    https://scikit-learn.org/stable/auto_examples/applications/plot_topics_extraction_with_nmf_lda.html#
    """
    logging.info(
        f'{"Fitting the NMF model (generalized Kullback-Leibler divergence) with tf-idf features"}',
    )
    # calling vectorize_dataset method to test package functionality.
    t0 = time()
    vectorize_dataset_out_put = vectorize_dataset()
    tfidf = vectorize_dataset_out_put[0]
    tfidf_vectorizer = vectorize_dataset_out_put[1]

    nmf = NMF(
        n_components=n_components,
        random_state=1,
        beta_loss="kullback-leibler",
        solver="mu",
        max_iter=1000,
        alpha=0.1,
        l1_ratio=0.5,
    ).fit(tfidf)
    logging.info("done in %0.3fs." % (time() - t0))
    tfidf_feature_names = tfidf_vectorizer.get_feature_names_out()
    # Generating plot using the data generated from pkg module and doing assertions.
    extract_top_words_by_feature_extraction_method(
        nmf,
        tfidf_feature_names,
        n_top_words,
        "Topics in NMF model (generalized Kullback-Leibler divergence)",
        "Kullback_Leibler_O_P.png",
    )


def test_lda_model():
    """
    This test is to validate the lda model.
    REF document:
    https://scikit-learn.org/stable/auto_examples/applications/plot_topics_extraction_with_nmf_lda.html#
    """
    logging.info(f'{"Fitting LDA models with tf features"}')
    # calling vectorize_dataset and other methods to test package functionality.
    lda = LatentDirichletAllocation(
        n_components=n_components,
        max_iter=5,
        learning_method="online",
        learning_offset=50.0,
        random_state=0,
    )
    t0 = time()
    vectorize_dataset_out_put = vectorize_dataset()
    tf = vectorize_dataset_out_put[3]
    tf_vectorizer = vectorize_dataset_out_put[2]
    lda.fit(tf)
    logging.info("done in %0.3fs." % (time() - t0))
    tf_feature_names = tf_vectorizer.get_feature_names_out()
    # Generating plot using the data generated from pkg module and doing assertions.
    extract_top_words_by_feature_extraction_method(
        lda, tf_feature_names, n_top_words, "Topics in LDA model", "LDA.png"
    )
