from . import models
from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants


class Elicitation(Page):

    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        # self.player.check_and_adjust()
        self.player.percentile_other_guy()
        self.group.define_alpha()

    form_model = models.Player
    form_fields = ['q_conf_1', 'q_conf_2', 'q_conf_3', 'q_conf_4', 'q_conf_5', 'q_conf_6',
                   'q_conf_7', 'q_conf_8', 'q_conf_9', 'q_conf_10']


class HalfWaitPage(WaitPage):
    wait_for_all_groups = True
    body_text = "Waiting for other participants to fill in their table. Afterwards you are going to move on into part 2. Instructions follow."

    def is_displayed(self):
        return self.round_number == 1


class WithinWaitPage(WaitPage):
    #wait_for_all_groups = True
    body_text = "As soon as your future match will have contributed in the previous round you can move on."

    def is_displayed(self):
        return self.round_number > 1


class Introduction(Page):
    """Description of the game. Obtain the alpha and the info condition."""

    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.group.define_alpha()
        for p in self.group.get_players():
            p.count_overconfidence()
            p.pay_elicitation()


class Control(Page):

    def is_displayed(self):
        return self.round_number == 1

    form_model = models.Player
    form_fields = ['control1', 'control2', 'control3', 'control4', 'control5']


class BeforeInfo(Page):
    """Here the player will be reminded of the randomization"""

    def before_next_page(self):
        if self.round_number == 1:
            self.player.identify_rel_overconfident()

        self.player.percentile_other_guy()
        self.group.define_alpha()

class Information(Page):
    """Here the player will be informed on the information condition he's into. Obtain the mpcr."""

    def vars_for_template(self):
        mate = self.player.meet_friend()
        # self.player.percentile_other_guy()

        return{
            'info_condition': self.player.treat,
            'other_confidence': mate.in_round(1).estimate * 100,
            'other_result': self.player.result_other * 10,
            'mpcr': self.player.alpha,
        }

class Contribute(Page):
    """Player will be informed about mpcr and decide contribution."""

    form_model = models.Player
    form_fields = ['contribution']

    timeout_submission = {'contribution': c(Constants.endowment / 2)}

    def vars_for_template(self):

        return{
            'mpcr': self.player.alpha,
        }


class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.pay_public()

    body_text = "Waiting for other participants to contribute."

class Expectations(Page):
    form_model = models.Player
    form_fields = ['expected_contribution']

    def before_next_page(self):
        if self.round_number == Constants.num_rounds:
            self.group.set_payoffs()  
        else:
            pass

class EndResults(Page):

    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        mate = self.player.in_round(self.player.rnd_round).meet_friend()
        return {
            'random_choice': self.player.in_round(1).rnd,
            'choice': self.player.in_round(1).choice,
            'random_public': self.player.rnd_round,
            'payoff_elicit': self.player.in_round(1).payoff_elicitation,
            'payoff_public': self.player.in_round(self.player.rnd_round).payoff_public,
            'your_contribution': self.player.in_round(self.player.rnd_round).contribution,
            'his_contribution': mate.contribution,
            'total': self.player.in_round(self.player.rnd_round).contribution + mate.contribution,
            'individual_share': self.player.in_round(self.player.rnd_round).individual_share,
            'alpha': self.player.in_round(self.player.rnd_round).alpha,
            'final': self.participant.payoff_plus_participation_fee()
        }

class Demographics(Page):

    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    form_model = models.Player
    form_fields = ['q_age', 'q_gender', 'q_risk1', 'q_risk2', 'comments', 'q_social1', 'q_social2', 'q_social3', 'q_social4', 'q_social5',
                   'q_social6', 'q_social7', 'q_social8', 'q_social9', 'q_social10', 'q_social11', 'q_social12', 'q_social13', 'q_social14']


class EndVince(Page):

    def is_displayed(self):
        return self.round_number == Constants.num_rounds

page_sequence = [
    Elicitation,
    HalfWaitPage,
    WithinWaitPage,
    Introduction,
    Control,
    BeforeInfo,
    Information,
    Contribute,
    ResultsWaitPage,
    Expectations,
    EndResults,
    Demographics,
    EndVince
]
