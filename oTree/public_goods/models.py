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
    players_per_group = 4
    num_rounds = 12

    instructions_template = 'public_goods/Instructions.html'
    options = [('A',''), ('B', '')] 
    # """Amount allocated to each player"""
    endowment = c(100)
    
    individual_alpha = 0.5                                                      #To be substituted at some point with the actual alpha
    treatments = [['Bel', 'Bel','Bel'],['Act', 'Act', 'Act'],['Ctrl', 'Ctrl', 'Ctrl'],['No', 'No', 'No']]


class Subsession(BaseSubsession):
    final = models.CharField()
    treatments = models.CharField()
    matrix = models.CharField()

    def before_session_starts(self):
        initial_data = list(itertools.permutations('abcd'))

        def by_letters(a, b):
            u = zip(a, b)
            for i, j in u:
                if i == j:
                    return True
            return False


        def filtered(what):
            x = [i for i in a if not by_letters(i, what)]
            return x


        def triple(str):
            return ''.join([c+c+c for c in str])

        result = None

        
        while result is None:
            try:
                matrices = []
                a = initial_data
                for i in range(4):
                    print('cycle:: ', i)
                    line1 = random.choice(a)
                    line2 = random.choice(filtered(line1))
                    s1 = set(filtered(line1))
                    s2 = set(filtered(line2))
                    sets = [s1, s2]
                    line3 = random.choice(list(set.intersection(*sets)))
                    s3 = set(filtered(line3))
                    sets = [s1, s2, s3]
                    line4 = random.choice(list(set.intersection(*sets)))
                    matrix1 = [line1, line2, line3, line4]
                    matrices.append(matrix1)
                    a = list(itertools.filterfalse(lambda x: x in matrix1, a))
                result = matrices                

            except:
                 pass
        self.final = [triple(j) for i in matrices for j in i]
        print(self.final)

        for p in self.get_players():
            if self.in_round(12).final is not None:
                i = p.id_in_subsession
                p.treat = self.final[i-1]
                for i in range(0, 12):
                    p_round = p.in_round(i+1)
                    p_round.info_player = p.treat[i]

        for i in range(1,13):
            self.in_round(i).matrix = [[],[],[],[]]
            for p in self.get_players():
                if p.in_round(i).info_player == 'a':
                    self.in_round(i).matrix[0].append(p)
                if p.in_round(i).info_player == 'b':
                    self.in_round(i).matrix[1].append(p)
                if p.in_round(i).info_player == 'c':
                    self.in_round(i).matrix[2].append(p)
                if p.in_round(i).info_player == 'd':
                    self.in_round(i).matrix[3].append(p)
        
            if (len(self.in_round(i).matrix[0]) == 4) and (len(self.in_round(i).matrix[1]) == 4) and (len(self.in_round(i).matrix[2]) == 4) and (len(self.in_round(i).matrix[3]) == 4):  
                self.in_round(i).treatments = self.in_round(i).matrix

                #self.in_round(i).set_group_matrix(self.in_round(i).matrix)
                #print(type(self.in_round(i).matrix[0][0]), len(self.in_round(i).matrix), len(self.get_group_matrix()), type(self.get_group_matrix()[0][0]))

                # print('ideal', type(self.in_round(i).ciao[0][0]))
                # print('matrix', self.in_round(i).get_group_matrix())
                # if self.in_round(i).ciao is not None:
                #     self.in_round(i).set_group_matrix(self.in_round(i).ciao)
                #     print(self.in_round(i).get_group_matrix())
        

    def retrieve_percentile(self):
        for p in self.get_players():
            p.percentile = p.participant.vars['perc']


class Group(BaseGroup):
    ciao = models.CharField()
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()
    alpha = models.FloatField()
    info = models.CharField()
    mpcr = models.FloatField()
    final = models.CharField()

    
    def define_alpha(self):
        self.alpha = sum(p.percentile for p in self.get_players())
        
    def define_return(self):
        if self.info == "Ctrl":
            self.mpcr = Constants.individual_alpha
        else:
            self.mpcr = Constants.individual_alpha*(self.alpha)

    def set_payoffs(self):
        self.total_contribution = sum([p.contribution for p in self.get_players()])
        self.individual_share = self.total_contribution * self.mpcr       ##### QUI BISOGNA AGGIUSTARE CON LA NUOVA DEFINIZIONE DI MPCR ######
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
    # ctrl_count = models.PositiveIntegerField(initial = 0)
    # no_count = models.PositiveIntegerField(initial = 0)
    # bel_count = models.PositiveIntegerField(initial = 0)
    # act_count = models.PositiveIntegerField(initial = 0)
    # ctrl_check = models.BooleanField(initial = False)
    # act_check = models.BooleanField(initial = False)
    # no_check = models.BooleanField(initial = False)
    # bel_check = models.BooleanField(initial = False)
    info_player = models.CharField()
    runs = models.CharField()
    treat = models.CharField()



    # def count_treat(self):
    #     ctrl_count = 0
    #     no_count = 0
    #     bel_count = 0
    #     act_count = 0
    #     for p in self.in_all_rounds():
    #         if p.info_player == "Ctrl":
    #             ctrl_count += 1
    #         elif p.info_player == "No":
    #             no_count += 1
    #         elif p.info_player == "Bel":
    #             bel_count += 1
    #         elif p.info_player == "Act":
    #             act_count += 1
    #         p.runs = dict()
    #         p.runs['Ctrl'] = ctrl_count
    #         p.runs['Bel'] = bel_count
    #         p.runs['No'] = no_count
    #         p.runs['Act'] = act_count


    # def can_go_on(self, activity):
    #     self.count_treat()
    #     print(self.id_in_subsession, self.runs[activity] < 3, activity, self.runs[activity])
    #     return self.runs[activity] < 3

    # def check_treat(self):
    #     for p in self.in_all_rounds():    
    #         if p.ctrl_count > 2:
    #             self.ctrl_check = True
    #         elif p.act_count > 2:
    #             self.act_check = True
    #         elif p.bel_count > 2:
    #             self.bel_check = True
    #         elif p.no_count > 2:
    #             self.no_check = True



    def count_overconfidence(self):                                                         #da spostare
        d = [self.q_conf_1, self.q_conf_2, self.q_conf_3, self.q_conf_4, self.q_conf_5, 
        self.q_conf_6, self.q_conf_7, self.q_conf_8, self.q_conf_9, self.q_conf_10]
        self.estimate = 0
        for i in range(0,10):
            if d[i] == 'A':
                self.estimate += 0.10


    # def identify_overconfident(self):                                                       #da spostare e cambiare
    #     if self.estimate > self.cum_count:
    #         self.guy = "Overconfident"
    #     elif self.estimate == self.cum_count:
    #         self.guy = "On spot"
    #     else:
    #         self.guy = "Underconfident"
    
    def percentile_other_guy(self):
        self.result_other = self.get_others_in_group()[0].percentile



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
 


    
