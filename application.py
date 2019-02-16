import sys
from flask import Flask, jsonify, redirect, url_for, request, render_template
from flask_restplus import Resource, Api, reqparse
from encounters.encounter_api import EncounterSource
from encounters.monsters import load_monster_sets
from collections import Counter
from werkzeug.exceptions import BadRequest
from flask_cors import CORS

application = Flask(__name__)
cors = CORS(application)

api = Api(application,
          version='0.1',
          title='Encounter REST API',
          description='REST-ful API for encounters',
)

application.config['monster_sets'] = load_monster_sets()

parser = api.parser()
parser.add_argument('character_levels', type=int, action='split', required=True, help='Comma-separated list of character levels.')
parser.add_argument('monster_sets', action='split', required=True, help='Comma-separated list of valid monster sets.')


@api.route('/monster-sets')
class MonsterSets(Resource):
    
    def get(self):
        '''List of accepted values for "monster sets" parameter.'''
        return sorted(list(application.config['monster_sets'].keys()))

@api.route("/encounter")
class Encounter(Resource):

    @api.doc(parser=parser)
    def get(self):
        '''Returns a random encounter meeting the supplied specifications.'''
        args = parser.parse_args()
        character_level_dict = Counter(args['character_levels'])
        monster_sets = args['monster_sets']
        if not all([monster_set in application.config['monster_sets'] for monster_set in monster_sets]):
            raise BadRequest('One or more invalid monster sets in request')
        source = EncounterSource(character_level_dict=character_level_dict, monster_sets=monster_sets)
        encounter = source.get_encounter()
        return encounter

@application.route("/encounter-ui", methods=['GET', 'POST'])
def encounter_ui():
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
    source = EncounterSource(xp_budget=xp_budget, style=style, monster_sets=[monster_set])
    sets = source.monster_source.monster_set_names
    styles = ['elite', 'leader', 'basic', 'all']
    encounter = source.get_encounter()
    values = {'xp_budget': xp_budget, 'style': style, 'monster_set': monster_set}
    return render_template('encounter.html',
                            encounter=encounter,
                            values=values,
                            all_sets=sets,
                            styles=styles)


if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)