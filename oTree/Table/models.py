import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
import itertools
import numpy as np

author = 'Pietro+Fredi+Eren'

doc = """
Smileys
"""


class Constants(BaseConstants):
    name_in_url = 'Table2'
    players_per_group = None
    num_rounds = 21
    lst = list(itertools.product([0, 1], repeat=8))
    likertscale = [('1', ''), ('2', ''), ('3', ''), ('4', ''), ('5', ''), ('6', ''), ('7', '')]
    
class Subsession(BaseSubsession):
    def before_session_starts(self):
        """The following defines one color for the player, which is the cost of clicks treatment.
        Moreover one round for the payment is selected"""
        if self.round_number == 1:
            pool = ['red','blue']*12
            for p in self.get_players():
                p.participant.vars['color'] = pool[-1]
                del pool[-1]
            paying_round_1 = random.randint(2, 11)
            paying_round_2 = random.randint(12, 21)
            self.session.vars['paying_round_1'] = paying_round_1
            self.session.vars['paying_round_2'] = paying_round_2


class Group(BaseGroup):
    pass

class Player(BasePlayer):
    tempo = models.IntegerField()      
    clicchi = models.IntegerField()    
    clicchinuovi = models.IntegerField()
    distanza = models.IntegerField()
    arr_distanza = models.TextField()
    colors = models.TextField()
    cost_of_clicks = models.FloatField()

    lst_for_template = models.TextField()
    lst_strings = models.TextField()
    selec_for_template = models.TextField()
    filt_for_template = models.TextField()
    price = models.TextField()
    fake_payoff = models.CurrencyField()

    money_kept = models.BooleanField()
    etichetta = models.CharField()

    filters_applied = models.PositiveIntegerField(      
        choices=[0, 1, 2, 3, 4, 5, 6, 7, 8],            
        widget=widgets.RadioSelectHorizontal()
    )
    
    def labeling(self):
        self.etichetta = self.participant.label

    def set_colors(self):
        """Here we set the color, i.e. the treatment, for the single player."""
        colors = self.participant.vars['color']
        return colors

    def create_list(self):
        """The method returns a list of strings, in order to make it readable by the HTML template. The list created in the Constant class contains all
        possible combinations of zeros and ones forming an 8-digit number."""
        lst_lists = [list(elem) for elem in Constants.lst]  # the 0/1 are converted into a list, because lists are immutable and
        lst_strings = []                                    # I couldn't have done all the join/appending work i do afterwards. lst_strings
        for i in range(0, len(lst_lists)):                  # is iniciated and the objective of the following loop is to create a list
            lst_string = ''.join(
                str(e) for e in lst_lists[i])               # of 0/1 strings, all the elements of each list is joined and they are
            lst_strings.append(lst_string)                  # then appended to the empty lst_strings[].
        return lst_strings

    def lets_filter(self, lst_strings): 
        """This method selects a string from the pool, then he creates a dictionary with the distance of each string from the selected one.
        Moreover 256 strings are drew (with replacement) and they are going to be the one shown in the HTML template. Outputs then are
        the list of strings, the dictionary and the selected emoji"""
        selec_string = random.choice(lst_strings)       # one value is extracted
        selec_for_template = [selec_string]
        selec = [int(i) for i in selec_string]          #created a list starting from selec_string
        distance = []                                   # Iniciated empty distance list:
        for attempt in Constants.lst:                   # for each tuple in the list...
            diff = 0                                    # diff(erence) is defined and starting from zero
            for i in range(0,8):          
                if attempt[i] == selec[i]:
                    diff += 0                           # if the element is the same of pref, then add +0,
                else:
                    diff += 1                           # otherwise add a 1, then iterate and get a value, which is
            distance.append(diff)                       # summed to the value diff
        d = dict()                                      # started a dictionary
        for i in range(0, len(lst_strings)):
            if distance[i] not in d:                    # if a certain distance (say 5) is not already in the dictionary,
                d[distance[i]] = [lst_strings[i]]       # then create a new key and the corresponding value is added
            else:
                d[distance[i]].append(lst_strings[i])   # otherwise append it to the right key
        lst_for_template_provv = [d[x] for x in range(0, 8 - int(self.filters_applied) + 1)]          # now using the filters explicited in the template
        lst_for_template_prov = list(itertools.chain(*lst_for_template_provv))                        # extracts all the elements that satisfy the requirements
        lst_for_template = np.random.choice(lst_for_template_prov, size=256, replace= True).tolist()  # and make a random draw with replacement
        filt_for_template = [d[x] for x in range(0, 9)]                                               # to export the dictionary in the template
        return str(lst_for_template), filt_for_template, selec_for_template

    def set_price(self):
        """The method sets the price of the filters [3,3,3,3,4,5,6,7,8]"""
        if self.round_number == 1:
                price = 4
        if self.round_number > 1:
            if self.filters_applied < 4:
                price = 3
            if self.filters_applied > 3:
                price = self.filters_applied
        return price

    def define_cost(self):
        """The method defines the costs of the filters depending on the treatment"""
        if self.round_number < 12 and self.participant.vars['color'] == 'blue':
            cost_of_clicks = 0.05
        elif self.round_number > 11 and self.participant.vars['color'] == 'blue':
            cost_of_clicks = 0.20
        elif self.round_number > 11 and self.participant.vars['color'] == 'red':
            cost_of_clicks = 0.05
        else:
            cost_of_clicks = 0.20
        return cost_of_clicks

    def set_payoffs(self, cost_of_clicks, price):
        """Calculates the payoffs. We have a 'fake payoff' which is the one shown to the player and a 'real' one which is used to calculate the final payoff"""
        clicks = self.clicchinuovi
        distance = self.distanza
        if self.money_kept:
            fake_payoff = (8 - int(distance)) - int(price) - int(clicks)*cost_of_clicks
            if self.round_number < 12:
                if (self.round_number == self.session.vars ['paying_round_1']):
                    payoff = (8 - int(distance)) -  int(price) - int(clicks)*cost_of_clicks
                else:
                    payoff = 0
            if self.round_number > 11:
                if (self.round_number == self.session.vars ['paying_round_2']):
                    payoff = (8 - int(distance)) -  int(price) - int(clicks)*cost_of_clicks
                else:
                    payoff = 0
        else:
            fake_payoff = 0 - int(clicks)*cost_of_clicks
            if self.round_number < 12:
                if (self.round_number == self.session.vars ['paying_round_1']):
                    payoff = 0 - int(clicks)*cost_of_clicks
                else:
                    payoff = 0
            if self.round_number > 11:
                if (self.round_number == self.session.vars ['paying_round_2']):
                    payoff = 0 - int(clicks)*cost_of_clicks
                else:
                    payoff = 0
        return payoff, fake_payoff

    #Define here the control questions    
    control_question1 = models.IntegerField()
    control_question2 = models.IntegerField()
    control_question3 = models.FloatField()
    control_question4 = models.FloatField()
    control_question5 = models.IntegerField()
    

    q_risk1 = models.CharField(initial=None,
                                choices=Constants.likertscale,
                                verbose_name='Sind Sie im Allgemeinen ein risikobereiter Mensch oder versuchen Sie, Risiken zu vermeiden?',
                                doc="""Sind Sie im Allgemeinen ein risikobereiter Mensch oder versuchen Sie, Risiken zu vermeiden?""",
                                widget=widgets.RadioSelectHorizontal())

    q_risk2 = models.CharField(initial=None,
                                choices=Constants.likertscale,
                                verbose_name='In unsicheren Situationen und Zeiten, gehe ich davon aus, dass schon alles gut gehen wird.',
                                doc="""In unsicheren Situationen und Zeiten, gehe ich davon aus, dass schon alles gut gehen wird.""",
                                widget=widgets.RadioSelectHorizontal())

    q_motive1 = models.CharField(initial=None,
                                choices=Constants.likertscale,
                                verbose_name='Ich habe im Experiment versucht möglichst ähnliche Gesichter zu finden, unabhängig vom Preis',
                                doc="""In unsicheren Situationen und Zeiten, gehe ich davon aus, dass schon alles gut gehen wird.""",
                                widget=widgets.RadioSelectHorizontal())

    q_motive2 = models.CharField(initial=None,
                                choices=Constants.likertscale,
                                verbose_name='Ich habe im Experiment nur auf den angezeigten Wert und nicht auf die Gesichter geschaut.',
                                widget=widgets.RadioSelectHorizontal())

    q_motive3 = models.CharField(initial=None,
                                choices=Constants.likertscale,
                                verbose_name='Es lohnt  im Experiment, viele Filter zu setzen.',
                                widget=widgets.RadioSelectHorizontal())

    q_age = models.PositiveIntegerField(verbose_name='Wie alt sind Sie?',
                                        choices=range(13, 125),
                                        initial=None)
    q_gender = models.CharField(initial=None,
                                choices=['männlich', 'weiblich'],
                                verbose_name='Sind Sie...',
                                widget=widgets.RadioSelect())
    q_shopping = models.CharField(initial=None,
                                choices=['Mehr als dreimal in der Woche', 'Ein bis dreimal in der Woche', 'Mindestens einmal im Monat', 'Einmal im Jahr oder seltener' ],
                                verbose_name='Wie oft kaufen Sie auf Online-Portalen ein?',
                                widget=widgets.RadioSelect())
    q_amazon = models.CharField(initial=None,
                                  choices=['Ja', 'Nein'],
                                  verbose_name='Haben Sie einen Amazon account oder einen Account bei einer ähnlichen Website?',
                                  widget=widgets.RadioSelect())
    q_internet = models.CharField(initial=None,
                                choices=['Ja', 'Ich habe davon gehört', 'Nein'],
                                verbose_name='Kennen Sie die Konzepte Machine Learning und User Profiling?',
                                widget=widgets.RadioSelect())
    comments = models.TextField(initial=None,
                                verbose_name='Haben Sie noch zusätzliche Kommentare zu dem Experiment?',
                                blank=True
                                )

