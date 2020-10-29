# us_election_2020
A toy model for predicting the 2020 US presidential election outcome

Ideas:

* Can we train a model on the 2016 election results using only demographic data and the previous election results?

* Can we update that model somehow using new polling data such that we can create new polling estimates for other (un-polled) states?

* Can we use these synthetic polls to estimate the results of the 2020 election?

The answers to these are: 'yes', 'kind of' and 'probably not'. That said, a first attempt is contained in the notebooks folder.

The process runs as follows:

* Fit a model to the 2016 results using some demographic features and the 2012 result in that state
* For a set of swing states (*Florida, Wisconsin, Pennsylvania, North Carolina, Michigan*):
  * The average of the last three [fivethirtyeight](https://projects.fivethirtyeight.com/2020-election-forecast/) polls (adjusted for weightings) for that state is calculated
  * Using the demographic data for that state and the poll average, re-train the model against this single instance of data until the error is <0.25% (totally arbitrary but in the recount region for most states!)
  * Using the re-trained model, make predictions for 2020 based on demographic data and 2016 vote in each state
  * Calculate the winner of each state and the number of electoral votes
* The average outcome of these model re-training runs is calculated to generate the final output

A basic Flask API is available but beware - it's resource heavy to run as it re-loads the input data and models each time to ensure it's up to date. A test query script is also provided. Hitting http://127.0.0.1:500/api should return the results in json.

**Last Update 29th Oct 2020:** 

Trump: **154**

Biden: **384**

![alt text](https://github.com/nowaycomputer/us_election_2020/blob/main/img/291020.png)



```
Modelling Election based on latest polls from Florida

Model Outputs: Dem: 52.02  and Rep: 47.92
Current Poll: Dem: 51.92  and Rep: 48.08

Trump Electoral College Votes: 179
Biden Electoral College Votes: 359

-------------------------

Modelling Election based on latest polls from Wisconsin

Model Outputs: Dem: 55.93  and Rep: 43.89
Current Poll: Dem: 55.88  and Rep: 44.12

Trump Electoral College Votes: 114
Biden Electoral College Votes: 424

-------------------------

Modelling Election based on latest polls from Pennsylvania

Model Outputs: Dem: 52.64  and Rep: 47.47
Current Poll: Dem: 52.47  and Rep: 47.53

Trump Electoral College Votes: 153
Biden Electoral College Votes: 385

-------------------------

Modelling Election based on latest polls from North Carolina

Model Outputs: Dem: 51.31  and Rep: 48.34
Current Poll: Dem: 51.41  and Rep: 48.59

Trump Electoral College Votes: 203
Biden Electoral College Votes: 335

-------------------------

Modelling Election based on latest polls from Michigan

Model Outputs: Dem: 55.1  and Rep: 45.09
Current Poll: Dem: 55.23  and Rep: 44.77

Trump Electoral College Votes: 120
Biden Electoral College Votes: 418

-------------------------


 Implied Mean Republican Electoral College Votes: 154.0

 Implied Mean Democrat Electoral College Votes: 384.0
```

Recognised Issues:
* *The selection of swing states is a bit arbitrary but was selected as the five closest to the centre of the fivethirtyeight tipping point 'snake' when the model was built*
* *Demographics have changed since the dataset I'm using was created*
* *Differential turnout (or even a general increase in turnout) is not handled at all*
* *The 'backtesting below runs to January 2020 when Biden wasn't confirmed as the candidate but he was generally seen as the favourite for most of 2020 even before the primaries had concluded*

