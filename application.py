import json
import urllib
import uuid
import random
import logging
from random import Random
from places.place import PlaceSource
from dungeons.dungeon_api import DungeonSource
from flask_cors import CORS
from werkzeug.exceptions import BadRequest
from collections import Counter
from flask.logging import default_handler
from utils.library import monster_manual
from encounters.encounter_api import EncounterSource
from encounters.encounter_set import EncounterSetSource
from flask_restplus import Resource, Api, reqparse
from flask import Flask, jsonify, redirect, url_for, request, render_template
import sys
from logging.config import dictConfig

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)


application = Flask(__name__)
cors = CORS(application)

api = Api(
    application,
    version="0.1",
    title="Encounter REST API",
    description="REST-ful API for encounters",
)

parser = reqparse.RequestParser()
parser.add_argument(
    "character_levels",
    type=int,
    action="split",
    required=True,
    help="Comma-separated list of character levels.",
)
parser.add_argument(
    "monster_sets",
    action="split",
    required=True,
    help="Comma-separated list of valid monster sets.",
)
parser.add_argument(
    "difficulty",
    type=str,
    required=False,
    help="Desired difficulty for encounter - medium, difficult, hard. Outcome not guaranteed.",
)

encounter_set_parser = reqparse.RequestParser()
encounter_set_parser.add_argument(
    "character_levels",
    type=int,
    action="split",
    required=True,
    help="Comma-separated list of character levels.",
)
encounter_set_parser.add_argument(
    "monster_set", required=False, help="Monster set.")

tag_parser = reqparse.RequestParser()
tag_parser.add_argument(
    "all_tags",
    action="split",
    required=False,
    help="Required tags - all must be present",
)
tag_parser.add_argument(
    "any_tags",
    action="split",
    required=False,
    help="Required tags - one must be present",
)
tag_parser.add_argument(
    "none_tags",
    action="split",
    required=False,
    help="Excluded tags - none must be present",
)

dungeon_parser = reqparse.RequestParser()
dungeon_parser.add_argument(
    "level", type=int, required=True, help="Average level of party"
)
dungeon_parser.add_argument(
    "terrain", type=str, required=False, help="Terrain type for dungeon setting."
)
dungeon_parser.add_argument(
    "dungeon_type", type=str, required=False, help="Base type of dungeon."
)
dungeon_parser.add_argument(
    "main_antagonist",
    type=str,
    required=False,
    help="Monster set of main dungeon antagonist.",
)
dungeon_parser.add_argument(
    "guid", type=str, required=False, help="GUID to intialise random state"
)

dungeon_tags_parser = reqparse.RequestParser()
dungeon_tags_parser.add_argument(
    "level", type=int, required=False, help="Average level of party"
)


@api.route("/monster-sets")
class MonsterSets(Resource):
    @api.doc(parser=tag_parser)
    def get(self):
        """Returns list "monster_set" matching supplied tags."""
        args = tag_parser.parse_args()
        return monster_manual.get_monster_sets(
            all_tags=args["all_tags"],
            any_tags=args["any_tags"],
            none_tags=args["none_tags"],
        )


@api.route("/encounter-tags")
class EncounterTags(Resource):
    def get(self):
        """List of valid tags for monster sets"""
        return monster_manual.get_tags()


@api.route("/encounter")
class Encounter(Resource):
    @api.doc(parser=parser)
    def get(self):
        """Returns a random encounter meeting the supplied specifications."""
        args = parser.parse_args()
        character_level_dict = Counter(args["character_levels"])
        monster_sets = args["monster_sets"]
        difficulty = args["difficulty"]
        if not args["difficulty"] is None and args["difficulty"] not in [
            "medium",
            "easy",
            "hard",
        ]:
            raise BadRequest("Invalid difficulty value")
        if not all(
            [monster_set in monster_manual.monster_sets for monster_set in monster_sets]
        ):
            raise BadRequest("One or more invalid monster sets in request")
        if not all([level <= 20 for level in character_level_dict.keys()]):
            raise BadRequest("Maximum character level is 20")
        source = EncounterSource(
            character_level_dict=character_level_dict, monster_sets=monster_sets
        )
        encounter = source.get_encounter(difficulty=difficulty)
        return encounter


@api.route("/dungeon")
class Dungeon(Resource):
    @api.doc(parser=dungeon_parser)
    def get(self):
        """Returns JSON representation of a random dungeon"""
        args = dungeon_parser.parse_args()
        level = args["level"]
        if args.get("guid"):
            guid = args["guid"]
        else:
            guid = str(uuid.uuid4())
        url = str(level) + "&guid=%s" % guid
        if args.get("templates"):
            templates = args["templates"].split(",")
            url += "&templates=%s" % args["templates"]
        else:
            templates = None
        if args.get("terrain"):
            terrain = urllib.parse.unquote(args["terrain"])
            url += "&terrain=%s" % args["terrain"]
        else:
            terrain = None
        if request.args.get("dungeon_type"):
            base_type = request.args["dungeon_type"]
            url += "&dungeon_type=%s" % base_type
        else:
            base_type = None
        if args.get("main_antagonist"):
            main_antagonist = urllib.parse.unquote(args["main_antagonist"])
            url += "&main_antagonist=%s" % args["main_antagonist"]
        else:
            main_antagonist = None
        base_type = args.get("dungeon_type")
        state = Random(guid)
        application.logger.debug(
            "Making a dungeon %s %s %s %s"
            % (level, base_type, main_antagonist, terrain)
        )
        d = DungeonSource(
            level,
            random_state=state,
            base_type=base_type,
            main_antagonist=main_antagonist,
            templates=templates,
            terrain=terrain,
        )
        module = d.get_dungeon()
        return jsonify({"dungeon": module, "url": url})


@api.route("/dungeon-tags")
class DungeonTags(Resource):
    @api.doc(parser=dungeon_tags_parser)
    def get(self):
        args = dungeon_tags_parser.parse_args()
        if args.get("level"):
            level = args["level"]
        else:
            level = None
        """JSON blob of valid dungeon parameters"""
        any_tags = [
            "dungeon-explorer",
            "undead",
            "beast",
            "evil",
            "cave-dweller",
            "guardian",
            "aberration",
        ]
        none_tags = ["rare"]
        valid_params = {
            "terrain": [
                "forest",
                "desert",
                "mountains",
                "arctic",
                "plains",
                "hills",
                "jungle",
                "swamp",
            ],
            "dungeontype": [
                "mine",
                "temple",
                "stronghold",
                "tomb",
                "cave",
                "treasure vault",
                "sewer",
            ],
            "antagonists": monster_manual.get_monster_sets(
                any_tags=any_tags, none_tags=none_tags
            ),
            "in_level_antagonists": monster_manual.get_monster_sets(level=level),
        }
        return jsonify(valid_params)


@api.route("/encounter_set")
class EncounterSet(Resource):
    @api.doc(parser=encounter_set_parser)
    def get(self):
        """Returns a random encounter meeting the supplied specifications."""
        args = encounter_set_parser.parse_args()
        character_level_dict = Counter(args["character_levels"])
        monster_set = args.get("monster_set")
        if monster_set is not None and monster_set not in monster_manual.monster_sets:
            raise BadRequest("One or more invalid monster sets in request")
        if monster_set is None:
            monster_set = random.choice(
                list(monster_manual.monster_sets.keys()))
        if not all([level <= 20 for level in character_level_dict.keys()]):
            raise BadRequest("Maximum character level is 20")
        source = EncounterSetSource(
            character_level_dict=character_level_dict, monster_sets=[
                monster_set]
        )
        return source.get_encounters()


if __name__ == "__main__":
    application.run(host="0.0.0.0", debug=True)
