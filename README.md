# us_election_2020
A toy model for predicting the 2020 US presidential election outcome

Ideas:

* Can we train a model on the 2016 election results using only demographic data and the previous election results?

* Can we update that model somehow using new polling data such that we can create new polling estimates for other (un-polled) states?

* Can we use these synthetic polls to estimate the results of the 2020 election?

The answers to these are: 'yes', 'kind of' and 'probably not accurately'. That said, a first attempt is contained in the notebooks folder.

The process runs as follows:

* Fit a model to the 2016 results using some demographic features and the 2012 result in that state
* For a set of swing states (*Florida, Wisconsin, Pennsylvania, North Carolina, Michigan, Arizona, Georgia*):
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

**Final Update 3rd Nov 2020:** 

Trump: **177**

Biden: **361**

![alt text](https://github.com/nowaycomputer/us_election_2020/blob/main/img/031120.png)


Recognised Issues:
* *The selection of swing states is a bit arbitrary but was selected as the five closest to the centre of the fivethirtyeight tipping point 'snake' when the model was built*
* *Demographics have changed since the dataset I'm using was created*
* *Differential turnout (or even a general increase in turnout) is not handled at all*
* *The 'backtesting below runs to May 2020 when Biden wasn't confirmed as the candidate but he was generally seen as the favourite for most of 2020 even before the primaries had concluded*

