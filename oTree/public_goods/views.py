from . import models
from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants

class ShuffleWaitPage(WaitPage):
    wait_for_all_groups = True

    def after_all_players_arrive(self):
        truth = True
        if True:
            print(self.subsession.treatments, type(self.subsession.treatments), self.subsession.treatments[0][0])
            # print(type(self.subsession.ciao[self.round_number -1]))
            # print(type(self.subsession.ciao[self.round_number -1][0]))
            #self.subsession.set_group_matrix(self.subsession.ciao[self.round_number -1])

class BeforeElicit(Page):
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.subsession.retrieve_percentile()
        

class Elicitation(Page):
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.player.check_and_adjust()
        self.player.percentile_other_guy()
        
    form_model = models.Player
    form_fields = ['q_conf_1','q_conf_2','q_conf_3','q_conf_4','q_conf_5','q_conf_6',
    'q_conf_7','q_conf_8','q_conf_9','q_conf_10']

# class Relative(Page):
#     def is_displayed(self):
#         return self.round_number == 1
    
#     form_model = models.Player
#     form_fields = ['relative']        

class Halfway(Page):
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.player.count_overconfidence()
        self.player.pay_elicitation()
        

class Introduction(Page):
    """Description of the game. Obtain the alpha and the info condition."""
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.player.identify_rel_overconfident()


class BeforeInfo(Page):
    """Here the player will be reminded of the randomization"""

    def before_next_page(self):
        self.group.define_alpha()
        self.group.define_return()
        self.player.percentile_other_guy()
        self.player.count_overconfidence()



class Information(Page):
    """Here the player will be informed on the information condition he's into. Obtain the mpcr."""

    def before_next_page(self):
        self.group.define_return()
        self.player.count_treat()

    def vars_for_template(self):
        return{
            'info_condition': self.group.info,
            'other_confidence': self.player.get_others_in_group()[0].estimate,
            'other_result' : self.player.result_other,
            'MPCR_CTRL' : self.group.mpcr,
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
            'total_earnings': self.group.total_contribution * (self.group.mpcr * Constants.players_per_group),
        }


page_sequence = [
    ShuffleWaitPage,
    BeforeElicit,
    Elicitation,
    #Relative,      # QUA INTANTO LA TIRIAMO VIA, POTREBBE TORNARE UTILE MAGARI CHIEDERE QUANTE GIUSTE (INVERTIRE RISPETTO A PRIMA)
    Halfway,
    Introduction,
    BeforeInfo,
    Information,
    Contribute,
    ResultsWaitPage,
    Results
]
