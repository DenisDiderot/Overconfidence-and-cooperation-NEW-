"""I wanted to create different bots, with different features. We noticed in ou analysis with real players that people divide into two cathegories.
Some of them are Behavioral, in the sense that they behave more in the sense of our empirical prediction, others stick quite closely to the model."""

from otree.api import Currency as c, currency_range
from . import views
from ._builtin import Bot
from .models import Constants
import random

class BehavioralGuy:
    
    def filters(self):
        """He uses between 3 and 6 filters."""
        xlist = random.randint(3,6)
        return xlist

    def distance(self, lst):
        maxx = 8 - lst
        ylist =random.randint(0, maxx)
        return ylist

    def answers(self):
        """He thinks that following the payoff displayed is less important, while he gives quite high importance to the number of filters used."""
        mot2 = random.randint(2,4)
        mot3 = random.randint(4,7)
        return mot2, mot3
   
class ClassicGuy:                           #Here inherit second method at some point
    def filters(self):
        """He uses between 1 and 4 filters. (optimal following the standard model prediction should be 3!)"""
        xlist = random.randint(1,4)
        return xlist

    def distance(self, lst):
        maxx = 8 - lst
        ylist =random.randint(0, maxx)
        return ylist

    def answers(self):
        """He doesn't look at the smileys much and he realizes that filters can be costly."""
        mot2 = random.randint(5,7)
        mot3 = random.randint(2,5)
        return mot2, mot3

class PlayerBot(Bot):
    def play_round(self):
        if self.participant.id_in_session < 6:
            xlist = BehavioralGuy.filters(self)
            ylist = BehavioralGuy.distance(self, xlist)
            mot2 = BehavioralGuy.answers(self)[0]
            mot3 = BehavioralGuy.answers(self)[1]
            
        else:
            xlist = ClassicGuy.filters(self)
            ylist = ClassicGuy.distance(self, xlist)
            mot2 = ClassicGuy.answers(self)[0]
            mot3 = ClassicGuy.answers(self)[1]

        if self.player.round_number == 1:
            yield (views.Introduction)
            yield (views.Instructions)
            yield (views.ControlQuest, {'control_question1':8, 'control_question2':5, 
            	'control_question3':1.6, 'control_question4':-0.4, 'control_question5':2})
            yield (views.ControlAnsw)
            yield (views.Proberunde)
        if self.player.round_number == 12:
           yield (views.Halfway)
           yield (views.ChangeCosts)
        yield (views.Filters, {'filters_applied': xlist})
        yield (views.Table, {'tempo': 521, 'clicchi': 2, 'clicchinuovi': 1, 'distanza': ylist, 'arr_distanza': '6,7', 'money_kept': True })
        yield (views.Results)
        if self.player.round_number == Constants.num_rounds:
            yield (views.Demographics, {'q_age': 23, 'q_gender':'weiblich','q_shopping':'Ein bis dreimal in der Woche','q_amazon':'Ja',
                'q_internet':'Ja', 'q_risk1': 4, 'q_risk2': 4, 'q_motive1': 4, 'q_motive2': mot2,'q_motive3': mot3,'comments': ''})
            yield (views.FinalResult)
            
