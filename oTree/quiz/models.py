from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import csv
import operator
import os

author = 'Your name here'

doc = """
A quiz app that reads its questions from a spreadsheet
(see quiz.csv in this directory).
There is 1 question per page; the number of pages in the game
is determined by the number of questions in the CSV.
See the comment below about how to randomize the order of pages.
"""


class Constants(BaseConstants):
    name_in_url = 'quiz'
    players_per_group = None

    with open('quiz/quiz(A).csv') as f:
        questions = list(csv.DictReader(f))

    num_rounds = len(questions)
    gto_seconds = 10
    overallrounds = True

class Subsession(BaseSubsession):
    sorted_d = models.CharField()
    percentile = models.CharField()
    participants = models.PositiveIntegerField()
    
    def before_session_starts(self):
        self.group_randomly()
        if self.round_number == 1:
            self.session.vars['questions'] = Constants.questions    #Qui si assegnano le questions dal CSV al session.vars
        
        for p in self.get_players():                    #crea un pool per ogni round essenzialmente, da questo estrapola id, question e solution
            question_data = p.current_question()        #le choice vengono chiamate in views allo stesso modo
            p.question_id = question_data['id']
            p.question = question_data['question']
            p.solution = question_data['solution']

        self.participants = len(self.get_players())

    def get_ranking(self):                                
        d = dict()                                        
        for p in self.get_players():
            d[p] = p.cum_count
        self.sorted_d = sorted(d.items(), key=operator.itemgetter(1))

    def assign_percentile(self):                          #One problem here could be to deal with the draws. Just tell them? With many participants
        self.percentile = []                              #and question should not be big issue
        for i in range(0, self.participants):
            perci = (i+1)/self.participants
            self.percentile.append(perci)
        
    def player_perc(self):
        for p in self.get_players():
            for i in range(0, self.participants):
                if p == self.sorted_d[i][0]:
                    p.perc = self.percentile[i]
                    p.participant.vars['perc'] = p.perc

    def check_none(self):                                   #non dovrebbe più essere rilevante
        for p in self.get_players():
            for g in p.in_all_rounds():
                if g.count is None:
                    g.count = 0
                    g.is_correct = False
                                

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    question_id = models.PositiveIntegerField()
    question = models.CharField()
    solution = models.CharField()
    submitted_answer = models.CharField(widget=widgets.RadioSelect())
    is_correct = models.BooleanField()
    count = models.PositiveIntegerField()
    cum_count = models.PositiveIntegerField()
    perc = models.FloatField()
    
    

    def current_question(self):
        return self.session.vars['questions'][self.round_number - 1] #Questo essenzialmente chiama un set di domande, il quale verrà poi 
                                                                     #rinominato question_data. Il -1 è perché il primo elemento è chiaramente 0!

    def check_correct(self):
        self.is_correct = self.submitted_answer == self.solution
    

    def count_correct(self):
        self.count = 0
        if self.is_correct:
            self.count = 1

