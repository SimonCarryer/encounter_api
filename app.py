import sys
from flask import Flask, jsonify, redirect, url_for, request, render_template
from encounters.encounter_api import EncounterSource

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def home():
    return "ok, it works"

@app.route("/encounter", methods=['GET', 'POST'])
def encounter():
    xp_budget = 450
    monster_set = None
    style = None
    if request.form:
        xp_budget = int(request.form['xp_budget'])
        monster_set = request.form['monster_set']
        if monster_set == 'None':
            monster_set = None
        style = request.form['style']
        if style == 'all':
            style = None
    source = EncounterSource(xp_budget=xp_budget, style=style, monster_set=monster_set)
    sets = source.monster_source.monster_sets
    styles = ['elite', 'leader', 'basic', 'all']
    encounter = source.get_encounter()
    values = {'xp_budget': xp_budget, 'style': style, 'monster_set': monster_set}
    return render_template('encounter.html',
                            encounter=encounter,
                            values=values,
                            all_sets=sets,
                            styles=styles)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)