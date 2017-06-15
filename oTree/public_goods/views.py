from . import models
from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants


class Introduction(Page):
    """Description of the game. Obtain the alpha and the info condition."""
    def before_next_page(self):
        self.group.define_alpha()

class Information(Page):
    """Here the player will be informed on the information condition he's into. Obtain the mpcr."""

    def before_next_page(self):
        self.group.define_return()

    def vars_for_template(self):
        return{
            'info_condition': self.group.info,
        }

class Contribute(Page):
    """Player will be informed about mpcr and decide contribution."""

    form_model = models.Player
    form_fields = ['contribution']

    timeout_submission = {'contribution': c(Constants.endowment / 2)}

    def vars_for_template(self):
        return{
            'mpcr': self.group.mpcr,
        }

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


# class Relative(Page):
#     def is_displayed(self):
#         return self.round_number == 1
    
#     form_model = models.Player
#     form_fields = ['relative']        


class Halfway(Page):
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.player.identify_rel_overconfident()
        


page_sequence = [
    Before,
    Elicitation,
    #Relative,      # QUA INTANTO LA TIRIAMO VIA, POTREBBE TORNARE UTILE MAGARI CHIEDERE QUANTE GIUSTE (INVERTIRE RISPETTO A PRIMA)
    Halfway,
    Introduction,
    Information,
    Contribute,
    ResultsWaitPage,
    Results
]
