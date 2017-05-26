from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random

doc = """
This is a one-period public goods game with 3 players.
"""


class Constants(BaseConstants):
    name_in_url = 'public_goods'
    players_per_group = 2
    num_rounds = 1

    instructions_template = 'public_goods/Instructions.html'

    # """Amount allocated to each player"""
    endowment = c(100)
    individual_return = 1                                               #To be substituted at some point with the actual alpha



class Subsession(BaseSubsession):
    def retrieve_percentile(self):
        for p in self.get_players():
            p.percentile = p.participant.vars['perc']
            p.estimate = p.participant.vars['estimate']
            p.relative = p.participant.vars['relative']


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()
    alpha = models.FloatField()

    def define_alpha(self):
        self.alpha = sum(p.percentile for p in self.get_players())

    def set_payoffs(self):
        self.total_contribution = sum([p.contribution for p in self.get_players()])
        self.individual_share = self.total_contribution * Constants.individual_return
        for p in self.get_players():
            p.payoff = (Constants.endowment - p.contribution) + self.individual_share


class Player(BasePlayer):
    percentile = models.FloatField()
    estimate = models.FloatField()
    relative = models.FloatField()
    contribution = models.CurrencyField(
        min=0, max=Constants.endowment,
        doc="""The amount contributed by the player""",
    )
    
