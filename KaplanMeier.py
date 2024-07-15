import random
import numpy as np
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt
from scipy.stats import gamma, norm
import matplotlib
matplotlib.use('Agg')
import copy


def KaplanMeier_fit(samples,rpt_limits):
    """
    This is an extended usage of Kaplan-Meier (KM) method. Typically, the KM
    method is employed for survival curve estimation. In environmental studies,
    it has been adopted to estimate the mean, median, and standard deviation of
    a (left-) censored dataset. In this case, the obtained survival curve is adopted
    as a threshold curve for a random generator to estimated left-censored data points.

    Note: The KM method is invalid (same as substitution) if all the samples have the
    same LOD value. In my case, if all the samples have the sampe LOD, the turncation
    function will become a pure random generator.

    :param samples:
    :param rpt_limits:
    :return:
    """

    kmf = KaplanMeierFitter()
    # 1 -> normal, 0 -> left-censored. The annotation in the lifelines package seems incorrect.
    kmf.fit_left_censoring(samples, event_observed=np.where(samples > rpt_limits, 1, 0))

    return kmf


def gen_sample(kmf,limit):
    """
    Logic: for a given survival curve, if a random generated loc (0,LOD) has
    a lower survival value on the curve, it will much more easier for it to be kept.

    :param kmf: the fitted KaplanMeierFitter object
    :param limit: LOD value
    :return:
    """
    while True:
        loc = random.random() * limit
        threshold = float(kmf.survival_function_at_times(loc).iloc[0])
        sur = random.random()
        if sur >= threshold:
            return loc


def turncation(kmf, samples , rpt_limits):
    samples = samples.reshape(-1,1)
    for i,s in enumerate(samples):
        if s <= rpt_limits[i]:
            new_val = gen_sample(kmf,rpt_limits[i])
            samples[i] = new_val
    return samples

if __name__ == "__main__":
    # generate samples from normally distribution
    size = 1000
    model_shape, model_scale = 4.0, 2.0
    samples = gamma.rvs(model_shape, loc = 0,scale=model_scale, size=size)

    # set censoring limits
    lower_limit = np.random.randint(2,4,1000)

    args = np.where(samples <= lower_limit)

    left_censored_array = np.full(len(samples[samples <= lower_limit]), lower_limit[args])
    #left_censored_array = lower_limit

    uncensored_array = samples[samples > lower_limit]
    censored = np.concatenate((left_censored_array, uncensored_array))

    kmf = KaplanMeier_fit(censored, lower_limit)
    new_samples = turncation(kmf, copy.copy(censored), lower_limit).flatten()
    plt.hist(samples, color="g", histtype="step", label="True Data", range=(0, np.max(samples)), bins=50)
    plt.hist(censored, color="b", histtype="step", label="With Uncensored Data", range=(0, np.max(samples)), bins=50,
             linestyle="-.")
    plt.hist(new_samples, color="r", histtype="step", label="After Estimation", range=(0, np.max(samples)), bins=50,
             linestyle="--")
    plt.legend()
    plt.savefig("res.jpg")
