from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
from decimal import *
getcontext()

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
    options = [('A',''), ('B', '')]                 #SPOSTA



class Subsession(BaseSubsession):
    def retrieve_percentile(self):
        for p in self.get_players():
            p.percentile = p.participant.vars['perc']
            p.cum_count = p.participant.vars['cumcount']


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
    percentile = models.CharField()
    estimate = models.CharField()
    contribution = models.CurrencyField(
        min=0, max=Constants.endowment,
        doc="""The amount contributed by the player""",
    )
    guy = models.CharField()
    relative = models.FloatField(
        min=0, max=100, doc="""Estimate of own ranking""")
    guy_relative = models.CharField()


    def count_overconfidence(self):                                                         #da spostare
        d = [self.q_conf_1, self.q_conf_2, self.q_conf_3, self.q_conf_4, self.q_conf_5]#, 
        #self.q_conf_6, self.q_conf_7, self.q_conf_8, self.q_conf_9, self.q_conf_10]
        self.estimate = 0
        for i in range(0,5):
            if d[i] == 'A':
                self.estimate += 0.20

    # def identify_overconfident(self):                                                       #da spostare e cambiare
    #     if self.estimate > self.cum_count:
    #         self.guy = "Overconfident"
    #     elif self.estimate == self.cum_count:
    #         self.guy = "On spot"
    #     else:
    #         self.guy = "Underconfident"

    def identify_rel_overconfident(self):                                                    #da spostare
        if Decimal(self.estimate) > Decimal(self.percentile):
            self.guy_relative = "Relative Overconfident"
        if Decimal(self.estimate) == Decimal(self.percentile):
            self.guy_relative = "Relative on spot"
        if Decimal(self.estimate) < Decimal(self.percentile):
            self.guy_relative = "Relative underconfident"
        else:
            self.guy_relative = "ERROR"
    
    # def something(self):                
    #     for i in range(1,6):
    #         setattr(self, "q_conf_{0}".format(i), models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal()))

    def check_and_adjust(self):                                                                 # da spostare
        for i in range(1,6):
            if getattr(self, "q_conf_{0}".format(i)) == 'B':
                for j in range(i, 6):
                    setattr(self, "q_conf_{0}".format(j), 'B')
       


    # da spostare -->
    q_conf_1 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_2 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_3 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_4 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_5 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_6 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_7 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_8 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_9 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_10 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
 


    
