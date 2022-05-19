# Copyright 2017 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""DialogFlow API Intent Python sample showing how to manage intents.
Examples:
  python intent_management.py -h
  python intent_management.py --project-id PROJECT_ID list
  python intent_management.py --project-id PROJECT_ID create \
  "room.cancellation - yes" \
  --training-phrases-parts "cancel" "cancellation" \
  --message-texts "Are you sure you want to cancel?" "Cancelled."
  python intent_management.py --project-id PROJECT_ID delete \
  74892d81-7901-496a-bb0a-c769eda5180e
"""

import argparse
import os
import logging.config

from dotenv import load_dotenv

from core.custom_lib.intent_management import IntentManagement

logging.config.fileConfig(
    os.path.join(os.getcwd(), "core/logging.ini"),
    disable_existing_loggers=False,
)
logger = logging.getLogger(__name__)

load_dotenv()

INTENT_NAME = os.getenv("INTENT_NAME")
PROJECT_ID = os.getenv("PROJECT_ID")
SECRET_FILE = os.getenv("SECRET_FILE")
SCOPES = [os.getenv("SCOPES")]
logger.debug(f"intent name: {INTENT_NAME}")
logger.debug(f"SCOPES: {SCOPES}")
logger.debug(f"project id: {PROJECT_ID}")
logger.debug(f"SECRET_FILE {SECRET_FILE}")


# [START dialogflow_list_intents]
def list_intents():
    from google.cloud import dialogflow

    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(PROJECT_ID)

    intents = intents_client.list_intents(request={"parent": parent})

    for intent in intents:
        print("=" * 20)
        # print("Intent name: {}".format(intent.name))
        logger.info("Intent display_name: {}".format(intent.display_name))
        # print("Action: {}\n".format(intent.action))
        # print("Root followup intent: {}".format(intent.root_followup_intent_name))
        # print("Parent followup intent: {}\n".format(intent.parent_followup_intent_name))

        # print("Input contexts:")
        # for input_context_name in intent.input_context_names:
        #     print("\tName: {}".format(input_context_name))

        # print("Output contexts:")
        # for output_context in intent.output_contexts:
        #     print("\tName: {}".format(output_context.name))


# [END dialogflow_list_intents]


# [START dialogflow_create_intent]
def create_intent(project_id, training_phrases_parts, message_texts):
    """Create an intent of the given intent type."""
    from google.cloud import dialogflow

    # intents_client = dialogflow.IntentsClient()

    # parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(
            text=training_phrases_part, entity_type="@meeting", alias="meeting"
        )
        # Here we create a new training phrase for each provided part.
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=INTENT_NAME, training_phrases=training_phrases, messages=[message]
    )

    # response = intents_client.create_intent(
    #     request={"parent": parent, "intent": intent}
    # )
    logger.info(f"Intent trained: {intent}")

    # logger.info(f"Intent created: {response}")


# [END dialogflow_create_intent]


# [START dialogflow_delete_intent]
def delete_intent(project_id, intent_id):
    """Delete intent with the given intent type and intent value."""
    from google.cloud import dialogflow

    intents_client = dialogflow.IntentsClient()

    intent_path = intents_client.intent_path(project_id, intent_id)

    intents_client.delete_intent(request={"name": intent_path})


# [END dialogflow_delete_intent]


# Helper to get intent from display name.
def _get_intent_ids(project_id, display_name):
    from google.cloud import dialogflow

    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    intents = intents_client.list_intents(request={"parent": parent})
    intent_names = [
        intent.name for intent in intents if intent.display_name == display_name
    ]

    intent_ids = [intent_name.split("/")[-1] for intent_name in intent_names]

    return intent_ids


if __name__ == "__main__":
    intent_management = IntentManagement(SECRET_FILE, SCOPES)
    messages_texts = intent_management.get_message_texts_from_sheet_file()
    training_phrases_parts = (
        intent_management.get_training_phrases_parts_from_sheet_file()
    )
    PATH_TO_CREDS = os.path.join("core/secrets.json")
    logger.debug(f"Path Client secrets json file: {PATH_TO_CREDS}")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = PATH_TO_CREDS
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    # parser.add_argument(
    #     "--list", help="list all intents.  Required.", required=True
    # )

    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help=list_intents.__doc__)

    create_parser = subparsers.add_parser("create", help=create_intent.__doc__)
    # create_parser.add_argument("display_name")
    # create_parser.add_argument(
    #     "--training-phrases-parts",
    #     nargs="*",
    #     type=str,
    #     help="Training phrases.",
    #     default=[],
    # )
    # create_parser.add_argument(
    #     "--message-texts",
    #     nargs="*",
    #     type=str,
    #     help="Message texts for the agent's response when the intent " "is detected.",
    #     default=[],
    # )

    delete_parser = subparsers.add_parser("delete", help=delete_intent.__doc__)
    delete_parser.add_argument("intent_id", help="The id of the intent.")

    args = parser.parse_args()

    if args.command == "list":
        list_intents()
    elif args.command == "create":
        create_intent(
            PROJECT_ID,
            training_phrases_parts,
            messages_texts,
        )
    elif args.command == "delete":
        delete_intent(args.project_id, args.intent_id)
