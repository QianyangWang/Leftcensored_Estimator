import copy
import numpy as np
from scipy.stats import gamma,norm,CensoredData
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def MLEfit(samples,rpt_limits):
    """
    MLE for a left-censored case with various reporting detection limits.
    The reason for a Gamma distribution assumption can be supported by

    :param samples: sample data-1D array
    :param rpt_limits: reporting detection limit
    :return: PDF parameters -> (shape, loc, scale)
    """

    idx = np.where(samples <= rpt_limits)
    left_censored_array = np.full(len(samples[samples <= rpt_limits]), rpt_limits[idx])
    uncensored_array = samples[samples > rpt_limits]
    censored_for_mle = CensoredData(uncensored=uncensored_array,left=left_censored_array)
    params = gamma.fit(censored_for_mle) # shape, loc, scale
    print(params)
    return params


def gen_sample(gamma_params,limit):
    while True:
        value = gamma.rvs(*gamma_params, size=1)
        if value <= limit:
            return value


def turncation(gamma_params, samples , rpt_limits):
    samples = samples.reshape(-1,1)
    for i,s in enumerate(samples):
        if s <= rpt_limits[i]:
            new_val = gen_sample(gamma_params,rpt_limits[i])
            samples[i] = new_val
    return samples


if __name__ == "__main__":
    # generate samples from normally distribution
    size = 1000
    model_shape, model_scale = 4.0, 2.0
    samples = gamma.rvs(model_shape, loc=0,scale=model_scale, size=size)

    # set censoring limits
    lower_limit = np.random.randint(3,5,1000)
    #lower_limit = np.ones(1000) * 5

    args = np.where(samples <= lower_limit)

    left_censored_array = np.full(len(samples[samples <= lower_limit]), lower_limit[args])

    uncensored_array = samples[samples > lower_limit]
    censored = np.concatenate((left_censored_array, uncensored_array))

    params = MLEfit(censored, lower_limit)
    new_samples = turncation(params, copy.copy(censored), lower_limit).flatten()
    plt.hist(samples, color="g", histtype="step", label="True Data", range=(0, np.max(samples)), bins=50)
    plt.hist(censored, color="b", histtype="step", label="With Uncensored Data", range=(0, np.max(samples)), bins=50,
             linestyle="-.")
    plt.hist(new_samples, color="r", histtype="step", label="After Estimation", range=(0, np.max(samples)), bins=50,
             linestyle="--")
    plt.legend()
    plt.savefig("resMLE.jpg")

