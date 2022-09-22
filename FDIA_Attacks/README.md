# Setup Instructions

## Install MATPOWER7.0

Download (MATPOWER 7.0)[https://matpower.org/] and add the downloaded
folder to this directory

# Running experiments

## Baseline J value experiment

In MATLAB run `BaselineJ_experiment.m`. In the file you can set N, the\
number of trials. N=1000 will take awhile so I recommend starting with N=5 :p

## Single FDIA experiment

In MATLAB run the `FDIA_modelling_main.m`. This will run an FDIA attack for
varying access to measurement devices. This is a single experiment and
there is a lot variance in results.

## Run a batch FDIA experiment

To run many FDIA experiments, like Finding 5 in the paper, run
`FDIA_batch_experiment.m`.

N in `FDIA_batch_experiment.m` is the number of trials to run. Each trial
takes a fair amount of time, so it will likely take a few days to replicate
the N=1000 (the trials used the paper).