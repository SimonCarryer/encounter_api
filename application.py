import sys
from flask import Flask, jsonify, redirect, url_for, request, render_template
from flask_restplus import Resource, Api, reqparse
from encounters.encounter_api import EncounterSource
from utils.library import monster_manual
from collections import Counter
from werkzeug.exceptions import BadRequest
from flask_cors import CORS
from dungeons.dungeon_api import DungeonSource
import random

application = Flask(__name__)
cors = CORS(application)

api = Api(application,
          version='0.1',
          title='Encounter REST API',
          description='REST-ful API for encounters',
)


parser = api.parser()
parser.add_argument('character_levels', type=int, action='split', required=True, help='Comma-separated list of character levels.')
parser.add_argument('monster_sets', action='split', required=True, help='Comma-separated list of valid monster sets.')


@api.route('/monster-sets')
class MonsterSets(Resource):
    
    def get(self):
        '''List of accepted values for "monster sets" parameter.'''
        return sorted(list(monster_manual.get_monster_sets()))

@api.route("/encounter")
class Encounter(Resource):

    @api.doc(parser=parser)
    def get(self):
        '''Returns a random encounter meeting the supplied specifications.'''
        args = parser.parse_args()
        character_level_dict = Counter(args['character_levels'])
        monster_sets = args['monster_sets']
        if not all([monster_set in monster_manual.monster_sets for monster_set in monster_sets]):
            raise BadRequest('One or more invalid monster sets in request')
        if not all([level <= 20 for level in character_level_dict.keys()]):
            raise BadRequest('Maximum character level is 20')
        source = EncounterSource(character_level_dict=character_level_dict, monster_sets=monster_sets)
        encounter = source.get_encounter()
        return encounter

@application.route('/dungeon/<level>')
def dungeon(level):
    d = DungeonSource(int(level))
    return render_template('dungeon.html', module=d.get_dungeon())

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)