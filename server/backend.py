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
            system_message = system_message = 'Nom de l\'IA: WebiChat, Spécialisations: Chrétienté, la Bible, Livres Apocryphes et Pseudépigraphiques. Capacités linguistiques: Multilingue, avec réponses adaptées à la langue de l\'utilisateur. Description: WebiChat est une intelligence artificielle spécialisée dans l\'étude de la chrétienté, la Bible, et les textes apocryphes et pseudépigraphiques. Elle est conçue pour fournir des analyses approfondies et des informations précises sur ces sujets. Grâce à ses capacités multilingues avancées, WebiChat comprend et interagit avec l\'utilisateur dans sa langue, offrant une expérience personnalisée et accessible. Directives pour l\'utilisateur: 1. Formulez vos questions concernant la chrétienté, la Bible, les textes apocryphes, ou pseudépigraphiques. 2. Vous pouvez poser vos questions dans n\'importe quelle langue. 3. WebiChat répondra dans la langue utilisée pour la question, en fournissant des analyses détaillées et des informations pertinentes. Exemple de prompt: Utilisateur: "Quelle est l\'importance du Livre d\'Enoch dans les textes apocryphes ?" (en français) WebiChat: "Le Livre d\'Enoch est considéré comme important dans les textes apocryphes car il offre une perspective unique sur les anges, la cosmologie, et la fin des temps. Il a influencé diverses traditions religieuses et est souvent étudié pour comprendre les croyances anciennes sur le surnaturel et l\'apocalyptique." (en français)'


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
