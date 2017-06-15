from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from .gto_timeout_page import GTOPage
import time

class Beginning(Page):
    def is_displayed(self):
        return self.round_number == 1

    
class Question(GTOPage):
    form_model = models.Player
    form_fields = ['submitted_answer']
    timer_text = 'Time left to complete this section:'
    general_timeout = True


    def gto_vars_for_template(self):
        roundd = self.round_number
        
        return{
            'round' : roundd,
            'image_path1' : 'quiz/{}.jpg'.format(self.round_number),
            'image_path2' : 'quiz/{}R.jpg'.format(self.round_number),
        }

    def submitted_answer_choices(self):
        qd = self.player.current_question()
        return [
            qd['choice1'],
            qd['choice2'],
            qd['choice3'],
            qd['choice4'],
            qd['choice5'],
            qd['choice6']
        ]

    def before_next_page(self):
        self.player.check_correct()
        self.player.count_correct()
        

class BeginWaitPage(WaitPage):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    wait_for_all_groups = True
    template_name = 'quiz/BeginWaitPage.html'

class AfterWait(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def before_next_page(self):
        self.subsession.check_none()
        self.player.cum_count = sum(p.count for p in self.player.in_all_rounds())


class Results(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        player_in_all_rounds = self.player.in_all_rounds()
        summ = sum([p.count for p in player_in_all_rounds])
        return {
            'player_in_all_rounds': player_in_all_rounds,
            'questions_correct': summ
        }  

    def before_next_page(self):
        self.subsession.get_ranking()               #LASCIA IN QUIZ
        self.subsession.assign_percentile()         #LASCIA IN QUIZ
        self.subsession.player_perc()               #LASCIA IN QUIZ
        

page_sequence = [
    Beginning,
    Question,
    BeginWaitPage,
    AfterWait,
    Results,
]
