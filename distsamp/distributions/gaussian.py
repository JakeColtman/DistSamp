

def convert_to_natural_parameters(mean, variance):
    l = 1.0 / variance
    e = l * mean
    return e, l


def convert_to_expectation_parameters(eta, llambda):
    variance = 1.0 / llambda
    mean = eta / llambda
    return mean, variance


def cavity_distribution(full_distribution, site_distribution):
    full_eta, full_lambda = convert_to_natural_parameters(**full_distribution)
    site_eta, site_ll = convert_to_natural_parameters(**site_distribution)

    mu, var = convert_to_expectation_parameters(full_eta - site_eta, full_lambda - site_ll)
    return {"mean": mu, "variance": var}
