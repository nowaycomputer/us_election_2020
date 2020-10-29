from flask import Flask, request, redirect, url_for, flash, jsonify
import numpy as np
import json
import us2020.us2020 as us2020
import tensorflow as tf
import joblib

app = Flask(__name__)


@app.route('/api/', methods=['POST'])
def get_prediction_based_on_swing_states():
    scaler_filename = "models/scaler.save"
    scaler = joblib.load(scaler_filename)
    model_tools = us2020.ModelTools()

    model_run_rep_ev = []
    model_run_dem_ev = []

    # test_states=['Florida']
    test_states = ['Florida', 'Wisconsin', 'Pennsylvania', 'North Carolina', 'Michigan']
    for s in test_states:

        wa_poll = model_tools.get_weighted_norm_poll_vote_share(model_tools.get_short_name_from_long(s))

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

        for s in model_tools.states:
            if s != 'United States':
                if s != 'District Of Columbia':
                    results = new_model.predict(scaler.transform(model_tools.make_new_feature_2016_based(s).reshape(1, -1)))
                    if results[0][1] > results[0][0]:
                        rep_state_wins.append(s)
                        rep_elec_coll_votes += \
                        model_tools.elec_college[model_tools.elec_college['State'] == model_tools.get_short_name_from_long(s)]['Votes'].values[0]
                    elif results[0][1] < results[0][0]:
                        dem_state_wins.append(s)
                        dem_elec_coll_votes += \
                        model_tools.elec_college[model_tools.elec_college['State'] == model_tools.get_short_name_from_long(s)]['Votes'].values[0]

        model_run_rep_ev.append(rep_elec_coll_votes)
        model_run_dem_ev.append(dem_elec_coll_votes)

    r_ev = str(np.round(np.mean(model_run_rep_ev), 0))
    d_ev = str(np.round(np.mean(model_run_dem_ev), 0))

    results = {}
    results['Trump'] = r_ev
    results['Biden'] = d_ev

    return jsonify(results)


if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0')
