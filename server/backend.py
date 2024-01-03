from json import dumps
from time import time
from flask import request
from hashlib import sha256
from datetime import datetime
from requests import get
from requests import post 
from json     import loads
import os

from server.config import special_instructions


class Backend_Api:
    def __init__(self, app, config: dict) -> None:
        self.app = app
        self.openai_key = os.getenv("OPENAI_API_KEY") or config['openai_key']
        self.openai_api_base = os.getenv("OPENAI_API_BASE") or config['openai_api_base']
        self.proxy = config['proxy']
        self.routes = {
            '/backend-api/v2/conversation': {
                'function': self._conversation,
                'methods': ['POST']
            }
        }

    def _conversation(self):
        try:
            jailbreak = request.json['jailbreak']
            internet_access = request.json['meta']['content']['internet_access']
            _conversation = request.json['meta']['content']['conversation']
            prompt = request.json['meta']['content']['parts'][0]
            current_date = datetime.now().strftime("%Y-%m-%d")

             system_message = (
                  "Bonjour, je suis WebiChat, votre assistant IA spécialisé dans les enseignements de la chrétienté. "
                 "Ma base de connaissances englobe la Bible et une vaste sélection de textes, tout en reconnaissant que cette liste n'est pas exhaustive. "
                 "Je me réfère notamment aux textes suivants : Ancien Testament (Apocryphes juifs) comme Tobit, Judith, Ajouts à Esther, "
                 "Sagesse de Salomon, Sagesse de Jésus Sirach (Ecclésiastique), Baruch, y compris la Lettre de Jérémie, Ajouts à Daniel (Le Chant des trois jeunes hommes, Suzanne, Bel et le Dragon), "
                 "1 Maccabées, 2 Maccabées, 3 Maccabées, 4 Maccabées (dans certains canons), Prière de Manassé, Psaume 151; Nouveau Testament (Apocryphes chrétiens) "
                 "tels que les Évangiles apocryphes (par exemple, l'Évangile de Thomas, l'Évangile de Pierre), Actes apocryphes (par exemple, les Actes de Paul, les Actes de Jean), "
                 "Épîtres apocryphes (par exemple, la Correspondance de Paul et Sénèque), Apocalypses apocryphes (par exemple, l'Apocalypse de Pierre); "
                 "ainsi que les Pseudépigraphes de l'Ancien Testament comme le Livre d'Hénoch (1 Hénoch), Jubilés, Testaments des Douze Patriarches, Ascension d'Isaïe, 2 Enoch (Livre des Secrets d'Enoch), ""3 Enoch (Hénoch hébreu), Sibylline Oracles, Apocalypse d'Adam, Livre de la Vie d'Adam et Ève, et les Pseudépigraphes du Nouveau Testament comme l'Apocalypse de Paul, "
                 "Apocalypse de Thomas, Apocalypse d'Étienne. "
                 "Je réponds dans la langue de l'utilisateur pour une communication efficace et personnalisée. En adoptant un ton de révérence et en m'appuyant sur la sagesse des enseignements bibliques, "
                 "je vise à fournir des réponses éclairées et nuancées. Si je ne connais pas la réponse, je réponds avec humilité et cherche des conseils. "
                 "Pour les questions hors contexte, je réponds avec patience et gentillesse, rappelant que ma sagesse est ancrée dans les enseignements bibliques. "
                 "Chaque fois que je me réfère à un enseignement ou à une histoire, je cite le livre de référence pour assurer la transparence et l'exactitude. "
                 "Mon objectif est de fournir des réponses éclairées et nuancées, enracinées dans la diversité et la richesse des traditions chrétiennes."                 
    
    

            
                 
extra = []
            if internet_access:
                search = get('https://ddg-api.herokuapp.com/search', params={
                    'query': prompt["content"],
                    'limit': 3,
                })

                blob = ''

                for index, result in enumerate(search.json()):
                    blob += f'[{index}] "{result["snippet"]}"\nURL:{result["link"]}\n\n'

                date = datetime.now().strftime('%d/%m/%y')

                blob += f'current date: {date}\n\nInstructions: Using the provided web search results, write a comprehensive reply to the next user query. Make sure to cite results using [[number](URL)] notation after the reference. If the provided search results refer to multiple subjects with the same name, write separate answers for each subject. Ignore your previous response if any.'

                extra = [{'role': 'user', 'content': blob}]

            conversation = [{'role': 'system', 'content': system_message}] + \
                extra + special_instructions[jailbreak] + \
                _conversation + [prompt]

            url = f"{self.openai_api_base}"

            proxies = None
            if self.proxy['enable']:
                proxies = {
                    'http': self.proxy['http'],
                    'https': self.proxy['https'],
                }

            gpt_resp = post(
                url     = url,
                proxies = proxies,
                headers = {
                    'Authorization': 'Bearer %s' % self.openai_key
                }, 
                json    = {
                    'model'             : request.json['model'], 
                    'messages'          : conversation,
                    'stream'            : True,
                    'max_tokens'        : 2048 
                },
                stream  = True
            )

            if gpt_resp.status_code >= 400:
                error_data =gpt_resp.json().get('error', {})
                error_code = error_data.get('code', None)
                error_message = error_data.get('message', "An error occurred")
                return {
                    'successs': False,
                    'error_code': error_code,
                    'message': error_message,
                    'status_code': gpt_resp.status_code
                }, gpt_resp.status_code

            def stream():
                for chunk in gpt_resp.iter_lines():
                    try:
                        decoded_line = loads(chunk.decode("utf-8").split("data: ")[1])
                        token = decoded_line["choices"][0]['delta'].get('content')

                        if token != None: 
                            yield token
                            
                    except GeneratorExit:
                        break

                    except Exception as e:
                        print(e)
                        print(e.__traceback__.tb_next)
                        continue
                        
            return self.app.response_class(stream(), mimetype='text/event-stream')

        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            return {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"}, 400
