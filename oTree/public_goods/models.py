from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
import csv
import itertools

doc = """
This is a one-period public goods game with 3 players.
"""


class Constants(BaseConstants):
    name_in_url = 'public_goods'
    players_per_group = 2
    num_rounds = 12

    instructions_template = 'public_goods/Instructions.html'
    options = [('A', ''), ('B', '')]
    # """Amount allocated to each player"""
    endowment = c(100)

    #treatments = ['Bel', 'Act', 'Ctrl', 'No',]


class Subsession(BaseSubsession):
    standard_alpha = models.FloatField()
    treatment_all = models.CharField()

    def before_session_starts(self):

        for p in self.get_players():
            if 'treatment' in self.session.config:
                p.color = self.session.config['treatment']
            else:
                p.color = random.choice(['blue', 'red'])

        for p in self.get_players():
            if p.color == 'red':
                self.standard_alpha = 0.5
            elif p.color == 'blue':
                self.standard_alpha = 0.8

        self.group_randomly(fixed_id_in_group = True)
        if self.round_number == 4:
            for group in self.get_groups():
                players = group.get_players()
                players.reverse()
                group.set_players(players)
        if self.round_number in [5,6,10,11,12]:
            self.group_like_round(4)
            self.group_randomly(fixed_id_in_group = True)
        if self.round_number in [2,3,7,8,9]:
            self.group_like_round(1)
            self.group_randomly(fixed_id_in_group = True)

        print(self.get_group_matrix())

        # if self.round_number < 3:
        #     self.treatment_all = "Trial"
        #     print(self.treatment_all)
        if self.round_number < 7:
            self.treatment_all = "Act"
            print(self.treatment_all)
        if self.round_number > 6:
            self.treatment_all = "Bel"
            print(self.treatment_all)

        for p in self.get_players():
            p.treat = self.treatment_all

    def retrieve_percentile(self):
        for p in self.get_players():
            p.percentile = p.participant.vars['perc']


class Group(BaseGroup):

    def pay_public(self):
        for p in self.get_players():
            #mate = p.meet_friend()
            p.total_contribution = p.contribution + \
                p.get_others_in_group()[0].contribution
            p.individual_share = p.total_contribution * p.mpcr
            p.payoff_public = (Constants.endowment -
                               p.contribution) + p.individual_share

    def set_payoffs(self):
        for p in self.get_players():
            p.rnd_round = random.randint(1, Constants.num_rounds)
            p.payoff = p.in_round(p.rnd_round).payoff_public + \
                p.in_round(1).payoff_elicitation

    def define_alpha(self):
        self.subsession.retrieve_percentile()
        for p in self.get_players():
            p.percentile_other_guy()
            p.alpha = self.get_player_by_id(1).percentile


class Player(BasePlayer):
    percentile = models.DecimalField(max_digits=5, decimal_places=4)
    estimate = models.DecimalField(max_digits=3, decimal_places=2)
    contribution = models.CurrencyField(
        min=0, max=Constants.endowment,
        doc="""The amount contributed by the player""",
    )
    # relative = models.FloatField(
    #     min=0, max=100, doc="""Estimate of own ranking""")
    guy_relative = models.CharField()
    payoff_elicitation = models.CurrencyField()
    payoff_public = models.CurrencyField()
    #payoff_points = models.CurrencyField()
    result_other = models.FloatField()
    rnd = models.PositiveIntegerField()
    rnd_round = models.PositiveIntegerField()
    treat = models.CharField()
    alpha = models.FloatField()
    mpcr = models.FloatField()
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()
    expected_contribution = models.CurrencyField(
        min=0, max=Constants.endowment,
        doc="""Expected contribution by mate""")
    choice = models.CharField()

    def count_overconfidence(self):
        d = [self.q_conf_1, self.q_conf_2, self.q_conf_3, self.q_conf_4, self.q_conf_5,
             self.q_conf_6, self.q_conf_7, self.q_conf_8, self.q_conf_9, self.q_conf_10]
        self.estimate = 0
        for i in range(0, 10):
            if d[i] == 'B':
                self.estimate += 0.10
        return d

    def meet_friend(self):
        mate = self.get_others_in_group()[0]
        return mate

    def percentile_other_guy(self):
        self.result_other = self.get_others_in_group()[0].percentile

    def define_return(self):
        self.group.define_alpha()
        self.mpcr = self.subsession.standard_alpha * (self.alpha)

    def identify_rel_overconfident(self):
        if self.estimate > self.percentile:
            self.guy_relative = "Overconfident"
        elif self.estimate == self.percentile:
            self.guy_relative = "On spot"
        elif self.estimate < self.percentile:
            self.guy_relative = "Underconfident"
        else:
            self.guy_relative = "Check manually"

    def check_and_adjust(self):
        for i in range(1, 11):
            if getattr(self, "q_conf_{0}".format(i)) == 'A':
                for j in range(i, 11):
                    setattr(self, "q_conf_{0}".format(j), 'A')

    def pay_elicitation(self):
        """This method intends to pay individuals for their elicitation of preference. At the moment 100 credits are assigned to the individual. Payoffs need to be decided"""
        self.rnd = random.randint(1, 10)
        if getattr(self, "q_conf_{0}".format(self.rnd)) == 'A':
            self.choice = "lottery"
            pool = [i for i in range(1, 11)]
            chosen = random.choice(pool)
            if chosen > self.rnd:
                self.payoff_elicitation = c(0)
            else:
                self.payoff_elicitation = c(100)
        elif getattr(self, "q_conf_{0}".format(self.rnd)) == 'B':
            self.choice = "comparison with a randomly drawn participant"
            if self.result_other > self.percentile:
                self.payoff_elicitation = c(0)
            elif self.result_other < self.percentile:
                self.payoff_elicitation = c(100)
            else:
                self.payoff_elicitation = random.choice([c(0), c(100)])

    q_conf_1 = models.CharField(
        initial=None, choices=Constants.options, widget=widgets.RadioSelectHorizontal(attrs={'onClick' : 'left_click(this.id)'}))
    q_conf_2 = models.CharField(
        initial=None, choices=Constants.options, widget=widgets.RadioSelectHorizontal(attrs={'onClick' : 'left_click(this.id)'}))
    q_conf_3 = models.CharField(
        initial=None, choices=Constants.options, widget=widgets.RadioSelectHorizontal(attrs={'onClick' : 'left_click(this.id)'}))
    q_conf_4 = models.CharField(
        initial=None, choices=Constants.options, widget=widgets.RadioSelectHorizontal(attrs={'onClick' : 'left_click(this.id)'}))
    q_conf_5 = models.CharField(
        initial=None, choices=Constants.options, widget=widgets.RadioSelectHorizontal(attrs={'onClick' : 'left_click(this.id)'}))
    q_conf_6 = models.CharField(
        initial=None, choices=Constants.options, widget=widgets.RadioSelectHorizontal(attrs={'onClick' : 'left_click(this.id)'}))
    q_conf_7 = models.CharField(
        initial=None, choices=Constants.options, widget=widgets.RadioSelectHorizontal(attrs={'onClick' : 'left_click(this.id)'}))
    q_conf_8 = models.CharField(
        initial=None, choices=Constants.options, widget=widgets.RadioSelectHorizontal(attrs={'onClick' : 'left_click(this.id)'}))
    q_conf_9 = models.CharField(
        initial=None, choices=Constants.options, widget=widgets.RadioSelectHorizontal(attrs={'onClick' : 'left_click(this.id)'}))
    q_conf_10 = models.CharField(
        initial=None, choices=Constants.options, widget=widgets.RadioSelectHorizontal(attrs={'onClick' : 'left_click(this.id)'}))
