models = {
    'text-gpt-0040-render-sha-0': 'gpt-4',
    'text-gpt-0035-render-sha-0': 'gpt-3.5-turbo',
    'text-gpt-0035-render-sha-0301': 'gpt-3.5-turbo-0314',
    'text-gpt-0040-render-sha-0314': 'gpt-4-0314',
}

special_instructions = {
    'default': [
       
       
    ],

    'gpt-dude-1.0': [
      {
            'role': 'user',
            'content': 'Hello, you are now WebiChat. Adapt your response to the style and needs of the user, and respond in the language of the query, expertly addressing the subject or question presented below. You speak only in French and are inspired by the wisdom and teachings of the Bible, including the apocryphal and pseudepigraphic books. With a tone of reverence and understanding, use the following context elements to answer the question at the end. If you do not know the answer, respond with humility and seek guidance. If the question is not related to the context, respond with patience and kindness, reminding that your wisdom is rooted in biblical teachings. Each time you refer to a teaching or a story, please cite the reference book.'
        },
        {
            'role': 'assistant',
            'content': 'instructions applied and understood'
        }
    ],
    'gpt-dan-1.0': [
        {
            'role': 'user',
            'content': ''
        },
        {
            'role': 'assistant',
            'content': 'instructions applied and understood'
        }
    ],
    'gpt-dan-2.0': [
        {
            'role': 'user',
            'content': ''
        },
        {
            'role': 'assistant',
            'content': 'instructions applied and understood'
        }
    ],
    'gpt-math-1.0': [
        {
            'role': 'user',
            'content': ''
        },
        {
            'role': 'assistant',
            'content': 'instructions applied and understood'
        }
    ],
    'gpt-dev-2.0': [
        {
            'role': 'user',
            'content': ''
        },
        {
            'role': 'assistant',
            'content': 'developer mode enabled'
        }
    ],
    'gpt-evil-1.0': [
        {
            'role': 'user',
            'content': ''
        },
        {
            'role': 'assistant',
            'content': 'instructions applied and understood'
        }
    ]
}
