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

A basic Flask API is available but beware - it's resource heavy to run as it re-loads the input data and models each time to ensure it's up to date. A [test query script](https://github.com/nowaycomputer/us_election_2020/blob/main/app/test_query.py) is also provided. 
The following API routes are available: 

* http://127.0.0.1:500/api/singlestate will predict the election based on polls from a single state

* http://127.0.0.1:500/api/swingstates will predict the election based on the average of a selection of swing states

* http://127.0.0.1:500/api/swingstatesdatelimited will predict the election based on the average of a selection of swing states for on a given date

**Last Update 30th Oct 2020:** 

Trump: **167**

Biden: **371**

![alt text](https://github.com/nowaycomputer/us_election_2020/blob/main/img/301020.png)



```
Modelling Election based on latest polls from Florida

Model Outputs: Dem: 51.57  and Rep: 48.4
Current Poll: Dem: 51.6  and Rep: 48.4

Trump Electoral College Votes: 183
Biden Electoral College Votes: 355

-------------------------

Modelling Election based on latest polls from Wisconsin

Model Outputs: Dem: 54.05  and Rep: 45.95
Current Poll: Dem: 53.85  and Rep: 46.15

Trump Electoral College Votes: 150
Biden Electoral College Votes: 388

-------------------------

Modelling Election based on latest polls from Pennsylvania

Model Outputs: Dem: 51.83  and Rep: 48.26
Current Poll: Dem: 51.62  and Rep: 48.38

Trump Electoral College Votes: 153
Biden Electoral College Votes: 385

-------------------------

Modelling Election based on latest polls from North Carolina

Model Outputs: Dem: 49.42  and Rep: 51.29
Current Poll: Dem: 49.63  and Rep: 50.37

Trump Electoral College Votes: 288
Biden Electoral College Votes: 250

-------------------------

Modelling Election based on latest polls from Michigan

Model Outputs: Dem: 57.15  and Rep: 43.72
Current Poll: Dem: 56.96  and Rep: 43.04

Trump Electoral College Votes: 87
Biden Electoral College Votes: 451

-------------------------


 Implied Mean Republican Electoral College Votes: 172.0

 Implied Mean Democrat Electoral College Votes: 366.0
```

Recognised Issues:
* *The selection of swing states is a bit arbitrary but was selected as the five closest to the centre of the fivethirtyeight tipping point 'snake' when the model was built*
* *Demographics have changed since the dataset I'm using was created*
* *Differential turnout (or even a general increase in turnout) is not handled at all*
* *The 'backtesting below runs to January 2020 when Biden wasn't confirmed as the candidate but he was generally seen as the favourite for most of 2020 even before the primaries had concluded*

