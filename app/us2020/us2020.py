import pandas as pd
import numpy as np
# To fix - some messy slicing of pandas frames
pd.set_option('mode.chained_assignment', None)

class ModelTools:
    def __init__(self):

        # State demographics as of 2016
        self.state_demo = pd.read_csv(
            'https://corgis-edu.github.io/corgis/datasets/csv/state_demographics/state_demographics.csv')

        # We only want (or need, for now) a subset of the demographic features - these are pretty self explanitory
        features_to_use = ['State',
                           'Education.Bachelor\'s Degree or Higher',
                           'Education.High School or Higher',
                           'Miscellaneous.Percent Female',
                           ]

        # Filter by the features we want
        self.state_demo_use = self.state_demo[features_to_use]

        self.states = self.state_demo['State'].unique()

        # Electoral college votes by state
        self.elec_college = pd.read_csv('../data/electoral-college-votes.csv', names=['State_full', 'State', 'Votes'])

        # 2016 Election results by state
        self.results_2016_state = pd.read_csv('../data/2016state.csv')

        # 2012 Election results by state
        self.results_2012_state = pd.read_excel('../data/US Presidential Election 2012 By State.xlsx',
                                           names=['State', 'Democratic Party', 'Republican Party', 'Libertarian Party',
                                                  'Green Party', 'Others', 'Total Votes'])
        # Skip the first row of the 2012 results (metadata)
        self.results_2012_state = self.results_2012_state.iloc[1:]

        # Calculate the % of dem and rep votes in 2012
        self.results_2012_state['dem_pc'] = (self.results_2012_state['Democratic Party'] / self.results_2012_state[
            'Total Votes']) * 100
        self.results_2012_state['rep_pc'] = (self.results_2012_state['Republican Party'] / self.results_2012_state[
            'Total Votes']) * 100

        # 538's excellent polling database
        self.polls_pres = pd.read_csv('https://projects.fivethirtyeight.com/2020-general-data/presidential_polls_2020.csv')

    # Get the full state name (e.g. 'Florida') from the short state name (e.g. 'FL')
    def get_long_name_from_short(self, short_name):
        long_name = self.elec_college[self.elec_college['State'] == short_name]['State_full'].values[0]
        return long_name

    # And the same for long to short
    def get_short_name_from_long(self, long_name):
        short_name = self.elec_college[self.elec_college['State_full'] == long_name]['State'].values[0]
        return short_name

    # Get the polls for a given state
    def get_polls_for_state(self, state):
        dates = []
        weights = []
        biden = []
        trump = []

        unique_polls = self.polls_pres[self.polls_pres['state'] == state]['poll_id'].unique()

        for p in unique_polls:
            sub = self.polls_pres[self.polls_pres['poll_id'] == p]

            dates.append(sub['startdate'].iloc[0])
            weights.append(sub['weight'].iloc[0])
            biden.append(sub[sub['candidate_name'] == 'Joseph R. Biden Jr.']['pct'].iloc[0])
            trump.append(sub[sub['candidate_name'] == 'Donald Trump']['pct'].iloc[0])

        subdata = pd.DataFrame({'Date': dates,
                                'Weights': weights,
                                'Trump': trump,
                                'Biden': biden,
                                })
        subdata['Date'] = pd.to_datetime(subdata['Date'])
        subdata.index = subdata['Date']
        subdata = subdata.drop('Date', axis=1).sort_index()
        return subdata

    # Get the weighted (by 538) polls for a given state
    # Ideally we get the last 3 polls but in some cases there are only 2, 1 or none
    def get_weighted_norm_poll_vote_share(self, state):
        vote_shares = self.get_polls_for_state(self.get_long_name_from_short(state))
        vote_shares['Biden_norm'] = vote_shares['Biden'] / (vote_shares['Biden'] + vote_shares['Trump'])
        vote_shares['Trump_norm'] = vote_shares['Trump'] / (vote_shares['Biden'] + vote_shares['Trump'])

        biden = 0
        trump = 0

        #  Really scrappy handling of available polls - to clean
        if len(vote_shares) > 2:
            last_polls = vote_shares.tail(3)
            last_polls_total_weight = last_polls['Weights'].sum()
            last_polls['poll_frac'] = last_polls['Weights'] / last_polls_total_weight

            biden = last_polls.iloc[0]['poll_frac'] * last_polls.iloc[0]['Biden_norm'] + last_polls.iloc[1][
                'poll_frac'] * last_polls.iloc[1]['Biden_norm'] + last_polls.iloc[2]['poll_frac'] * last_polls.iloc[2][
                        'Biden_norm']
            trump = last_polls.iloc[0]['poll_frac'] * last_polls.iloc[0]['Trump_norm'] + last_polls.iloc[1][
                'poll_frac'] * last_polls.iloc[1]['Trump_norm'] + last_polls.iloc[2]['poll_frac'] * last_polls.iloc[2][
                        'Trump_norm']

        elif len(vote_shares) > 1:
            last_polls = vote_shares.tail(2)
            last_polls_total_weight = last_polls['Weights'].sum()
            last_polls['poll_frac'] = last_polls['Weights'] / last_polls_total_weight

            biden = last_polls.iloc[0]['poll_frac'] * last_polls.iloc[0]['Biden_norm'] + last_polls.iloc[1][
                'poll_frac'] * last_polls.iloc[1]['Biden_norm']
            trump = last_polls.iloc[0]['poll_frac'] * last_polls.iloc[0]['Trump_norm'] + last_polls.iloc[1][
                'poll_frac'] * last_polls.iloc[1]['Trump_norm']

        else:
            last_polls = vote_shares.tail(1)
            biden = last_polls.iloc[0]['Biden_norm']
            trump = last_polls.iloc[0]['Trump_norm']

        return biden, trump

    def get_weighted_norm_poll_vote_share_date_limited(self, state, end_date):
        vote_shares = self.get_polls_for_state(self.get_long_name_from_short(state))
        vote_shares['Biden_norm'] = vote_shares['Biden'] / (vote_shares['Biden'] + vote_shares['Trump'])
        vote_shares['Trump_norm'] = vote_shares['Trump'] / (vote_shares['Biden'] + vote_shares['Trump'])

        vote_shares = vote_shares[vote_shares.index < end_date]
        biden = 0
        trump = 0

        #  Really scrappy handling of available polls - to clean
        if len(vote_shares) > 2:
            last_polls = vote_shares.tail(3)
            last_polls_total_weight = last_polls['Weights'].sum()
            last_polls['poll_frac'] = last_polls['Weights'] / last_polls_total_weight

            biden = last_polls.iloc[0]['poll_frac'] * last_polls.iloc[0]['Biden_norm'] + last_polls.iloc[1][
                'poll_frac'] * last_polls.iloc[1]['Biden_norm'] + last_polls.iloc[2]['poll_frac'] * last_polls.iloc[2][
                        'Biden_norm']
            trump = last_polls.iloc[0]['poll_frac'] * last_polls.iloc[0]['Trump_norm'] + last_polls.iloc[1][
                'poll_frac'] * last_polls.iloc[1]['Trump_norm'] + last_polls.iloc[2]['poll_frac'] * last_polls.iloc[2][
                        'Trump_norm']

        elif len(vote_shares) > 1:
            last_polls = vote_shares.tail(2)
            last_polls_total_weight = last_polls['Weights'].sum()
            last_polls['poll_frac'] = last_polls['Weights'] / last_polls_total_weight

            biden = last_polls.iloc[0]['poll_frac'] * last_polls.iloc[0]['Biden_norm'] + last_polls.iloc[1][
                'poll_frac'] * last_polls.iloc[1]['Biden_norm']
            trump = last_polls.iloc[0]['poll_frac'] * last_polls.iloc[0]['Trump_norm'] + last_polls.iloc[1][
                'poll_frac'] * last_polls.iloc[1]['Trump_norm']

        else:
            last_polls = vote_shares.tail(1)
            biden = last_polls.iloc[0]['Biden_norm']
            trump = last_polls.iloc[0]['Trump_norm']

        return biden, trump

    # Get the dem and rep % vote share for 2012
    def get_2012_vote_shares(self, state):
        state = self.get_short_name_from_long(state)
        dem = self.results_2012_state[self.results_2012_state['State'] == state]['dem_pc'].values[0]
        rep = self.results_2012_state[self.results_2012_state['State'] == state]['rep_pc'].values[0]
        return dem, rep

    # Get the dem and rep % vote share for 2016
    def get_2016_vote_shares(self, state):
        dem = self.results_2016_state[self.results_2016_state['State'] == state]['percD'].values[0]
        rep = self.results_2016_state[self.results_2016_state['State'] == state]['percR'].values[0]
        return dem, rep

    # This function is useful later when we want to build features for a given state (rather than all)
    def get_features_state(self, s):
        demo_inputs = self.state_demo_use[self.state_demo_use['State'] == s].drop('State', axis=1).values[0].tolist()
        dem_2012, rep_2012 = self.get_2012_vote_shares(s)
        demo_inputs.append(dem_2012)
        demo_inputs.append(rep_2012)

        return np.array(demo_inputs)

    # Get features and POLL outputs for re-tuning the model

    def make_new_feature_poll_based(self, s):
        demo_inputs = self.state_demo_use[self.state_demo_use['State'] == s].drop('State', axis=1).values[0].tolist()
        dem_2016, rep_2016 = self.get_2016_vote_shares(s)
        demo_inputs.append(dem_2016)
        demo_inputs.append(rep_2016)

        Y = []
        polls = self.get_weighted_norm_poll_vote_share(self.get_short_name_from_long(s))
        dem_poll = 100 * polls[0]
        rep_poll = 100 * polls[1]

        Y.append(dem_poll)
        Y.append(rep_poll)

        return np.array(demo_inputs), np.array(Y)

    def make_new_feature_poll_based_time_limited(self, state, end_date):
        demo_inputs = self.state_demo_use[self.state_demo_use['State'] == state].drop('State', axis=1).values[0].tolist()
        dem_2016, rep_2016 = self.get_2016_vote_shares(state)
        demo_inputs.append(dem_2016)
        demo_inputs.append(rep_2016)

        Y = []
        polls = self.get_weighted_norm_poll_vote_share_date_limited(self.get_short_name_from_long(state), end_date)
        dem_poll = 100 * polls[0]
        rep_poll = 100 * polls[1]

        Y.append(dem_poll)
        Y.append(rep_poll)

        return np.array(demo_inputs), np.array(Y)

    # Get features for 2020 predictions
    def make_new_feature_2016_based(self, state):
        demo_inputs = self.state_demo_use[self.state_demo_use['State'] == state].drop('State', axis=1).values[0].tolist()
        dem_2016, rep_2016 = self.get_2016_vote_shares(state)
        demo_inputs.append(dem_2016)
        demo_inputs.append(rep_2016)

        return np.array(demo_inputs)