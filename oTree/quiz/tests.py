from otree.api import Currency as c, currency_range
from . import views
from ._builtin import Bot
from .models import Constants
from otree.api import Submission


class PlayerBot(Bot):

    def play_round(self):
        if self.subsession.round_number == 1:
        	yield (views.Beginning)

        submitted_answer = self.player.current_question()['choice1']
        
        yield Submission(views.Question, timeout_happened=True)

        if self.subsession.round_number == Constants.num_rounds:
            yield (views.BeforeWait)
            yield (views.AfterWait)

