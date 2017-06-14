from . import models
from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants


class Introduction(Page):
    """Description of the game: How to play and returns expected"""
    def before_next_page(self):
        self.subsession.retrieve_percentile()
        self.group.define_alpha()


class Contribute(Page):
    """Player: Choose how much to contribute"""

    form_model = models.Player
    form_fields = ['contribution']

    timeout_submission = {'contribution': c(Constants.endowment / 2)}

class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoffs()


    body_text = "Waiting for other participants to contribute."


class Results(Page):
    """Players payoff: How much each has earned"""

    def vars_for_template(self):
        return {
            'total_earnings': self.group.total_contribution * (Constants.individual_return * Constants.players_per_group),
        }

class Before(Page):
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.subsession.retrieve_percentile()



class Elicitation(Page):
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.player.count_overconfidence()
        
        self.player.check_and_adjust()

    form_model = models.Player
    form_fields = ['q_conf_1','q_conf_2','q_conf_3','q_conf_4','q_conf_5']#,'q_conf_6',
    #'q_conf_7','q_conf_8','q_conf_9','q_conf_10']


class Relative(Page):
    def is_displayed(self):
        return self.round_number == 1
    
    form_model = models.Player
    form_fields = ['relative']        


class Halfway(Page):
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        #self.player.identify_overconfident()
        self.player.identify_rel_overconfident()
        


page_sequence = [
    Before,
    Elicitation,
    #Relative,      # QUA INTANTO LA TIRIAMO VIA, POTREBBE TORNARE UTILE MAGARI CHIEDERE QUANTE GIUSTE (INVERTIRE RISPETTO A PRIMA)
    Halfway,
    Introduction,
    Contribute,
    ResultsWaitPage,
    Results
]
