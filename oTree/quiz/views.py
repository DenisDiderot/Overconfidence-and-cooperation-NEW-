from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants


class Question(Page):
    form_model = models.Player
    form_fields = ['submitted_answer']

    def submitted_answer_choices(self):
        qd = self.player.current_question()
        return [
            qd['choice1'],
            qd['choice2'],
            qd['choice3'],
            qd['choice4'],
        ]

    def before_next_page(self):
        self.player.check_correct()
        self.player.count_correct()
        self.player.cum_count = sum(p.count for p in self.player.in_all_rounds())
        #self.player.create_questions()

class BeginWaitPage(WaitPage):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    wait_for_all_groups = True
    template_name = 'quiz/BeginWaitPage.html'

class Results(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        player_in_all_rounds = self.player.in_all_rounds()
        summ = sum([p.is_correct for p in player_in_all_rounds])
        return {
            'player_in_all_rounds': player_in_all_rounds,
            'questions_correct': summ
        }

    def before_next_page(self):
        self.subsession.get_ranking()
        self.subsession.assign_percentile()
        self.subsession.player_perc()
        

class Halfway(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def before_next_page(self):
        self.player.identify_overconfident()


class Elicitation(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def before_next_page(self):
        self.player.count_overconfidence()

    form_model = models.Player
    form_fields = ['q_conf_1','q_conf_2','q_conf_3','q_conf_4','q_conf_5']#,'q_conf_6',
    #'q_conf_7','q_conf_8','q_conf_9','q_conf_10']

class Relative(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds
    
    form_model = models.Player
    form_fields = ['relative']        

    


page_sequence = [
    Question,
    BeginWaitPage,
    Results,
    Elicitation,
    Relative,
    Halfway,
]
