from otree.api import (
    Currency as c, currency_range, SubmissionMustFail, Submission
)
from . import views
from ._builtin import Bot
from .models import Constants

import random

class PlayerBot(Bot):

    cases = ['basic', 'min', 'max']

    def play_round(self):
        case = self.case
        yield (views.BeforeElicit)
        yield (views.Elicitation, {'q_conf_1': 'A', 'q_conf_2': 'A', 'q_conf_3': 'A', 'q_conf_4': random.choice(['A','B']), 'q_conf_5': random.choice(['A','B']),
            'q_conf_6': random.choice(['A','B']), 'q_conf_7': random.choice(['A','B']), 'q_conf_8': random.choice(['A','B']), 'q_conf_9': random.choice(['A','B']),
            'q_conf_10': random.choice(['A','B'])})
        yield (views.HalfWaitPage)
        yield (views.Introduction)

        if case == 'basic':
            if self.player.id_in_group == 1:
                for invalid_contribution in [-1, 101]:
                    yield SubmissionMustFail(views.Contribute, {
                        'contribution': invalid_contribution})

        contribution = {
            'min': 0,
            'max': 100,
            'basic': 50,
        }[case]

        yield (views.BeforeInfo)
        yield (views.Information)
        yield (views.Contribute, {"contribution": contribution})
        yield (views.ResultsWaitPage)
        yield (views.Expectations, {'expected_contribution': 100, 'expected_ability': 0.5})
        yield (views.Results)
        yield (views.EndResults)
        yield (views.EndVince)

        # if self.player.id_in_group == 1:

        #     if case == 'min':
        #         expected_payoff = 100
        #     elif case == 'max':
        #         expected_payoff = 200
        #     else:
        #         expected_payoff = 150
        #     assert self.player.payoff == expected_payoff
