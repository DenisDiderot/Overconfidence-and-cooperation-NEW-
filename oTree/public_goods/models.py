from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
import csv
import itertools
from .treatment_matrix import get_treatment_matrix

doc = """
This is a one-period public goods game with 3 players.
"""


class Constants(BaseConstants):
    name_in_url = 'public_goods'
    players_per_group = 4
    num_rounds = 12

    instructions_template = 'public_goods/Instructions.html'
    options = [('A',''), ('B', '')] 
    # """Amount allocated to each player"""
    endowment = c(100)
    
    treatments = ['Bel', 'Act', 'Ctrl', 'No',]

class Subsession(BaseSubsession):
    final = models.CharField()
    treatments = models.CharField()
    matrix = models.CharField()
    individual_alpha = models.FloatField()

    def before_session_starts(self):
        
        for p in self.get_players():
            if 'treatment'  in self.session.config:
                p.color = self.session.config['treatment']
            else:
                p.color = random.choice(['blue', 'red'])

        for p in self.get_players():
            if p.color == 'red':
                self.individual_alpha = 0.5                                                      
            elif p.color == 'blue':
                self.individual_alpha = 0.8
    
        if not self.session.vars.get('treatment_matrix'):
            self.session.vars['treatment_matrix'] = get_treatment_matrix()
            print(self.session.vars['treatment_matrix'])
        for p in self.get_players():
            p.treat = self.session.vars['treatment_matrix'][p.id_in_subsession-1][p.round_number - 1]
        new_matrix = []
        for i in Constants.treatments:
            toadd = [p for p in self.get_players() if p.treat == i]
            new_matrix.append(toadd)
        self.set_group_matrix(new_matrix)        

    def retrieve_percentile(self):
        for p in self.get_players():
            p.percentile = p.participant.vars['perc']


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()
    alpha = models.FloatField()
    info = models.CharField()
    mpcr = models.FloatField()
    
    def define_alpha(self):
        self.alpha = sum(p.percentile for p in self.get_players())
        
    def define_return(self):
        if self.info == "Ctrl":
            self.mpcr = self.subsession.individual_alpha                            ### Check it works
        else:
            self.mpcr = self.subsession.individual_alpha*(self.alpha)               ### Check it works

    def set_payoffs(self):
        self.total_contribution = sum([p.contribution for p in self.get_players()])
        self.individual_share = self.total_contribution * self.mpcr       
        for p in self.get_players():
            p.payoff = (Constants.endowment - p.contribution) + self.individual_share


class Player(BasePlayer):
    percentile = models.FloatField()
    estimate = models.FloatField()
    contribution = models.CurrencyField(
        min=0, max=Constants.endowment,
        doc="""The amount contributed by the player""",
    )
    guy = models.CharField()
    relative = models.FloatField(
        min=0, max=100, doc="""Estimate of own ranking""")
    guy_relative = models.CharField()
    payoff_elicitation = models.CurrencyField()
    result_other = models.FloatField()
    rnd = models.PositiveIntegerField()
    info_player = models.CharField()
    treat = models.CharField()
    mate = models.CharField()

    def count_overconfidence(self):                                                         #da spostare
        d = [self.q_conf_1, self.q_conf_2, self.q_conf_3, self.q_conf_4, self.q_conf_5, 
        self.q_conf_6, self.q_conf_7, self.q_conf_8, self.q_conf_9, self.q_conf_10]
        self.estimate = 0
        for i in range(0,10):
            if d[i] == 'A':
                self.estimate += 0.10

    def meet_friend(self):
        """Here define the group mate"""
        if self.round_number in [1,4,7,10]:    
            if self.id_in_group in [1,2]:
                self.mate = print(self.id_in_group, self.get_others_in_group()[0].id_in_group)
            elif self.id_in_group in [3,4]:
                self.mate = print(self.id_in_group, self.get_others_in_group()[2].id_in_group)
        if self.round_number in [2,5,8,11]:
            if self.id_in_group == 1:
                self.mate = print(self.id_in_group, self.get_others_in_group()[1].id_in_group)
            elif self.id_in_group == 2:
                self.mate = print(self.id_in_group, self.get_others_in_group()[2].id_in_group)
            elif self.id_in_group == 3:
                self.mate = print(self.id_in_group, self.get_others_in_group()[0].id_in_group)
            elif self.id_in_group == 4:
                self.mate = print(self.id_in_group, self.get_others_in_group()[1].id_in_group)
        if self.round_number in [3,6,9,12]:
            if self.id_in_group == 1:
                self.mate = print(self.id_in_group, self.get_others_in_group()[2].id_in_group)
            elif self.id_in_group == 2:
                self.mate = print(self.id_in_group, self.get_others_in_group()[1].id_in_group)
            elif self.id_in_group == 3:
                self.mate = print(self.id_in_group, self.get_others_in_group()[1].id_in_group)
            elif self.id_in_group == 4:
                self.mate = print(self.id_in_group, self.get_others_in_group()[0].id_in_group)


    def percentile_other_guy(self):
        self.result_other = print(self.id_in_group, self.get_others_in_group()[0].percentile)

    def identify_rel_overconfident(self):                                                    #da spostare
        if self.estimate > self.percentile:
            self.guy_relative = "Overconfident"
        elif self.estimate == self.percentile:
            self.guy_relative = "On spot"
        elif self.estimate < self.percentile:
            self.guy_relative = "Underconfident"
        else:
            self.guy_relative = "Check manually"
    
    def check_and_adjust(self):                                                                 # da spostare
        for i in range(1,11):
            if getattr(self, "q_conf_{0}".format(i)) == 'B':
                for j in range(i, 11):
                    setattr(self, "q_conf_{0}".format(j), 'B')
        
    def pay_elicitation(self):
        self.rnd = random.randint(1,10)
        if getattr(self, "q_conf_{0}".format(self.rnd)) == 'A':
            pool = [i for i in range(1,11)]
            chosen = random.choice(pool)
            if chosen > self.rnd:
                self.payoff_elicitation = 0
            else:
                self.payoff_elicitation = 10                        #PAYOFF TO BE DECIDED
        elif getattr(self, "q_conf_{0}".format(self.rnd)) == 'B':
            if self.result_other > self.percentile:
                self.payoff_elicitation = 0
            elif self.result_other < self.percentile:
                self.payoff_elicitation = 10
            else:
                self.payoff_elicitation = random.choice([0,10])



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
 


    
