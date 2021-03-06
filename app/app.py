from flask import Flask, request, redirect, url_for, flash, jsonify
import numpy as np
import json
import us2020.us2020 as us2020
import tensorflow as tf
import joblib

app = Flask(__name__)

scaler_filename = "models/scaler.save"
scaler = joblib.load(scaler_filename)

# Predict the election based on recent polls from a single state
@app.route('/api/singlestate/', methods=['POST'])
def get_prediction_based_on_single_states():
    s = request.get_json()

    model_tools = us2020.ModelTools()

    wa_poll = model_tools.get_538_poll_ave(s)

    X_new = []
    Y_new = []

    x, y = model_tools.make_new_feature_poll_based(s)
    X_new.append(x)
    Y_new.append(y)

    X_new = np.array(X_new)
    Y_new = np.array(Y_new)

    X_new = scaler.transform(X_new)

    # Make a new model that re-tunes the baseline model
    new_model = tf.keras.models.load_model('models/271020_baseline.h5')

    error = np.abs(
        new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(s).reshape(1, -1)))[0][0] - wa_poll[
            0] * 100)

    # Let's do a maximum of 100 re-trains of the model on the single example
    for i in range(0, 100):
        new_model.fit(
            X_new, Y_new,
            epochs=1,
            verbose=0
        )
        error = np.abs(
            new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(s).reshape(1, -1)))[0][0] - wa_poll[
                0] * 100)
        #     We've got the model close enough
        if error < 0.25:
            break

    model_results = new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(s).reshape(1, -1)))

    # Let's predict the 2020 election based on this re-tuned model

    rep_state_wins = []
    dem_state_wins = []
    rep_elec_coll_votes = 0
    dem_elec_coll_votes = 0

    # Hacky Alaska workaround!
    rep_state_wins.append('AK')
    rep_elec_coll_votes += model_tools.elec_college[model_tools.elec_college['State'] == 'AK']['Votes'].values[0]

    for state in model_tools.states:
        if state != 'United States':
            if state != 'District Of Columbia':
                results = new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(state).reshape(1, -1)))
                if results[0][1] > results[0][0]:
                    rep_state_wins.append(state)
                    rep_elec_coll_votes += \
                    model_tools.elec_college[model_tools.elec_college['State'] == model_tools.get_short_name_from_long(state)]['Votes'].values[0]
                elif results[0][1] < results[0][0]:
                    dem_state_wins.append(state)
                    dem_elec_coll_votes += \
                    model_tools.elec_college[model_tools.elec_college['State'] == model_tools.get_short_name_from_long(state)]['Votes'].values[0]

    results = {'Based_on_state': s,
               'Trump': str(rep_elec_coll_votes),
               'Biden': str(dem_elec_coll_votes),
               'Trump_won_states': str(rep_state_wins),
               'Biden_won_state': str(dem_state_wins)
               }
    return jsonify(results)

# Predict the election based on the average output from a set of swing states
@app.route('/api/swingstates/', methods=['POST'])
def get_prediction_based_on_swing_states():

    model_tools = us2020.ModelTools()

    model_run_rep_ev = []
    model_run_dem_ev = []

    test_states = ['Florida', 'Wisconsin', 'Pennsylvania', 'North Carolina', 'Michigan']
    for s in test_states:

        wa_poll = model_tools.get_538_poll_ave(s)

        X_new = []
        Y_new = []

        x, y = model_tools.make_new_feature_poll_based(s)
        X_new.append(x)
        Y_new.append(y)

        X_new = np.array(X_new)
        Y_new = np.array(Y_new)

        X_new = scaler.transform(X_new)

        # Make a new model that re-tunes the baseline model
        new_model = tf.keras.models.load_model('models/271020_baseline.h5')

        error = np.abs(
            new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(s).reshape(1, -1)))[0][0] - wa_poll[
                0] * 100)

        # Let's do a maximum of 100 re-trains of the model on the single example
        for i in range(0, 100):
            new_model.fit(
                X_new, Y_new,
                epochs=1,
                verbose=0
            )
            error = np.abs(
                new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(s).reshape(1, -1)))[0][0] - wa_poll[
                    0] * 100)
            #     We've got the model close enough
            if error < 0.25:
                break

        model_results = new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(s).reshape(1, -1)))

        # Let's predict the 2020 election based on this re-tuned model

        rep_elec_coll_votes = 0
        dem_elec_coll_votes = 0

        # Hacky Alaska workaround!
        rep_elec_coll_votes += model_tools.elec_college[model_tools.elec_college['State'] == 'AK']['Votes'].values[0]

        for state in model_tools.states:
            if state != 'United States':
                if state != 'District Of Columbia':
                    results = new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(state).reshape(1, -1)))
                    if results[0][1] > results[0][0]:
                        rep_elec_coll_votes += \
                        model_tools.elec_college[model_tools.elec_college['State'] == model_tools.get_short_name_from_long(state)]['Votes'].values[0]
                    elif results[0][1] < results[0][0]:
                        dem_elec_coll_votes += \
                        model_tools.elec_college[model_tools.elec_college['State'] == model_tools.get_short_name_from_long(state)]['Votes'].values[0]

        model_run_rep_ev.append(rep_elec_coll_votes)
        model_run_dem_ev.append(dem_elec_coll_votes)

    r_ev = str(np.round(np.mean(model_run_rep_ev), 0))
    d_ev = str(np.round(np.mean(model_run_dem_ev), 0))

    results = {'Trump': r_ev, 'Biden': d_ev}
    return jsonify(results)
@app.route('/api/five_thirty_eight_tipping_points/', methods=['POST'])
def five_thirty_eight_tipping_points():

    model_tools = us2020.ModelTools()

    model_run_rep_ev = []
    model_run_dem_ev = []

    test_states = ['Florida', 'Wisconsin', 'Pennsylvania', 'North Carolina', 'Michigan','Arizona', 'Minnesota',
                   'Georgia','Michigan','Nevada','Ohio', 'New Mexico', 'Colorado', 'New Hampshire', 'Virginia']
    for s in test_states:

        wa_poll = model_tools.get_538_poll_ave(s)

        X_new = []
        Y_new = []

        x, y = model_tools.make_new_feature_poll_based(s)
        X_new.append(x)
        Y_new.append(y)

        X_new = np.array(X_new)
        Y_new = np.array(Y_new)

        X_new = scaler.transform(X_new)

        # Make a new model that re-tunes the baseline model
        new_model = tf.keras.models.load_model('models/271020_baseline.h5')

        error = np.abs(
            new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(s).reshape(1, -1)))[0][0] - wa_poll[
                0] * 100)

        # Let's do a maximum of 100 re-trains of the model on the single example
        for i in range(0, 100):
            new_model.fit(
                X_new, Y_new,
                epochs=1,
                verbose=0
            )
            error = np.abs(
                new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(s).reshape(1, -1)))[0][0] - wa_poll[
                    0] * 100)
            #     We've got the model close enough
            if error < 0.25:
                break

        model_results = new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(s).reshape(1, -1)))

        # Let's predict the 2020 election based on this re-tuned model

        rep_elec_coll_votes = 0
        dem_elec_coll_votes = 0

        # Hacky Alaska workaround!
        rep_elec_coll_votes += model_tools.elec_college[model_tools.elec_college['State'] == 'AK']['Votes'].values[0]

        for state in model_tools.states:
            if state != 'United States':
                if state != 'District Of Columbia':
                    results = new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(state).reshape(1, -1)))
                    if results[0][1] > results[0][0]:
                        rep_elec_coll_votes += \
                        model_tools.elec_college[model_tools.elec_college['State'] == model_tools.get_short_name_from_long(state)]['Votes'].values[0]
                    elif results[0][1] < results[0][0]:
                        dem_elec_coll_votes += \
                        model_tools.elec_college[model_tools.elec_college['State'] == model_tools.get_short_name_from_long(state)]['Votes'].values[0]

        model_run_rep_ev.append(rep_elec_coll_votes)
        model_run_dem_ev.append(dem_elec_coll_votes)

    r_ev = str(np.round(np.mean(model_run_rep_ev), 0))
    d_ev = str(np.round(np.mean(model_run_dem_ev), 0))

    results = {'Trump': r_ev, 'Biden': d_ev}
    return jsonify(results)

# Predict the election based on the average output from a set of swing states
@app.route('/api/swingstatesdatelimited/', methods=['POST'])
def get_prediction_based_on_swing_states_date_limited():
    data = request.get_json()
    date = data['date']

    model_tools = us2020.ModelTools()
    trump_upper_bound=[]
    trump_lower_bound=[]
    biden_upper_bound=[]
    biden_lower_bound=[]

    model_run_rep_ev = []
    model_run_dem_ev = []

    test_states=['Florida', 'Wisconsin', 'Pennsylvania', 'North Carolina', 'Michigan', 'Arizona', 'Georgia']

    trump_max = 0
    trump_min = 999
    biden_max = 0
    biden_min = 999

    for s in test_states:

        wa_poll = model_tools.get_538_poll_ave_date_limited(s, date)

        X_new = []
        Y_new = []

        x, y = model_tools.make_new_feature_poll_based_time_limited(s, date)
        X_new.append(x)
        Y_new.append(y)

        X_new = np.array(X_new)
        Y_new = np.array(Y_new)

        X_new = scaler.transform(X_new)

        # Make a new model that re-tunes the baseline model
        new_model = tf.keras.models.load_model('models/271020_baseline.h5')

        error = np.abs(
            new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(s).reshape(1, -1)))[0][0] - wa_poll[
                0] * 100)

        # Let's do a maximum of 100 re-trains of the model on the single example
        for i in range(0, 100):
            new_model.fit(
                X_new, Y_new,
                epochs=1,
                verbose=0
            )
            error = np.abs(
                new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(s).reshape(1, -1)))[0][0] - wa_poll[
                    0] * 100)
            #     We've got the model close enough
            if error < 0.25:
                break

        model_results = new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(s).reshape(1, -1)))

        # Let's predict the 2020 election based on this re-tuned model

        rep_elec_coll_votes = 0
        dem_elec_coll_votes = 0

        # Hacky Alaska workaround!
        rep_elec_coll_votes += model_tools.elec_college[model_tools.elec_college['State'] == 'AK']['Votes'].values[0]

        for state in model_tools.states:
            if state != 'United States':
                if state != 'District Of Columbia':
                    #  Calculate the model results
                    results = new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(state).reshape(1, -1)))
                    if results[0][1] > results[0][0]:
                        rep_elec_coll_votes += \
                        model_tools.elec_college[model_tools.elec_college['State'] == model_tools.get_short_name_from_long(state)]['Votes'].values[0]
                    elif results[0][1] < results[0][0]:
                        dem_elec_coll_votes += \
                        model_tools.elec_college[model_tools.elec_college['State'] == model_tools.get_short_name_from_long(state)]['Votes'].values[0]

        # Update bounds
        if dem_elec_coll_votes > biden_max:
            biden_max = dem_elec_coll_votes
        if dem_elec_coll_votes < biden_min:
            biden_min = dem_elec_coll_votes

        if rep_elec_coll_votes > trump_max:
            trump_max = rep_elec_coll_votes
        if rep_elec_coll_votes < trump_min:
            trump_min = rep_elec_coll_votes

        model_run_rep_ev.append(rep_elec_coll_votes)
        model_run_dem_ev.append(dem_elec_coll_votes)

    r_ev = str(np.round(np.mean(model_run_rep_ev), 0))
    d_ev = str(np.round(np.mean(model_run_dem_ev), 0))

    results = {'Trump': r_ev, 'Biden': d_ev,
               'Trump_min': str(trump_min), 'Trump_max': str(trump_max),
               'Biden_min': str(biden_min), 'Biden_max': str(biden_max)}
    return jsonify(results)


if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0')
