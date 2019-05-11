import sys
from flask import Flask, jsonify, redirect, url_for, request, render_template
from flask_restplus import Resource, Api, reqparse
from encounters.encounter_api import EncounterSource
from utils.library import monster_manual
from collections import Counter
from werkzeug.exceptions import BadRequest
from flask_cors import CORS
from dungeons.dungeon_api import DungeonSource
from random import Random
import random
import uuid

application = Flask(__name__)
cors = CORS(application)

api = Api(application,
          version='0.1',
          title='Encounter REST API',
          description='REST-ful API for encounters',
)

parser = reqparse.RequestParser()
parser.add_argument('character_levels', type=int, action='split', required=True, help='Comma-separated list of character levels.')
parser.add_argument('monster_sets', action='split', required=True, help='Comma-separated list of valid monster sets.')
parser.add_argument('difficulty', type=str, required=False, help='Desired difficulty for encounter - medium, difficult, hard. Outcome not guaranteed.')

tag_parser = reqparse.RequestParser()
tag_parser.add_argument('all_tags', action='split', required=False, help='Required tags - all must be present')
tag_parser.add_argument('any_tags', action='split', required=False, help='Required tags - one must be present')
tag_parser.add_argument('none_tags', action='split', required=False, help='Excluded tags - none must be present')


@api.route('/monster-sets')
class MonsterSets(Resource):
    
    @api.doc(parser=tag_parser)
    def get(self):
        '''Returns list "monster_set" matching supplied tags.'''
        args = tag_parser.parse_args()
        return monster_manual.get_monster_sets(all_tags=args['all_tags'],
                                               any_tags=args['any_tags'],
                                               none_tags=args['none_tags'])

@api.route('/encounter-tags')
class EncounterTags(Resource):
    
    def get(self):
        '''List of valid tags for monster sets'''
        return monster_manual.get_tags()

@api.route("/encounter")
class Encounter(Resource):

    @api.doc(parser=parser)
    def get(self):
        '''Returns a random encounter meeting the supplied specifications.'''
        args = parser.parse_args()
        character_level_dict = Counter(args['character_levels'])
        monster_sets = args['monster_sets']
        difficulty = args['difficulty']
        if not args['difficulty'] is None and args['difficulty'] not in ['medium', 'easy', 'hard']:
            raise BadRequest('Invalid difficulty value')
        if not all([monster_set in monster_manual.monster_sets for monster_set in monster_sets]):
            raise BadRequest('One or more invalid monster sets in request')
        if not all([level <= 20 for level in character_level_dict.keys()]):
            raise BadRequest('Maximum character level is 20')
        source = EncounterSource(character_level_dict=character_level_dict, monster_sets=monster_sets)
        encounter = source.get_encounter(difficulty=difficulty)
        return encounter

@application.route('/dungeon/<level>')
def dungeon(level):
    if request.args.get('guid'):
        guid = request.args['guid']
    else:
        guid = str(uuid.uuid4())
    state = Random(guid)
    d = DungeonSource(int(level), random_state=state)
    return render_template('dungeon.html', module=d.get_dungeon(), guid=guid)

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)