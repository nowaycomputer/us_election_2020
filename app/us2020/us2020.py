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

        # 538's excellent polling databases
        self.polls_pres = pd.read_csv('https://projects.fivethirtyeight.com/2020-general-data/presidential_polls_2020.csv')

        self.polls_pres_ave = pd.read_csv(
            'https://projects.fivethirtyeight.com/2020-general-data/presidential_poll_averages_2020.csv')
        self.polls_pres_ave['modeldate'] = pd.to_datetime(self.polls_pres_ave['modeldate'])

        self.polls_pres_ave = self.polls_pres_ave.set_index('modeldate').sort_index()

    def get_538_poll_ave(self, state):

        trump = self.polls_pres_ave[(self.polls_pres_ave['candidate_name'] == 'Donald Trump') &
                               (self.polls_pres_ave['state'] == state)].tail(1)['pct_estimate'].values[0]

        biden = self.polls_pres_ave[(self.polls_pres_ave['candidate_name'] == 'Joseph R. Biden Jr.') &
                               (self.polls_pres_ave['state'] == state)].tail(1)['pct_estimate'].values[0]
        return biden * 0.01, trump * 0.01

    def get_538_poll_ave_date_limited(self, state, date):
        date = pd.to_datetime(date, format="%d/%m/%Y")
        # print(date)
        # print(state)
        # print(self.polls_pres_ave[(self.polls_pres_ave['candidate_name'] == 'Donald Trump') &
        #                     (self.polls_pres_ave['state'] == state) &
        #                     (self.polls_pres_ave.index < date)].tail(1))

        trump = self.polls_pres_ave[(self.polls_pres_ave['candidate_name'] == 'Donald Trump') &
                               (self.polls_pres_ave['state'] == state) &
                               (self.polls_pres_ave.index <= date)].tail(1)['pct_estimate'].values[0]

        biden = self.polls_pres_ave[(self.polls_pres_ave['candidate_name'] == 'Joseph R. Biden Jr.') &
                               (self.polls_pres_ave['state'] == state) &
                               (self.polls_pres_ave.index <= date)].tail(1)['pct_estimate'].values[0]
        return biden * 0.01, trump * 0.01

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
        polls = self.get_538_poll_ave(s)
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
        polls = self.get_538_poll_ave_date_limited(state, end_date)
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